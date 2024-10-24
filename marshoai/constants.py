__version__ = "0.3.1"
VERSION = __version__
USAGE: str = f"""MarshoAI-Melobot Beta v{__version__} by Asankilp
用法：
  marsho <聊天内容> : 与 Marsho 进行对话。当模型为 GPT-4o(-mini) 等时，可以带上图片进行对话。
  reset : 重置当前会话的上下文。
超级用户命令(均需要加上命令前缀使用):
  /changemodel <模型名> : 切换全局 AI 模型。
※本AI的回答"按原样"提供，不提供任何担保。AI也会犯错，请仔细甄别回答的准确性。"""

SUPPORT_IMAGE_MODELS: list = ["gpt-4o","gpt-4o-mini","llama-3.2-90b-vision-instruct","llama-3.2-11b-vision-instruct"]
REASONING_MODELS: list = ["o1-preview","o1-mini"]
INTRODUCTION: str = """你好喵~我是一只可爱的猫娘AI，名叫小棉~🐾！
我是基于 Melobot 酱开发的哦~
我的代码在这里哦~↓↓↓
https://github.com/LiteyukiStudio/marshoai-melo"""