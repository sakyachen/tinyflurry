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

class Event_Daily_Handler(tornado.web.RequestHandler):   
           
    def daynbefore(self,N):
        today = datetime.date.today()
        Nday = datetime.timedelta(days=N)
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

        activeusers={}
        for x in range(0,len(res['day'])):
            # activeusers+=1
            activeusers[res['day'][x]['@date']]=int(res['day'][x]['@value'])

        return activeusers


    def get_flurry_event_by_event(self,appid,appname,startDate,endDate,eventName,versionName,switch):
        appinfo=app_info()
        appinfo=appinfo[appid]

        url = 'http://api.flurry.com/eventMetrics/Event' 
        data = {}
        data['apiAccessCode'] = appinfo["apiAccessCode"] 
        data['apiKey'] = appinfo["apiKey"]
        data['startDate'] = startDate
        data['endDate'] = endDate
        data['eventName'] = eventName

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
        chartx=[]
        charty=[]
        chartz=[]
        ult=[]

        if switch=='on':
            activeUsers=self.get_flurry_activeuser(appid,startDate,endDate,versionName)
        else:
            activeUsers={}

        for x in range(0,len(res['day'])):
            chartx.append(res['day'][x]['@date'])
            if x<6:
                charty.append(int(res['day'][x]['@uniqueUsers']))
                m=int(res['day'][x]['@uniqueUsers'])
                chartz.append(m)

            else:
                charty.append(int(res['day'][x]['@uniqueUsers']))
                m=0
                for i in range(x-6,x+1):
                    m+=int(res['day'][i]['@uniqueUsers'])
                m=int(m/7)
                chartz.append(m)

            if switch=='on':
                activeUser=activeUsers[str(res['day'][x]['@date'])]
                activeUserRatio=str(round(int(res['day'][x]['@uniqueUsers'])/activeUser*100,1))+'%'
            else:
                activeUser=''
                activeUserRatio=''

            resultlst=[appname,res['@eventName'],res['day'][x]['@date'],res['day'][x]['@totalCount'],res['day'][x]['@uniqueUsers'],versionName,str(m),str(activeUser),activeUserRatio]
            resultlst="<tr><td>"+ '</td><td>'.join(resultlst) + "</td></tr>"
            ult.append(resultlst)

        ult=''.join(ult)
        return chartx,charty,chartz,ult

    def get(self):
        appid=self.get_argument('appname',0)
        startDate = self.get_argument('startDate',self.daynbefore(60)).encode('utf8')
        endDate = self.get_argument('endDate',self.daynbefore(2)).encode('utf8')
        eventName = self.get_argument('eventName','010000_%E5%BE%AE%E4%BF%A1%E6%94%B6%E6%AC%BE').encode('utf8')
        versionName = self.get_argument('versionName','').encode('utf8')
        switch = self.get_argument('switch','').encode('utf8')
        appset=appsets()
        appname=appset[str(appid)]

        appset=OrderedDict(sorted(appset.items(), key=lambda t: int(t[0])))
        
        res_for_html=self.get_flurry_event_by_event(appid,appname,startDate,endDate,eventName,versionName,switch)
        version_lst=self.get_version(appid)
        swtich_lst=['off','on']

        self.render("flurry_event_daily.html", eventName=eventName,versionName=versionName,startDate=startDate,endDate=endDate,appset=appset,appid=appid,
        tt=res_for_html[3],chartx=res_for_html[0],charty=res_for_html[1],chartz=res_for_html[2],version_lst=version_lst,swtich_lst=swtich_lst,switch=switch
        )
