from abc import ABC, abstractmethod
from typing import List

from toolib import *


class Bot:

    def __init__(self):
        self.port = 1145
        self.ip = 'localhost'
        self.loadPlugins = []
        self.running = true
        self.commands: List[Command] = []

        self.whyShutdown = "未定义原因"


class PluginBase(ABC):

    @abstractmethod
    def __init__(self, mainClass: Bot):
        self.mainClass = mainClass
        self.pluginName = "新插件"
        self.description = "插件介绍"
        self.commands:List[Command] = []
        self.init()

    def registerCommand(self):
        """这个方法往主类注入Command对象"""
        for command in self.commands:
            self.mainClass.commands.append(command)

    @abstractmethod
    def init(self):
        pass