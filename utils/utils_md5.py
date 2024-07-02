# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: utils_md5.py
@time: 2024/7/2 20:47
@desc:

"""
import hashlib


class Tools:
    @staticmethod
    def make_md5(data, salt=b""):
        """

        """
        md5_machine = hashlib.md5(salt)
        md5_machine.update(str(data).encode('utf-8'))
        return md5_machine.hexdigest()
