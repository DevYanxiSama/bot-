# bot-
一个简易的bot后端

**不商用的前提下，允许随意修改代码**
**注册插件:你需要在plugins文件夹中创建一个名字包含Plugin(或首字母小写)的py文件,并且在其中写一个与文件名相同的类，这个类需要继承BaseClass.PluginBase类并且实现init方法,在init方法中:**

## 机器人协议端推荐:
## https://github.com/NapNeko/NapCatQQ

## 开始:
### python -m pip install requests

#### @self.commandManager.createCommand("命令", "介绍", bool(是否仅管理员可用此命令), false(是否需要at), true(仅群聊可用), mode.equals(命令的检测模式,正则 或 必须用户消息等于pattern))
#### def 命令功能的函数(message:toolib.MessageHandler):
####   pass

//作者还在更新中，可能有bug，请提交issues
