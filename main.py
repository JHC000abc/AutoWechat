# -*- coding: utf-8 -*-

import sys
import json
from ctypes import windll

from utils.utils_process import get_specific_process
from wechat_operation.wx_operation import WxOperation

DEBUG = True
# MAX_NUMS值参考 :好友总量//10 + 1
MAX_NUMS = 90
# 0:搜索发送 模糊匹配 1:标签
SEND_MODE = 0

wx = WxOperation()


class WechatSelf(object):
    """

    """

    def __init__(self):
        self.friends_list = []
        self.remark_map = {}
        self.nick_map = {}
        self.tag_map = {}
        self.black_list = []
        self.white_list = []
        self.send_msg_list = []
        self.send_file_list = []
        self.send_person_list = []

    def read_yield(self, file):
        """

        """
        lis = []
        with open(file, "r", encoding="utf-8") as fp:
            for i in fp:
                if i.strip():
                    lis.append(i.strip())
        return lis

    def get_file_list(self):
        """

        """
        self.send_person_list = self.read_yield("sendperson.list")
        self.black_list = self.read_yield("black.list")
        self.white_list = self.read_yield("white.list")
        self.send_msg_list = self.read_yield("sendmsg.list")
        self.send_file_list = self.read_yield("sendfile.list")

    def make_remark_nick_map(self):
        """

        """
        assert self.friends_list != [], "未获取到完整通讯录"
        remark_map = {}
        nick_map = {}
        tag_map = {}
        for user_info in self.friends_list:
            remark_name = user_info["remark_name"]
            nick_name = user_info["nick_name"]
            tag_name = user_info["tag_name"] if user_info["tag_name"] else "无标签"
            if remark_map.get(remark_name) is None:
                remark_map[remark_name] = user_info
            if nick_map.get(nick_name) is None:
                nick_map[nick_name] = user_info

            if tag_map.get(tag_name) is None:
                tag_map[tag_name] = [user_info]
            else:
                tag_map[tag_name].append(user_info)

        self.remark_map = remark_map
        self.nick_map = nick_map
        self.tag_map = tag_map
        print(self.tag_map)
        self.get_file_list()

    def get_friends_list(self):
        """
        获取通讯录数据
        """
        friends_list = []
        try:
            if not DEBUG:
                friends_list = wx.get_friend_list(num=MAX_NUMS)
                with open("friends.json", "w", encoding="utf-8") as fp:
                    fp.write(json.dumps(friends_list, indent=4, ensure_ascii=False))
                    print(f"成功导出好友：{len(friends_list)}")
            else:
                with open("friends.json", "r", encoding="utf-8") as fp:
                    friends_list = json.loads(fp.read())
                    print(f"成功导出好友：{len(friends_list)}")
            # raise ValueError('1231241')
        except Exception as e:
            print("获取失败", e, e.__traceback__.tb_lineno)
        finally:
            self.friends_list = friends_list
            self.make_remark_nick_map()

    def check_send(self, account):
        """

        """
        flag = False
        if self.white_list:
            if account in self.white_list:
                flag = True
        else:
            if not self.black_list:
                flag = True
            else:
                if account not in self.black_list:
                    flag = True
        return flag

    def send_by_tag(self):
        """

        """
        assert self.send_person_list != [], "未获取到要发送的人员标签"
        # 支持模糊发送，前提是获取到了完整的通讯录数据
        for tag in self.send_person_list:
            user_info_list = self.tag_map.get(tag, None)
            if user_info_list:
                for user_info in user_info_list:
                    remark_name = user_info["remark_name"]
                    try:
                        if self.check_send(remark_name):
                            wx.send_msg(remark_name, self.send_msg_list, self.send_file_list)
                            print(f"发送:{remark_name, self.send_msg_list, self.send_file_list}")
                    except:
                        print(f"不发送用户：{remark_name}")
            else:
                print(f"不存在标签：{tag}")

    def send(self):
        """

        """
        assert self.friends_list != [], "未获取到完整通讯录"
        assert self.remark_map != {}, "未获取到完整通讯录"
        assert self.nick_map != {}, "未获取到完整通讯录"
        assert self.send_person_list != [], "未获取到要发送的人员名单"
        # 支持模糊发送，前提是获取到了完整的通讯录数据
        for account in self.send_person_list:
            try:
                if self.check_send(account):
                    # 如果当前面板已经是需发送好友, 则无需再次搜索跳转
                    if not wx._match_nickname(name=account):
                        if not wx._goto_chat_box(name=account):
                            raise NameError('昵称不匹配')
                    wx.send_msg(account, self.send_msg_list, self.send_file_list)
                    print(f"发送:{account, self.send_msg_list, self.send_file_list}")
                else:
                    print(f"不发送用户：{account}")
            except Exception as e:
                print(e, e.__traceback__.tb_lineno)
                account_lis = []
                for user_info in self.friends_list:
                    remark_name = user_info["remark_name"]
                    nick_name = user_info["nick_name"]

                    if account in remark_name:
                        account_lis.append(remark_name)
                    else:
                        if account in nick_name:
                            account_lis.append(nick_name)
                account_lis = list(set(account_lis)) if account_lis else account_lis
                print(f"共计识别到符合条件的人数：{len(account_lis)},{account_lis}")
                if account_lis:
                    for account in account_lis:
                        if self.check_send(account):
                            print(f"模糊发送:{account, self.send_msg_list, self.send_file_list}")
                            wx.send_msg(account, self.send_msg_list, self.send_file_list)
                        else:
                            print(f"不发送用户：{account}")


if __name__ == "__main__":
    try:
        myapp_id = 'company.product.sub_product.version'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myapp_id)
    except ImportError:
        pass
    wechat_process = get_specific_process()
    if wechat_process:
        ws = WechatSelf()
        ws.get_friends_list()

        if SEND_MODE == 0:
            # 搜索发送
            ws.send()
        elif SEND_MODE == 1:
            # 根据标签发送
            ws.send_by_tag()
    else:
        print("严重错误,微信未启动!")
        sys.exit()  # 退出程序
