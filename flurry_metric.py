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

class Metric_Handler(tornado.web.RequestHandler):
           
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

    def get_flurry_metric(self,appid,appname,startDate,endDate,METRIC_NAME,versionName):
        appinfo=app_info()
        appinfo=appinfo[appid]

        url = 'http://api.flurry.com/appMetrics/'
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
        full_url = url + METRIC_NAME + '?' + url_values
        data = urllib2.urlopen(full_url)
        res=data.read()
        res=re.sub(r'null', '"null"', res)
        res=eval(res)
        chartx=[]
        charty=[]
        chartz=[]
        ult=[]
        for x in range(0,len(res['day'])):
            chartx.append(res['day'][x]['@date'])
            if x<6:
                charty.append(int(res['day'][x]['@value']))
                m=int(res['day'][x]['@value'])
                chartz.append(m)

            else:
                charty.append(int(res['day'][x]['@value']))
                m=0
                for i in range(x-6,x+1):
                    m+=int(res['day'][i]['@value'])
                m=int(m/7)
                chartz.append(m)

            resultlst=[appname,METRIC_NAME,res['day'][x]['@date'],res['day'][x]['@value'],str(m),versionName]
            resultlst="<tr><td>"+ '</td><td>'.join(resultlst) + "</td></tr>"
            ult.append(resultlst)

        ult=''.join(ult)
        return chartx,charty,chartz,ult
        
    def get(self):
        appid=self.get_argument('appname','0')
        startDate = self.get_argument('startDate',self.daynbefore(60))
        endDate = self.get_argument('endDate',self.daynbefore(2))
        METRIC_NAME = self.get_argument('METRIC_NAME','ActiveUsers').encode('utf8')
        versionName = self.get_argument('versionName','').encode('utf8')

        appset=appsets()
        appname=appset[str(appid)]

        appset=OrderedDict(sorted(appset.items(), key=lambda t: int(t[0])))

        res_for_html=self.get_flurry_metric(appid,appname,startDate,endDate,METRIC_NAME,versionName)
        version_lst=self.get_version(appid)

        metric_lst=['NewUsers','ActiveUsers','ActiveUsersByWeek','ActiveUsersByMonth','MedianSessionLength','AvgSessionLength','Sessions']

        self.render("flurry_metric.html", METRIC_NAME=METRIC_NAME,versionName=versionName,startDate=startDate,endDate=endDate,appset=appset,appid=appid,tt=res_for_html[3],chartx=res_for_html[0],charty=res_for_html[1],chartz=res_for_html[2],metric_lst=metric_lst,version_lst=version_lst
        )
