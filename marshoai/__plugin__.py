import traceback
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import UserMessage, TextContentItem, ImageContentItem, ImageUrl, CompletionsFinishReason
from melobot import Plugin, send_text
from melobot.protocols.onebot.v11 import on_start_match, on_message, on_command
from melobot.protocols.onebot.v11.handle import Args
from melobot.protocols.onebot.v11.utils import MsgChecker, LevelRole, MsgCheckerFactory, StartMatcher, ParseArgs
from melobot.protocols.onebot.v11.adapter.event import MessageEvent
from azure.core.credentials import AzureKeyCredential
from .constants import *
from .config import Config 
from .util import *
from .models import MarshoContext


config = Config()
model_name = config.marshoai_default_model
context = MarshoContext()
token = config.marshoai_token
endpoint = config.marshoai_azure_endpoint
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token)
        )
checker_ft = MsgCheckerFactory(
    owner= config.owner,
    super_users=config.superusers
)
superuser_checker: MsgChecker = checker_ft.get_base(LevelRole.SU)

@on_command(checker=superuser_checker, cmd_start="/", cmd_sep=" ", targets="changemodel")
async def changemodel(args: ParseArgs = Args()):
    global model_name
    model_name = args.vals[0]
    await send_text("已切换")

@on_start_match("reset")
async def reset(event: MessageEvent):
    context.reset(event.user_id, event.is_private)
    await send_text("上下文已重置")


@on_start_match("marsho")
async def marsho(event: MessageEvent):
        if event.text.lstrip("marsho") == "":
            await send_text(USAGE)
            await send_text(INTRODUCTION)
            return
       # await UniMessage(str(text)).send()
        try:
            is_support_image_model = model_name.lower() in SUPPORT_IMAGE_MODELS
            usermsg = [] if is_support_image_model else ""
            user_id = event.sender.user_id
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
                    msg=context.build(event.user_id, event.is_private)+[UserMessage(content=usermsg)])
            choice = response.choices[0]
            if choice["finish_reason"] == CompletionsFinishReason.STOPPED: # 当对话成功时，将dict的上下文添加到上下文类中
                context.append(UserMessage(content=usermsg).as_dict(), event.user_id, event.is_private)
                context.append(choice.message.as_dict(), event.user_id, event.is_private)
            elif choice["finish_reason"] == CompletionsFinishReason.CONTENT_FILTERED:
                await send_text("*已被内容过滤器过滤。请调整聊天内容后重试。")
                return
            await send_text(str(choice.message.content))
        except Exception as e:
            await send_text(str(e)+suggest_solution(str(e)))
            traceback.print_exc()
            return

class MarshoAI(Plugin):
    version = VERSION
    flows = [changemodel,marsho,reset]
