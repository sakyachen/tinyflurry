# @sakyachen
# coding:utf-8
# apiAccessCode:flurry账号的的apiAccessCode，需要在Manage中开启，每个账号独立，在https://dev.flurry.com/manageCompany.do
# apiKey:flurry的API Key，每个应用独立，在https://dev.flurry.com/manageProjectInfo.do的App Info中
# appname:记录在结果文件中的app名称

__version__ = '0.8'

def app_info():
    return {"0":{
                      "apiAccessCode":"xxxxxxxxxxxxxxxxxx",
                      "apiKey":"xxxxxxxxxxxxxxxxxx",
                      "appname":"testA"
                      },
            "1":{
                      "apiAccessCode":"xxxxxxxxxxxxxxxxxx",
                      "apiKey":"xxxxxxxxxxxxxxxxxx",
                      "appname":"testB"}

            }

def appsets():
    app_dic=app_info()
    app_sets={}
    for app in app_dic:
        app_sets[app]=app_dic[app]['appname']
    return app_sets