import traceback
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import UserMessage, AssistantMessage, TextContentItem, ImageContentItem, ImageUrl, CompletionsFinishReason
from melobot import Plugin, send_text
from melobot.log import get_logger
from melobot.protocols.onebot.v11 import on_start_match, on_message, on_command, on_notice, on_event, Adapter
from melobot.protocols.onebot.v11.handle import Args
from melobot.protocols.onebot.v11.utils import MsgChecker, LevelRole, MsgCheckerFactory, StartMatcher, ParseArgs, Parser
from melobot.protocols.onebot.v11.adapter.event import MessageEvent, PokeNotifyEvent, GroupMessageEvent, PrivateMessageEvent
from melobot.protocols.onebot.v11.adapter.segment import PokeSegment
from azure.core.credentials import AzureKeyCredential
from typing import Union
from .constants import *
from .config import Config 
from .util import *
from .models import MarshoContext
from .checkers import superuser_checker, PokeMarshoChecker
from .localstore import PluginStore
config = Config()
store = PluginStore(PLUGIN_NAME)
model_name = config.marshoai_default_model
context = MarshoContext()
token = config.marshoai_token
endpoint = config.marshoai_azure_endpoint
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token)
        )
logger = get_logger()

logger.info(f"Marsho 的插件数据存储于 : {str(store.get_plugin_data_dir())} 哦~🐾")
if config.marshoai_token == "":
    logger.warning("token 未配置。可能无法进行聊天。")
else:
    logger.info("token 已配置~！🐾")
logger.info("マルショは、高性能ですから!")

@on_command(checker=superuser_checker, cmd_start="/", cmd_sep=" ", targets="usermsg")
async def add_usermsg(event: MessageEvent, args: ParseArgs = Args()):
    context.append(UserMessage(content=" ".join(args.vals)).as_dict(), get_target_id(event), event.is_private)
    await send_text("已添加用户消息")

@on_command(checker=superuser_checker, cmd_start="/", cmd_sep=" ", targets="assistantmsg")
async def add_assistantmsg(event: MessageEvent, args: ParseArgs = Args()):
    context.append(AssistantMessage(content=" ".join(args.vals)).as_dict(), get_target_id(event), event.is_private)
    await send_text("已添加助手消息")

@on_command(checker=superuser_checker, cmd_start="/", cmd_sep=" ", targets="praises")
async def praises():
    await send_text(build_praises())

@on_command(checker=superuser_checker, cmd_start="/", cmd_sep=" ", targets="savecontext")
async def save_context(event: MessageEvent, args: ParseArgs = Args()):
    contexts = context.build(get_target_id(event), event.is_private)[1:]
    await save_context_to_json(" ".join(args.vals), contexts)
    await send_text("已保存上下文")

@on_command(checker=superuser_checker, cmd_start="/", cmd_sep=" ", targets="loadcontext")
async def load_context(event: MessageEvent, args: ParseArgs = Args()):
    context.set_context(await load_context_from_json(" ".join(args.vals)), get_target_id(event), event.is_private)
    await send_text("已加载并覆盖上下文")


@on_command(checker=superuser_checker, cmd_start="/", cmd_sep=" ", targets="changemodel")
async def changemodel(args: ParseArgs = Args()):
    global model_name
    model_name = args.vals[0]
    await send_text("已切换")

@on_command(checker=superuser_checker, cmd_start="/", cmd_sep=" ", targets="contexts")
async def contexts(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await send_text(str(context.build(get_target_id(event), event.is_private)[1:]))

@on_start_match("reset")
async def reset(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    context.reset(get_target_id(event), event.is_private)
    await send_text("上下文已重置")

@on_start_match("nickname")
async def nickname(event: MessageEvent):
        nicknames = await get_nicknames()
        user_id = str(event.sender.user_id)
        name = event.text.lstrip("nickname ")
        if not name:
            await send_text("你的昵称为："+str(nicknames[user_id]))
            return
        if name == "reset":
            await set_nickname(user_id, "")
            await send_text("已重置昵称")
        else:
            await set_nickname(user_id, name)
            await send_text("已设置昵称为："+name)

@on_start_match("marsho")
async def marsho(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await marsho_main(event, event.is_group)

async def marsho_main(event: Union[GroupMessageEvent, PrivateMessageEvent], is_group: bool):
        if event.text.lstrip("marsho") == "":
            await send_text(USAGE+"\n当前使用的模型："+model_name)
            await send_text(INTRODUCTION)
            await send_text(str(store.get_plugin_data_dir()))
            return
       # await UniMessage(str(text)).send()
        try:
            is_support_image_model = model_name.lower() in SUPPORT_IMAGE_MODELS
            usermsg = [] if is_support_image_model else ""
            user_id = str(event.sender.user_id)
            target_id = get_target_id(event)
            nicknames = await get_nicknames()
            nickname = nicknames.get(user_id, "")
            if nickname != "":
                nickname_prompt = f"\n*此消息的说话者:{nickname}*"
            else:
                nickname_prompt = ""
                await send_text("*你未设置自己的昵称。推荐使用'nickname [昵称]'命令设置昵称来获得个性化(可能）回答。")
            nickname_prompt = ""
            marsho_string_removed = False
            for i in event.get_segments("image"):
                if is_support_image_model:
                    imgurl = str(i.data["url"])
                    picmsg = ImageContentItem(
                        image_url=ImageUrl(url=str(await get_image_b64(imgurl)))
                    )
                    usermsg.append(picmsg)
                else:
                    await send_text("*此模型不支持图片处理。")
            for i in event.get_segments("text"):
                if not marsho_string_removed:
                    # 去掉最前面的"marsho "字符串
                    clean_text = i.data["text"].lstrip("marsho ")
                    marsho_string_removed = True  # 标记文本已处理
                else:
                    clean_text = i.data["text"]
                if is_support_image_model:
                    usermsg.append(TextContentItem(text=clean_text+nickname_prompt))
                else:
                    usermsg += str(clean_text+nickname_prompt)
            response = await make_chat(
                    client=client,
                    model_name=model_name,
                    msg=context.build(target_id, event.is_private)+[UserMessage(content=usermsg)])
            choice = response.choices[0]
            if choice["finish_reason"] == CompletionsFinishReason.STOPPED: # 当对话成功时，将dict的上下文添加到上下文类中
                context.append(UserMessage(content=usermsg).as_dict(), target_id, event.is_private)
                context.append(choice.message.as_dict(), target_id, event.is_private)
            elif choice["finish_reason"] == CompletionsFinishReason.CONTENT_FILTERED:
                await send_text("*已被内容过滤器过滤。请调整聊天内容后重试。")
                return
            await send_text(str(choice.message.content))
        except Exception as e:
            await send_text(str(e)+suggest_solution(str(e)))
            traceback.print_exc()
            return

@on_event(checker=PokeMarshoChecker())
async def poke(event: PokeNotifyEvent, adapter: Adapter): # 尚未实现私聊戳一戳 QwQ
    #await adapter.send_custom(str(event.user_id),group_id=event.group_id)
    user_id = str(event.user_id)
    nicknames = await get_nicknames()
    nickname = nicknames.get(user_id, "")
    # nicknames = await get_nicknames()
    # nickname = nicknames.get(user_id, "")
    nickname = ""
    try:
        if config.marshoai_poke_suffix != "":
            response = await make_chat(
                    client=client,
                    model_name=model_name,
                    msg=[get_prompt(),UserMessage(content=f"*{nickname}{config.marshoai_poke_suffix}")]
                )
            choice = response.choices[0]
            if choice["finish_reason"] == CompletionsFinishReason.STOPPED:
                await adapter.send_custom(" "+str(choice.message.content),group_id=event.group_id)
    except Exception as e:
        await adapter.send_custom(str(e)+suggest_solution(str(e)),group_id=event.group_id)
        traceback.print_exc()
        return

class MarshoAI(Plugin):
    version = VERSION
    flows = [changemodel,marsho,reset,poke,contexts,praises,nickname,add_assistantmsg,add_usermsg,load_context,save_context]
