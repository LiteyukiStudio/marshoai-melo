<div align="center">
  <img src="https://raw.githubusercontent.com/LiteyukiStudio/marshoai-melo/refs/heads/main/resources/logo.png" width="400" height="400" alt="Logo">
  <br>
</div>

<div align="center">

# marshoai-melo

_✨ 使用 Azure OpenAI 推理服务的聊天机器人（施工中） ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/LiteyukiStudio/marshoai-melo.svg" alt="license">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 📖 介绍

通过调用由 Azure OpenAI 驱动，GitHub Models 提供访问的生成式 AI 推理 API 来实现聊天的 Melobot 机器人。  
内置了猫娘小棉(Marsho)的人物设定，可以进行可爱的聊天！  
*谁不喜欢回复消息快又可爱的猫娘呢？*  
**※对 Azure AI Studio等的支持待定。对 OneBot 以外的适配器支持未经过完全验证。**
[Nonebot2 实现](https://github.com/LiteyukiStudio/nonebot-plugin-marshoai)
## 🐱 设定
#### 基本信息

- 名字：小棉(Marsho)
- 生日：9月6日

#### 喜好

- 🌞 晒太阳晒到融化
- 🤱 撒娇啊～谁不喜欢呢～
- 🍫 吃零食！肉肉好吃！
- 🐾 玩！我喜欢和朋友们一起玩！


## 🤖 获取 token
- 如果你未获取GitHub Models的早期访问权限，请前往[GitHub Marketplace中的Models分页](https://github.com/marketplace/models)，点击`Get early access`按钮获取早期访问权限。**进入waitlist阶段后，需要等待数日直到通过申请。** ~~也可以试着白嫖其它人的token~~
- [新建一个personal access token](https://github.com/settings/tokens/new)，**不需要给予任何权限**。
- 将新建的 token 复制，添加到`MARSHOAI_TOKEN`配置项中。
## 🎉 使用

发送`marsho`指令可以获取使用说明

#### 👉 戳一戳
当 melobot 连接到支持的 OneBot v11 实现端时，可以接收头像双击戳一戳消息并进行响应。详见`MARSHOAI_POKE_SUFFIX`配置项。
## ⚙️ 配置

在 `bot.py` 所在目录的`.env`文件中添加下表中的配置

|      配置项       | 必填 | 默认值 |                             说明                             |
| :---------------: | :--: | :----: | :----------------------------------------------------------: |
| MARSHOAI_TOKEN |  是  |   无    | 调用 API 必需的访问 token |
| MARSHOAI_DEFAULT_MODEL | 否 | `gpt-4o-mini` | Marsho 默认调用的模型 |
| MARSHOAI_PROMPT | 否 | 猫娘 Marsho 人设提示词 | Marsho 的基本系统提示词 |
| MARSHOAI_ADDITIONAL_PROMPT | 否 | 无 | Marsho 的扩展系统提示词 |
| MARSHOAI_POKE_SUFFIX | 否 | `揉了揉你的猫耳` | 对 Marsho 所连接的 OneBot 用户进行双击戳一戳时，构建的聊天内容。此配置项为空字符串时，戳一戳响应功能会被禁用。例如，默认值构建的聊天内容将为`*[昵称]揉了揉你的猫耳`。 |
| MARSHOAI_ENABLE_PRAISES | 否 | `true` | 是否启用夸赞名单功能（未实现） |
| MARSHOAI_ENABLE_TIME_PROMPT | 否 | `true` | 是否启用实时更新的日期与时间（精确到秒）与农历日期系统提示词 |
| MARSHOAI_AZURE_ENDPOINT | 否 | `https://models.inference.ai.azure.com` | 调用 Azure OpenAI 服务的 API 终结点 |
| MARSHOAI_TEMPERATURE | 否 | 无 | 进行推理时的温度参数 |
| MARSHOAI_TOP_P | 否 | 无 | 进行推理时的核采样参数 |
| MARSHOAI_MAX_TOKENS | 否 | 无 | 返回消息的最大 token 数 |

## © 版权说明
"Marsho" logo 由 [@Asankilp](https://github.com/Asankilp) 绘制，基于 [CC BY-NC-SA 4.0](http://creativecommons.org/licenses/by-nc-sa/4.0/) 许可下提供。  
"Melobot" logo 由 [@mldkouo](https://github.com/mldkouo) 绘制，版权归属于 [@Meloland](https://github.com/meloland)。