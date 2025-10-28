from abc import abstractmethod, ABC
from json import dumps as _dumps
from json import dump as _dump
import json
import logging
import traceback as tb
from pathlib import *
import datetime as dt
from typing import List
import re
from enum import Enum

import requests

false = False
true = True
admin = []


class BuildMessage:

    @staticmethod
    def atMessage(qq) -> dict:
        return {
            'type': 'at',
            'data': {
                'qq': qq
            }
        }

    @staticmethod
    def textMessage(message) -> dict:
        return {
            'type': 'text',
            'data': {
                'text': message
            }
        }

    @staticmethod
    def replyMessage(messageId) -> dict:
        return {
            'type': 'reply',
            'data': {
                'id': messageId
            }
        }

    @staticmethod
    def diceMessage() -> dict:
        return {
            'type': 'dice'
        }

    @staticmethod
    def rpsMessage() -> dict:
        return {
            'type': 'rps'
        }

    @staticmethod
    def videoMessage(path):
        return {
            'type': 'video',
            'data': {
                'file': path
            }
        }

    @staticmethod
    def fileMessage(filePath):
        return {
            'type': 'file',
            'data': {
                'file': filePath
            }
        }

    @staticmethod
    def audioMessage(path):
        return {
            'type': 'record',
            'data': {
                'file': path
            }
        }

    @staticmethod
    def imageMessage(path):
        return {
            'type': 'image',
            'data': {
                'file': path
            }
        }


class MessageHandler:

    def __init__(self, self_id=0, user_id="0", time=0, message_id=0, message_seq=0, real_id=0, real_seq=0,
                 message_type="None",
                 sender={}, raw_message="",
                 font=14, sub_type="normal",
                 message=[],
                 message_format='array', post_type='message', group_id=0, group_name="测试", target_id=0, **kwargs):
        self.target_id: int = target_id
        self.raw_message: str = raw_message
        self.real_seq: str = real_seq
        self.real_id: int = real_id
        self.message_seq: int = message_seq
        self.message_id: int = message_id
        self.time: int = time
        self.user_id: str = user_id
        self.self_id: int = self_id
        self.sub_type: str = sub_type  # 如果是好友，它的值为friend
        self.message_type: str = message_type
        self.group_name: str = group_name
        self.group_id: int = group_id
        self.post_type: str = post_type
        self.message_format: str = message_format
        self.font: int = font
        self.message: list = message
        self.sender: dict = sender

        self.private = "private"
        self.group = "group"
        self.bm = BuildMessage
        self.images = []
        self.at = []
        self.videos = []
        self.audios = []
        self.textMessage = ""

        self.httpPath = "http://127.0.0.1:8083/"
        # http服务器地址
        self.loadMessages()

    def getProfile(self, qq) -> dict:
        """可以获取用户信息"""
        result = {'status': 'error', 'data': {"nickname": "获取失败"}}
        data = {"user_id": qq}
        try:
            result = requests.post(self.httpPath + "get_stranger_info", data=json.dumps(data)).json()
            if result is None or result["status"] != "ok":
                result = {'status': 'error', 'data': {"nickname": "获取失败"}}
        except requests.Timeout:
            error("账号信息获取失败：请求超时")
        except Exception as e:
            error(f"账号信息获取失败\n{e}\n{tb.format_exc()}")
        return result

    def sendPrivateMessage(self, qq, message: list[dict]):
        """传进来的必须是一个消息列表，消息用self.bm合成"""
        data = {
            'user_id': qq,
            'message': message
        }
        result = {'status': 'error'}

        try:
            result = requests.post(self.httpPath + "send_private_msg", data=json.dumps(data)).json()
            # 这里还要对消息发送失败做一些处理
            if result["status"] != "ok":
                error(f"发送失败:{result}")
        except requests.Timeout:
            error("发送私聊消息失败：请求超时")
        except Exception as e:
            error(f"发送私聊消息失败\n{e}\n{tb.format_exc()}")

        return result

    def sendAutoTypeMessage(self, message: list[dict]):
        """如果当前消息是群消息，就会在当前群聊发消息"""
        data = {
            'message': message
        }
        path = ""
        messageType = "未定义类型"
        if self.message_type == self.private:
            data['user_id'] = self.sender
            path = "send_private_msg"
            messageType = "私聊"
        if self.message_type == self.group:
            data["group_id"] = self.group_id
            path = "send_group_msg"
            messageType = "群聊"

        result = {'status': 'error'}
        try:
            result = requests.post(self.httpPath + path, data=json.dumps(data)).json()
            # 这里还要对消息发送失败做一些处理
            if result["status"] != "ok":
                error(f"发送失败:{result}")
        except requests.Timeout:
            error(f"发送{messageType}消息失败：请求超时")
        except Exception as e:
            error(f"发送{messageType}消息失败\n{e}\n{tb.format_exc()}")
        return result

    def sendGroupMessage(self, group_id, message: list['dict']):
        data = {
            'group_id': group_id,
            'message': message
        }
        result = {'status': 'error'}
        try:
            result = requests.post(self.httpPath + "send_group_msg", data=json.dumps(data)).json()
            # 这里还要对消息发送失败做一些处理
            if result["status"] != "ok":
                error(f"发送失败:{result}")
        except requests.Timeout:
            error("发送群聊消息失败：请求超时")
        except Exception as e:
            error(f"发送群聊消息失败\n{e}\n{tb.format_exc()}")
        return result

    def ban(self, group_id, qq, banTime=60):
        """设置禁言"""
        result = {'status': 'error'}
        data = {
            "group_id": group_id,
            "user_id": qq,
            "duration": banTime
        }
        try:
            result = requests.post(self.httpPath + "set_group_ban", data=json.dumps(data)).json()
            # 这里还要对消息发送失败做一些处理
            if result["status"] != "ok":
                error(f"发送失败:{result}")
        except requests.Timeout:
            error("设置群聊禁言失败：请求超时")
        except Exception as e:
            error(f"设置群聊禁言失败\n{e}\n{tb.format_exc()}")
        return result

    def setGroupWholeBan(self, group_id, newStatus: bool):
        result = {'status': 'error'}
        data = {
            "group_id": group_id,
            "enable": newStatus
        }
        try:
            result = requests.post(self.httpPath + "set_group_whole_ban", data=json.dumps(data)).json()
            # 这里还要对消息发送失败做一些处理
            if result["status"] != "ok":
                error(f"发送失败:{result}")
        except requests.Timeout:
            error("设置全体失败：请求超时")
        except Exception as e:
            error(f"设置全体失败\n{e}\n{tb.format_exc()}")
        return result

    def leaveGroup(self, group_id):
        result = {'status': 'error'}
        data = {
            "group_id": group_id
        }
        try:
            result = requests.post(self.httpPath + "set_group_leave", data=json.dumps(data)).json()
            # 这里还要对消息发送失败做一些处理
            if result["status"] != "ok":
                error(f"发送失败:{result}")
        except requests.Timeout:
            error("退出群聊失败：请求超时")
        except Exception as e:
            error(f"退出群聊失败\n{e}\n{tb.format_exc()}")
        return result

    # 管理加群请求
    def setAddGroupRequestStatus(self, requestId, newStatus: bool, because=""):
        """设置"""
        result = {'status': 'error'}
        data = {
            "flag": requestId,
            "approve": newStatus,
            "reason": because
        }
        try:
            result = requests.post(self.httpPath + "set_group_add_request", data=json.dumps(data)).json()
            # 这里还要对消息发送失败做一些处理
            if result["status"] != "ok":
                error(f"发送失败:{result}")
        except requests.Timeout:
            error("管理加群申请失败：请求超时")
        except Exception as e:
            error(f"管理加群申请失败\n{e}\n{tb.format_exc()}")
        return result

    def getGroupList(self):
        """设置禁言"""
        result = {'status': 'error'}
        try:
            result = requests.post(self.httpPath + "get_group_list").json()
            if result["status"] != "ok":
                error(f"发送失败:{result}")
        except requests.Timeout:
            error("获取群列表失败：请求超时")
        except Exception as e:
            error(f"获取群列表失败\n{e}\n{tb.format_exc()}")
        return result

    def loadMessages(self):
        for message in self.message:
            match message["type"]:
                case "file":
                    if ".mp4" in message["data"]["file"]:
                        self.videos.append(message['data']['url'])
                        # 把文件链接添加进去
                        self.textMessage += "[文件:视频]"
                        continue
                    if ".mp3" in message["data"]["file"]:
                        self.audios.append(message['data']['url'])
                        # 把文件链接添加进去
                        self.textMessage += "[文件:音频]"
                        continue
                case "text":
                    self.textMessage += message["data"]["text"]

                case 'at':
                    nickname = self.getProfile(message["data"]["qq"])['data']["nickname"]

                    self.textMessage += f"[{nickname}]"
                    self.at.append(message["data"]["qq"])

                case "image":
                    self.images.append(message["data"]["url"])


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
        self.commands: List[Command] = []

    def registerCommand(self):
        """这个方法往主类注入Command对象"""
        for command in self.commands:
            self.mainClass.commands.append(command)


def log(content, level):
    today = dt.datetime.today()
    today.weekday()
    system_time = f"{today.year}年-{today.month}月-{today.day}日-{today.hour}时-{today.minute}分-{today.second}秒"
    outputContent = f"[{system_time}][{level}]: {content}"
    print(outputContent)
    filePath = Path(f"{today.year}年-{today.month}月-{today.day}日.log")
    notInit = filePath.exists()
    with open(filePath, "a+") as writer:
        if notInit:
            # 已经有内容了，附加
            writer.write(f"\n{outputContent}")
        else:
            writer.write(f"日志开始于 {today.year}年-{today.month}月-{today.day}日.log")
        writer.close()


info = lambda content: log(content, "INFO")
debug = lambda content: log(content, "DEBUG")
warn = lambda content: log(content, "WARN")
error = lambda content: log(content, "ERROR")
critical = lambda content: log(content, "CRITICAL")


def dumps(json: dict):
    return _dumps(json, ensure_ascii=false, indent=4)


def dump(json: dict, wf):
    return _dump(json, wf, ensure_ascii=false, indent=4)


def checkJsonValue(path: Path, key: str, value: str | int | bool) -> bool:
    """给定一个路径，然后判断路径的某个key的值是否为value
    路径不存在：返回 false"""
    if not path.exists():
        return false
    with open(path, "r") as reader:
        data = json.load(reader)
        try:
            return data[key] == value
        except KeyError:
            return false


def setJsonValue(path: Path, key: str, value: str | int | bool | list | dict) -> bool:
    if not path.exists():
        return false
    data = {}
    with open(path, "r") as reader:
        data = json.load(reader)
        data[key] = value
    with open(path, "w") as writer:
        dump(data, writer)
        return True


def getJsonValue(path: Path, key: str) -> bool | list | dict | None | int | str | float | tuple:
    """给定一个路径，然后判断路径的某个key的值是否为value
    路径不存在：返回 false"""
    if not path.exists():
        return None
    with open(path, "r") as reader:
        data = json.load(reader)
        try:
            return data[key]
        except KeyError:
            return None


def pathAutoCreate(path: Path, pathParents: bool = false) -> Path:
    targetPath = path
    if pathParents:
        targetPath = path.parent
    if not path.exists():
        targetPath.mkdir(parents=true, exist_ok=true)
    return path


class CommandMode:
    regex = "Regex"
    equals = "EQUALS"


mode = CommandMode


class Command:
    def __init__(self, pattern: str, description: str = "新命令", adminOnly: bool = false, atCommand: bool = false,
                 function=lambda: warn("未指定功能"), groupOnly: bool = false, commandMode=CommandMode.regex):
        self.commandMode = commandMode  # 如果pattern就是命令本身，而非正则表达式，你应该修改它的值为CommandMode.equals
        self.groupOnly = groupOnly
        self.function = function
        self.atCommand = atCommand
        self.adminOnly = adminOnly
        self.description = description
        self.pattern = pattern
        """pattern就是命令，可以使用正则表达式，或者直接填命令(需要把searchMode设置为CommandMode.equals)"""
        self.mode = CommandMode

    def canExec(self, message: MessageHandler) -> bool:
        match self.commandMode:
            case self.mode.regex:  # 正则表达式模式
                return bool(re.findall(self.pattern, message.textMessage))
            case self.mode.equals:
                return self.pattern == message.textMessage

    def exec(self, message: MessageHandler):
        if not self.canExec(message):  # 如果你希望别人发消息每次都会真正的执行你的命令，可以把这段去除
            return
        if self.adminOnly and message.sender not in admin:
            return message.sendAutoTypeMessage([message.bm.textMessage("此命令仅允许管理员使用")])

        info(f"执行了命令:{self.pattern} | {message.textMessage}")
        if message.message_type == message.private:
            return message.sendPrivateMessage(message.sender, [message.bm.textMessage("此命令仅允许群聊使用")])

        self.function(message)


class CommandManager:

    def __init__(self, parent: PluginBase):
        self.commands = []
        self.parent: PluginBase = parent

    def createCommand(self, pattern: str, description: str = "新命令", adminOnly: bool = false, atCommand: bool = false,
                      groupOnly: bool = false, commandMode=CommandMode.regex):
        def targetFunc(func):
            # 完成命令的注册
            self.parent.commands.append(
                Command(pattern, description, adminOnly, atCommand, func, groupOnly, commandMode))

        return targetFunc
