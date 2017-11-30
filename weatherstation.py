# -*- coding: utf-8 -*-

import urllib
import json
import time as times
import requests
from socket import timeout


class station:
    def __init__(self, innumber, inname, incity, inlat, inlon):
        self.number = innumber
        self.name = inname
        self.city = incity
        self.lon = inlon
        self.lat = inlat
        self.realtimecontent = ''
        self.forecastcontent = ''
        self.realtimeupdatetime = 0
        self.forecastupdatetime = 0
        self.webrealupdatetime = ''
        self.webforecastupdatetime = ''

        self.airupdatetime = 0
        self.webairupdatetime = ''
        self.air = ''

    def __str__(self):
        return '站点信息：' + self.number + self.name

    def updatestationweather(self, name, station, forecast):

        timenow = times.time()
        self.realtimeupdatetime = timenow
        print('[' + times.strftime("%Y-%m-%d %H:%M:%S", times.localtime()) + ']获取' + station + name + '天气信息')

        # http://www.nmc.cn/f/rest/real/58367
        try:
            data = urllib.request.urlopen(
            'http://www.nmc.cn/f/rest/real/' + str(station), timeout = 5).read()
        except timeout:
            return '抱歉，请求超时，请稍后重试。'
        record = data.decode('UTF-8')
        data = json.loads(record)

        time = data['publish_time']
        T = data['weather']['temperature']
        P = data['weather']['airpressure']
        H = data['weather']['humidity']
        R = data['weather']['rain']
        weather = data['weather']['info']
        feellike = data['weather']['feelst']
        WD = data['wind']['direct']
        WL = data['wind']['power']
        WS = data['wind']['speed']

        result = ''
        result += '当前' + name + ':' + weather + '，实时气温：' + str(T) + '度，湿度：' + str(H) + '%，小时降水' + str(R) + 'mm，' \
                  + WD + WL + '\n'
        self.realtimecontent = result[0:result.find('\n')]
        self.webrealupdatetime = time
        # print(result)

        if forecast:
            date = []
            forecast = []
            Temp = []
            wd = []
            ws = []
            url = data['station']['url']
            try:
                index = urllib.request.urlopen(
                    'http://www.nmc.cn/' + url, timeout = 5).read()
            except timeout:
                return '抱歉，请求超时，请稍后重试。'
            indexhtmlfile = index.decode('UTF-8')
            indexhtmlfile = indexhtmlfile.replace(' ', '')  # 删除所有空格
            indexhtmlfile = indexhtmlfile[
                            indexhtmlfile.find('七天天气预报') + len('七天天气预报'):indexhtmlfile.find('<!-- 逐3小时天气 -->')]

            nightflag = False
            count = 0

            # print(indexhtmlfile)

            while (indexhtmlfile.find('<divclass="detail">') != -1):
                if count < 3:
                    indexhtmlfile = indexhtmlfile[indexhtmlfile.find('<td>') + len('<td>'):len(indexhtmlfile)]

                if count >= 3:
                    indexhtmlfile = indexhtmlfile[indexhtmlfile.find('<td>') + len('<td>'):len(indexhtmlfile)]
                else:
                    indexhtmlfile = indexhtmlfile[indexhtmlfile.find('<td>') + len('<td>'):len(indexhtmlfile)]

                tempdate = indexhtmlfile[0:indexhtmlfile.find('</td>')]
                tempdate = tempdate.replace('<p></p>', '')
                date.append(tempdate)  # 分析得到预报日日期

                # 判断是否为夜间预报，True：
                if indexhtmlfile.find('<tdcolspan="2"class="wdesc">') < 150 and indexhtmlfile.find(
                        '<tdcolspan="2"class="wdesc">') != -1:
                    # print('检测到夜间模式')
                    nightflag = True
                    indexhtmlfile = indexhtmlfile[
                                    indexhtmlfile.find('<tdcolspan="2"class="wdesc">') + len(
                                        '<tdcolspan="2"class="wdesc">'):len(indexhtmlfile)]
                    forecast.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的天气现象

                    indexhtmlfile = indexhtmlfile[
                                    indexhtmlfile.find('<tdcolspan="2"class="temp">') + len(
                                        '<tdcolspan="2"class="temp">'):len(
                                        indexhtmlfile)]
                    Temp.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的气温

                    indexhtmlfile = indexhtmlfile[
                                    indexhtmlfile.find('<tdcolspan="2"class="direct">') + len(
                                        '<tdcolspan="2"class="direct">'):len(
                                        indexhtmlfile)]
                    wd.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的风向

                    indexhtmlfile = indexhtmlfile[
                                    indexhtmlfile.find('<tdcolspan="2"class="power">') + len(
                                        '<tdcolspan="2"class="power">'):len(
                                        indexhtmlfile)]
                    ws.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的风速

                # False：
                else:
                    indexhtmlfile = indexhtmlfile[
                                    indexhtmlfile.find('<tdclass="wdesc">') + len('<tdclass="wdesc">'):len(
                                        indexhtmlfile)]
                    forecast.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的天气现象
                    if indexhtmlfile.find('<tdclass="wdesc">') < 100:
                        indexhtmlfile = indexhtmlfile[
                                        indexhtmlfile.find('<tdclass="wdesc">') + len('<tdclass="wdesc">'):len(
                                            indexhtmlfile)]
                        forecast.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的天气现象2

                    indexhtmlfile = indexhtmlfile[
                                    indexhtmlfile.find('<tdclass="temp">') + len('<tdclass="temp">'):len(indexhtmlfile)]
                    Temp.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的气温
                    if indexhtmlfile.find('<tdclass="temp">') < 100:
                        indexhtmlfile = indexhtmlfile[
                                        indexhtmlfile.find('<tdclass="temp">') + len('<tdclass="temp">'):len(
                                            indexhtmlfile)]
                        Temp.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的气温2

                    indexhtmlfile = indexhtmlfile[
                                    indexhtmlfile.find('<tdclass="direct">') + len('<tdclass="direct">'):len(
                                        indexhtmlfile)]
                    wd.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的风向
                    if indexhtmlfile.find('<tdclass="direct">') < 100:
                        indexhtmlfile = indexhtmlfile[
                                        indexhtmlfile.find('<tdclass="direct">') + len('<tdclass="direct">'):len(
                                            indexhtmlfile)]
                        wd.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的风向2

                    indexhtmlfile = indexhtmlfile[
                                    indexhtmlfile.find('<tdclass="power">') + len('<tdclass="power">'):len(
                                        indexhtmlfile)]
                    ws.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的风速
                    if indexhtmlfile.find('<tdclass="power">') < 100:
                        indexhtmlfile = indexhtmlfile[
                                        indexhtmlfile.find('<tdclass="power">') + len('<tdclass="power">'):len(
                                            indexhtmlfile)]
                        ws.append(indexhtmlfile[0:indexhtmlfile.find('</td>')])  # 分析得到预报的风速2

                indexhtmlfile = indexhtmlfile[indexhtmlfile.find('<divclass="detail">'):len(indexhtmlfile)]
                count += 1

            if nightflag:
                result += date[0] + '夜间：' + forecast[0] + '，最低气温：' + Temp[0] + '\n'
                for i in range(1, len(date)):
                    if forecast[2 * i - 1] != forecast[2 * i]:
                        result += date[i] + '：' + forecast[2 * i - 1] + '转' + forecast[2 * i] + '，气温：' + Temp[
                            2 * i] + '~' + Temp[2 * i - 1] + '\n'
                    else:
                        result += date[i] + '：' + forecast[2 * i - 1] + '，气温：' + Temp[2 * i] + '~' + Temp[
                            2 * i - 1] + '\n'
            else:
                for i in range(0, len(date)):
                    if forecast[2 * i] != forecast[2 * i + 1]:
                        result += date[i] + '：' + forecast[2 * i] + '转' + forecast[2 * i + 1] + '，气温：' + Temp[
                            2 * i + 1] + '~' + Temp[2 * i] + '\n'
                    else:
                        result += date[i] + '：' + forecast[2 * i] + '，气温：' + Temp[2 * i + 1] + '~' + Temp[2 * i] + '\n'
                        # print(date,forecast,Temp,wd,ws)
                        # print('nightflag:' + str(nightflag))
                        # print(indexhtmlfile)

            forecastresult = result[result.find('\n'):len(result)]
            self.forecastcontent = forecastresult
            self.forecastupdatetime = timenow

            self.webforecastupdatetime = time

        result += '以上信息于' + time + '更新，数据源自国家气象中心'
        return result

    def updatestationair(self,name,station):
        timenow = times.time()
        self.airupdatetime = timenow
        print('[' + times.strftime("%Y-%m-%d %H:%M:%S", times.localtime()) + ']获取' + station + name + '空气质量信息')

        # http://www.nmc.cn/f/rest/real/58367
        try:
            data = urllib.request.urlopen(
            'http://www.nmc.cn/f/rest/aqi/' + str(station), timeout = 5).read()
        except timeout:
            return '抱歉，请求超时，请稍后重试。'
        record = data.decode('UTF-8')
        data = json.loads(record)
        forecasttime = data['forecasttime']
        aqi = data['aqi']
        description = data['text']

        result = name + forecasttime + '实时空气质量指数：' + str(aqi) + ',' + description
        self.webairupdatetime = forecasttime
        self.air = result
        return result
    #def getrealtimedata(self, time, stationnumber):

    # def infoupdate(self):

    def getweather(self, name, station, forecast, timestamp):
        if forecast and (timestamp - self.forecastupdatetime > 60 * 60):
            self.updatestationweather(name,station,True)
        elif timestamp - self.realtimeupdatetime > 10 * 60:
            self.updatestationweather(name, station, False)

        if forecast:
            return self.realtimecontent + self.forecastcontent +'实况数据于'+self.webrealupdatetime+',预报于' + self.webforecastupdatetime + '更新，数据来源自国家气象中心'
        if not forecast:
            return self.realtimecontent + '\n实况数据于'+self.webrealupdatetime+ '更新，数据来源自国家气象中心'

    def getair(self,name,station,timestamp):
        if (timestamp - self.airupdatetime > 20 * 60):
               self.updatestationair(name,station)

        return self.air + '\n空气质量数据于' + self.webairupdatetime + '更新，数据来源自国家气象中心'

#function to return the webstation URL
#http://toy1.weather.com.cn/search?cityname={input}&callback=success_jsonpCallback
def getwebresource(input):
    url = 'http://toy1.weather.com.cn/search?cityname=' + input
    data = urllib.request.urlopen(url).read()
    record = data.decode('UTF-8')
    data = json.loads(record)