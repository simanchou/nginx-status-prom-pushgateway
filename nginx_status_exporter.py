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
import time


def getConf(file="conf.yml"):
    conf_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], "etc", file)
    if os.path.exists(conf_file):
        with open(conf_file, "r", encoding="utf-8") as fp:
            conf = yaml.load(fp.read())
        return conf
    else:
        print("Error,while loading conf file '{}'".format(file))
        return None


def getNginxStatus(url):
    statusDict = {}
    try:
        r = requests.get(url)
        c = r.content.decode("utf-8").splitlines()
        statusDict["nginx_up"] = 1
        statusDict["connections"] = int(c[0].split(":")[-1].strip())
        statusDict["accepts"] = int(c[2].split()[0].strip())
        statusDict["handled"] = int(c[2].split()[1].strip())
        statusDict["requests"] = int(c[2].split()[2].strip())
        statusDict["reading"] = int(c[3].split()[1].strip())
        statusDict["writing"] = int(c[3].split()[3].strip())
        statusDict["waiting"] = int(c[3].split()[5].strip())
        #print(statusDict)
    except:
        statusDict["nginx_up"] = 0
    return statusDict


def exportToGateway(nginxStatusUrl, gateway, job, group, instance, host, env, service):
    gwUrl = "http://{}/metrics/job/{}/group/{}/instance/{}/host/{}/env/{}/service/{}".format(gateway,
                                                                                             job,
                                                                                             group,
                                                                                             instance,
                                                                                             host,
                                                                                             env,
                                                                                             service)
    nginxStatus = getNginxStatus(nginxStatusUrl)
    if nginxStatus["nginx_up"]:
        data = "nginx_up{} {}\n".format("{}", 1)
        for k, v in nginxStatus.items():
            if k != "nginx_up":
                data += "nginx_status{} {}\n".format("{}state=\"{}\"{}".format("{", k, "}"), nginxStatus[k])
    else:
        data = "nginx_up{} {}\n".format("{}", 0)
    #print(data)
    r = requests.put(gwUrl, data=data)
    return r.text


if __name__ == "__main__":
    conf = getConf()

    gateway = conf["global"]["gateway"]
    interval = conf["global"]["interval"]

    while True:
        for i in conf["target_configs"]:
            job = i["job"]
            for j in i["static_configs"]:
                group = j["group"]
                host = j["host"]
                env = j["env"]
                service = j["service"]
                for instance in j["targets"]:
                    nginxStatusUrl = instance
                    instance = instance.split("/")[2]
                    exportToGateway(nginxStatusUrl,gateway,job,group,instance,host,env,service)
        time.sleep(interval)
