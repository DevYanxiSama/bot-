import json
from pathlib import *
import os
import asyncio
from typing import List
from BaseClass import *
from toolib import *
import traceback as tb
from websocket import create_connection
from websocket import WebSocket
from dict import *
import importlib


class Bot:

    def __init__(self):
        self.port = 1145
        self.ip = 'localhost'
        self.netWorkConfigFilePath = Path("config/network.config")
        self.websocket: WebSocket = None

        info("----程序准备启动----")
        self.readNetworkConfig()
        self.connectServer()

        self.loadPlugins = []
        self.running = true
        self.commands: List[Command] = []

        self.whyShutdown = "未定义原因"
        # 任何修改self.running的地方都必须修改self.whyShutdown
        asyncio.run(self.mainLoop())

    def createNewConfig(self, newConfig):
        with open(self.netWorkConfigFilePath, "w", encoding="utf-8") as writer:
            dump(newConfig, writer)
            return info(f"创建了新的网络配置,位于{self.netWorkConfigFilePath}")

    def readNetworkConfig(self):
        defaultNetworkConfig = {
            "ip": "localhost",
            'port': '1145'
        }
        if not self.netWorkConfigFilePath.parent.exists():
            info("初始化网络配置")
            self.netWorkConfigFilePath.parent.mkdir(parents=true, exist_ok=true)
            self.ip = defaultNetworkConfig["ip"]
            self.port = defaultNetworkConfig["port"]
            return self.createNewConfig(defaultNetworkConfig)
        if not self.netWorkConfigFilePath.exists():
            info("初始化网络配置")
            return self.createNewConfig(defaultNetworkConfig)
        try:
            with open(self.netWorkConfigFilePath, "r", encoding="utf-8") as reader:
                info("正在读取网络配置")
                readConfig = json.loads(reader.read())
                self.ip = readConfig["ip"]
                self.port = readConfig["port"]
                return info("网络配置读取成功")
        except json.JSONDecodeError as jde:
            return info(f"网络配置解析失败\n{jde}\n{tb.format_exc()}")
        except KeyError as ke:
            return info(f"网络配置内容不正确\n{ke}\n{tb.format_exc()}")

    def connectServer(self):
        info("尝试连接wss服务器")
        try:
            self.websocket = create_connection(f"ws://{self.ip}:{self.port}")
            return info("wss服务器连接成功")
        except Exception as e:
            self.running = false
            self.whyShutdown = "未连接wss服务器"
            return error(f"连接wss服务器失败\n{e}\n{tb.format_exc()}")

    async def messageHandler(self):
        info("消息处理器启动了")
        while self.running:
            recv_data: dict = json.loads(self.websocket.recv())
            # 这里不负责异步，线程调度处理
            message = MessageHandler(**recv_data)
            print(f"text:{message.textMessage}")
            for command in self.commands:
                command.exec(message)
        return

    async def mainLoop(self):
        info("准备加载命令")
        self.loadCommand()
        info("准备进入消息处理")
        await self.messageHandler()
        info("退出消息处理器")
        self.closeClient()
        info("程序退出")

    def closeClient(self):
        info(f"准备关闭客户端,因为{self.whyShutdown}")
        if self.websocket is not None:
            self.websocket.close()
        info("客户端已关闭")

    def loadCommand(self):
        """
        plugin文件夹存储插件
        文件名中必须包含plugin字符
        插件的文件名和插件中主类名必须一致

        """
        # 第一步，查看哪些插件是可以添加的
        pluginPath = Path("plugins")
        info("正在检查插件文件夹是否存在")
        if not pluginPath.exists():
            info("插件文件夹不存在，创建它")
            pluginPath.mkdir(parents=true, exist_ok=true)

        pluginPathContent = os.listdir(pluginPath)
        # 里面还混杂了文件夹，和非插件文件
        plugins = []
        # 疑似插件
        for ppc in pluginPathContent:
            if Path(pluginPath / ppc).is_file() and ("plugin" in ppc or "Plugin" in ppc):
                info(f"找到了插件:{ppc[:-3]}")
                plugins.append(ppc)
                # 只把文件名添加进去

        # 然后是遍历，尝试加载插件
        for plugin in plugins:
            info(f"尝试加载{plugin[:-3]}插件")
            # 还要去掉后缀
            pluginModule = importlib.import_module(f"{pluginPath}.{plugin[:-3]}")
            # 然后获取plugin类
            try:
                _pluginClass: PluginBase = getattr(pluginModule, plugin[:-3])(self)
                # 创建pluginClass实例，然后调用它的registerCommand方法，往主类commands注入Command对象
                _pluginClass.registerCommand()
                # 这样一个插件的命令就注册完毕了
                self.loadPlugins.append(_pluginClass)
                info(f"{plugin[:-3]}插件加载了")
            except AttributeError as ae:
                error(f"{plugin} 插件加载失败,无法找到主类,请确保主类名与文件名一致\n{ae}\n{tb.format_exc()}")

        if not self.loadPlugins:
            # 没找到插件
            self.running = false
            self.whyShutdown = "未找到插件,无法运行"
            return


if __name__ == '__main__':
    bot = Bot()
