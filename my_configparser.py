#-*- coding: utf-8 -*-

import configparser


#继承自configparser.ConfigParser，目的为了支持配置文件区分大小写
class MyConfigParser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr


