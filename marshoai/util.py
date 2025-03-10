import base64
import mimetypes
import os
import json
import httpx
from datetime import datetime
from zhDateTime import DateTime
from .localstore import PluginStore
from typing import Union
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from melobot.protocols.onebot.v11.adapter.event import GroupMessageEvent, PrivateMessageEvent
from .config import Config
from .constants import PLUGIN_NAME
config = Config()
store = PluginStore(PLUGIN_NAME)

# 时间参数相关
if config.marshoai_enable_time_prompt:
    _weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    _time_prompt = "现在的时间是{date_time}{weekday_name}，{lunar_date}。"

async def get_image_b64(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            # 获取图片数据
            image_data = response.content
            content_type = response.headers.get('Content-Type')
            if not content_type:
                content_type = mimetypes.guess_type(url)[0]
            image_format = content_type.split('/')[1] if content_type else 'jpeg'
            base64_image = base64.b64encode(image_data).decode('utf-8')
            data_url = f"data:{content_type};base64,{base64_image}"
            return data_url
        else:
            return None

async def make_chat(client: ChatCompletionsClient, msg, model_name: str):
   return await client.complete(
           messages=msg,
           model=model_name,
           temperature=config.marshoai_temperature,
           max_tokens=config.marshoai_max_tokens,
           top_p=config.marshoai_top_p
                )
def get_praises():
    praises_file = store.get_plugin_data_file("praises.json") # 夸赞名单文件使用localstore存储
    if not os.path.exists(praises_file):
        init_data = {
            "like": [
                    {
                        "name": "Asankilp",
                        "advantages": "赋予了Marsho猫娘人格，使用vim与vscode为Marsho写了许多代码，使Marsho更加可爱"
                    },
                    {
                        "name": "律回(aicorein,Melorenae)",
                        "advantages": "创造了Melobot(同样是可爱的猫娘)，Marsho与她和Melobot亲密接触"
                    }
                ]
            }
        with open(praises_file,"w",encoding="utf-8") as f:
            json.dump(init_data,f,ensure_ascii=False,indent=4)
    with open(praises_file,"r",encoding="utf-8") as f:
        data = json.load(f)
    return data

def build_praises():
    praises = get_praises()
    result = ["你喜欢以下几个人物，他们有各自的优点："]
    for item in praises["like"]:
        result.append(f"名字：{item['name']}，优点：{item['advantages']}")
    return "\n".join(result)

async def save_context_to_json(name: str, context: str):
    context_dir = store.get_plugin_data_dir() / "contexts"
    os.makedirs(context_dir, exist_ok=True)
    file_path = os.path.join(context_dir, f"{name}.json")
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(context, json_file, ensure_ascii=False, indent=4)

async def load_context_from_json(name: str):
    context_dir = store.get_plugin_data_dir() / "contexts"
    os.makedirs(context_dir, exist_ok=True)
    file_path = os.path.join(context_dir, f"{name}.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []
async def set_nickname(user_id: str, name: str):
    filename = store.get_plugin_data_file("nickname.json")
    if not os.path.exists(filename):
        data = {}
    else:
        with open(filename,'r') as f:
            data = json.load(f)
    data[user_id] = name
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def get_nicknames():
    filename = store.get_plugin_data_file("nickname.json")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_target_id(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    try:
        return event.group_id
    except AttributeError:
        return event.user_id

def get_prompt():
    prompts = ""
    prompts += config.marshoai_additional_prompt
    if config.marshoai_enable_praises:
        praises_prompt = build_praises()
        prompts += praises_prompt
    if config.marshoai_enable_time_prompt:
        prompts += _time_prompt.format(
            date_time=(current_time := DateTime.now()).strftime(
                "%Y年%m月%d日 %H:%M:%S"
            ),
            weekday_name=_weekdays[current_time.weekday()],
            lunar_date=current_time.chinesize.date_hanzify(
                "农历{干支年}{生肖}年{月份}月{数序日}"
            ),
        )
    marsho_prompt = config.marshoai_prompt
    spell = SystemMessage(content=marsho_prompt+prompts).as_dict()
    return spell

def suggest_solution(errinfo: str) -> str:
    suggestions = {
        "content_filter": "消息已被内容过滤器过滤。请调整聊天内容后重试。",
        "RateLimitReached": "模型达到调用速率限制。请稍等一段时间或联系Bot管理员。",
        "tokens_limit_reached": "请求token达到上限。请重置上下文。",
        "content_length_limit": "请求体过大。请重置上下文。",
        "unauthorized": "Azure凭据无效。请联系Bot管理员。",
        "invalid type: parameter messages.content is of type array but should be of type string.": "聊天请求体包含此模型不支持的数据类型。请重置上下文。",
        "At most 1 image(s) may be provided in one request.": "此模型只能在上下文中包含1张图片。如果此前的聊天已经发送过图片，请重置上下文。"
    }

    for key, suggestion in suggestions.items():
        if key in errinfo:
            return f"\n{suggestion}"
    
    return ""
