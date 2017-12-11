#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time       : 2017/12/11 18:25
# @Author     : 周星星 Siman Chou
# @Site       : https://github.com/simanchou
# @File       : nginx_status_exporter.py
# @Description: 
import requests
import yaml
import os


def getConf(file="conf.yml"):
    conf_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], "etc", file)
    if os.path.exists(conf_file):
        with open(conf_file, "r", encoding="utf-8") as fp:
            conf = yaml.load(fp.read())
        return conf
    else:
        print("Error,while loading conf file '{}'".format(file))
        return None


url = "http://192.168.50.40/nginx_status"
c = requests.get(url)
r = c.content.decode("utf-8").splitlines()
print(r)


if __name__ == "__main__":
    conf = getConf()
    print(type(conf))
    print(conf)
