from __future__ import division
import urllib2
import urllib
import codecs
import re
import math
import time
import datetime
import sys
import operator
execfile(sys.path[0]+ '/'+ 'app_info.py')
from collections import OrderedDict

class Flurry_Show_Handler(tornado.web.RequestHandler):

    def daynbefore(self,n):
        today = datetime.date.today()
        Nday = datetime.timedelta(days=n)
        return today - Nday

    def get_version(self,appid):
        appinfo=app_info()
        appinfo=appinfo[appid]

        url = 'http://api.flurry.com/appInfo/getApplication'
        data = {}
        data['apiAccessCode'] = appinfo["apiAccessCode"]
        data['apiKey'] = appinfo["apiKey"]

        url_values = urllib.urlencode(data)
        full_url = url + '?' + url_values
        data = urllib2.urlopen(full_url)
        res=data.read()
        res=re.sub(r'null', '"null"', res)
        res=eval(res)
        version_lst=['ALL']

        for x in range(0,len(res['version'])):
            version_lst.append(res['version'][x]["@name"])
        return version_lst


    def get_flurry_activeuser(self,appid,startDate,endDate,versionName):
            appinfo=app_info()
            appinfo=appinfo[appid]

            url = 'http://api.flurry.com/appMetrics/ActiveUsers'
            data = {}
            data['apiAccessCode'] = appinfo["apiAccessCode"]
            data['apiKey'] = appinfo["apiKey"]
            data['startDate'] = startDate
            data['endDate'] = endDate

            if versionName=='' or versionName=='ALL':
                versionName=''
            else:
                data['versionName'] = versionName
                versionName=versionName

            url_values = urllib.urlencode(data)
            full_url = url + '?' + url_values
            data = urllib2.urlopen(full_url)
            res=data.read()
            res=re.sub(r'null', '"null"', res)
            res=eval(res)

            activeusers=0
            for x in range(0,len(res['day'])):
                # activeusers+=1
                activeusers+=int(res['day'][x]['@value'])

            return activeusers

    def game(self,appid,appname,startDate,endDate,versionName,switch):

        appinfo=app_info()
        appinfo=appinfo[appid]

        url = 'http://api.flurry.com/eventMetrics/Summary'
        data = {}
        data['apiAccessCode'] = appinfo["apiAccessCode"]
        data['apiKey'] = appinfo["apiKey"]
        data['startDate'] = startDate
        data['endDate'] = endDate

        if versionName=='' or versionName=='ALL':
            versionName=''
        else:
            data['versionName'] = versionName  
            versionName=versionName
        url_values = urllib.urlencode(data)
        full_url = url + '?' + url_values
        data = urllib2.urlopen(full_url)
        res=data.read()
        res=eval(res)
        eventres=res['event']
        eventres=sorted(eventres, key=operator.itemgetter('@eventName'))  
        ult=[]

        if versionName=='ALL':
            versionName_href=''
        else:
            versionName_href="&versionName=" + versionName

        href1=["<a href='flurry_event_daily.py?appname=",str(appid),versionName_href,"&startDate=",str(self.daynbefore(60)), "&endDate=",str(self.daynbefore(2)),"&eventName="]
        href1=''.join(href1)
        href2="' target='_blank'>"
        href3="</a>"

        if switch=='on':
            activeUsers=self.get_flurry_activeuser(appid,startDate,endDate,versionName)
        else:
            activeUsers=''

        for x in range(0,len(eventres)):
            if switch=='on':
                activeUser=str(round(int(eventres[x]['@avgUsersLastDay'])/activeUsers*100,2))+'%'
            else:
                activeUser=''

            if not re.search(r'Combine_|1301-%E6%88%91%E7%9A%84%E8%A1%97',eventres[x]['@eventName']):
                resultlst=[appname,res['@startDate'],res['@endDate'],href1 + eventres[x]['@eventName'] +href2+ eventres[x]['@eventName'] +href3,eventres[x]['@totalCount'],eventres[x]['@totalSessions'],eventres[x]['@avgUsersLastDay'],versionName,activeUser]
                resultlst="<tr><td>"+ '</td><td>'.join(resultlst) + "</td></tr>"
                ult.append(resultlst)
        return ''.join(ult)     
        
    def get(self):
        appid=self.get_argument('appname','0')
        startDate = self.get_argument('startDate','').encode('utf8')
        endDate =  self.get_argument('endDate','').encode('utf8')
        versionName = self.get_argument('versionName','').encode('utf8')
        switch = self.get_argument('switch','').encode('utf8')

        appset=appsets()
        appname=appset[str(appid)]

        appset=OrderedDict(sorted(appset.items(), key=lambda t: int(t[0])))
        version_lst=self.get_version(appid)
        swtich_lst=['off','on']

        if startDate=='' or endDate=='':
            startDate=self.daynbefore(2)
            endDate=self.daynbefore(2)
            res=''
        else:
            res=self.game(appid,appname,startDate,endDate,versionName,switch)


        self.render("flurry_event_summary.html",versionName=versionName,startDate=startDate,endDate=endDate,res=res,appset=appset,appid=appid,version_lst=version_lst,swtich_lst=swtich_lst,switch=switch)
    
    
    
    

