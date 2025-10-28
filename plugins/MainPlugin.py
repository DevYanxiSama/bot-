import os
import random

from BaseClass import *
from toolib import *

genPath = Path("资源")
if not genPath.exists():
    genPath.mkdir(parents=true, exist_ok=true)


class MainPlugin(PluginBase):

    def __init__(self, mainClass: Bot):
        self.pluginName = "主插件"
        self.description = "一个简单的插件 PVP_yanxi"
        self.commands: List[Command] = []
        self.mainClass: Bot = mainClass
        self.commandManager: CommandManager = CommandManager(self)
        self.init()

    def init(self):
        @self.commandManager.createCommand("检测", "检测机器人运行状态", false, false, false, mode.equals)
        def checkRunning(message: MessageHandler):
            return message.sendAutoTypeMessage([message.bm.textMessage("机器人运行中")])
