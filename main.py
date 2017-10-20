# -*- coding: utf-8 -*-
from weatherstation import *
import werobot
import time
import urllib
import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler
global weatherstation

weatherstation = []
robot = werobot.WeRoBot(token='louishe999617')
#client = robot.client

def getData(org,lon,lat):
    if org == 'GFS':
        data = urllib.request.urlopen('https://node.windy.com/forecast/v2.1/gfs/' + str(lat) +'/' + str(lon) + '?source=detail').read()
    if org == 'EC':
        data = urllib.request.urlopen('https://node.windy.com/forecast/v2.1/ecmwf/' + str(lat) +'/' + str(lon) + '?setup=summary&includeNow=true&source=hp').read()
    record = data.decode('UTF-8')
    data = json.loads(record)

    '''
    for i in range(0,len(data)):
        station.append(data[i]['station']['city'])
        province.append(data[i]['station']['province'])
        code.append(data[i]['station']['code'])
        time.append(data[i]['publish_time'])
        T.append(data[i]['temperature'])
        day1day.append(float(data[i]['detail'][0]['day']['weather']['temperature']))
        day1night.append(data[i]['detail'][0]['night'])
        day2day.append(float(data[i]['detail'][1]['day']['weather']['temperature']))
        day2night.append(data[i]['detail'][1]['night'])

        day1dayweather.append(int(data[i]['detail'][0]['day']['weather']['img']))
        day2dayweather.append(int(data[i]['detail'][1]['day']['weather']['img']))
    '''
    print(data)
    return data

def analyze(source, JSON):
    n = 0
    T = []
    HI = []
    LOW = []
    IC = []
    DATE = []

    seq = []
    result = "来自" + source + "模型的Toronto City天气预报：\n"
    #print(JSON)
    #'NOAA-GFS' OR 'ECMWF-HRES'
    model = JSON['header']['model']
    reftime = JSON['header']['refTime']
    daily = JSON['summary']
    print('[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']获取天气数据')
    for i in daily:
        t = daily[i]['timestamp']
        daymax = daily[i]['tempMax']
        daymin = daily[i]['tempMin']
        icon = daily[i]['icon']

        T.append(t/100000.0)
        HI.append(daymax)
        LOW.append(daymin)
        if icon == 1:
            icon = 'Sunny'
        elif icon == 2:
            icon = 'Cloudy'
        elif icon == 3:
            icon = 'Overcast'
        elif icon == 4:
            icon = 'Drizzle'
        elif icon == 5:
            icon = 'Moderate Rain'
        elif icon == 6:
            icon = 'Heavy Rain'
        elif icon == 7:
            icon = 'Shower'
        elif icon == 9:
            icon = 'Snow'
        elif icon == 10:
            icon = 'Heavy Snow'




        IC.append(icon)
        DATE.append(i)
        seq.append(n)
        n += 1
        #print(i + '\tHI:' + str(round(daymax - 273.15, 1)) + '°C, LOW:' + str(round(daymin - 273.15, 1)) + '°C')
        #result += (i + '\nHI:' + str(round(daymax - 273.15, 1)) + '°C, LOW:' + str(round(daymin - 273.15, 1)) + '°C\n')

    #根据日期顺序进行排序
    min = 99999999
    lastpos = 0
    pos = 0
    n = 0
    for i in range(0,len(T)):
        for i in range(n, len(T)):
            if T[i] < min:
                min = T[i]
                pos = i

        temp = seq[n]
        seq[n] = seq[pos]
        seq[pos] = temp

        temp = T[n]
        T[n] = T[pos]
        T[pos] = temp

        min = 99999999
        n += 1

    for i in range(0, len(DATE)):
        result += (DATE[seq[i]] + '\n' + str(IC[seq[i]]) + ', HI:' + str(round(HI[seq[i]] - 273.15, 1)) + '°C, LOW:' + str(round(LOW[seq[i]] - 273.15, 1)) + '°C' + '\n')

    return result

def getweather():
    source = 'EC'
    iodata = getData(source, -79.399, 43.663)
    result = analyze(source, iodata)
    print('[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']发送天气信息完成')
    return result

def turingreply(msg,usr):
    data = {'key': '1f87c3c9cf3b4867b412267f8c7c1d30',
            'info': msg,
            'loc': '',
            'userid': usr}
    r = requests.post(url='http://www.tuling123.com/openapi/api', data = data)
    result = json.loads(r.text)
    return result['text']

def getdaymsg():
    global daily
    timenow = time.strftime("%Y-%m-%d", time.localtime())
    data = urllib.request.urlopen(
        'http://open.iciba.com/dsapi/').read()
    record = data.decode('UTF-8')
    data = json.loads(record)
    note = data["content"]
    chinese = data["note"]
    print('[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']每日一句获取成功')
    daily = timenow+'每日一句：\n'+note+'\n'+chinese
    return timenow+'每日一句：\n'+note+'\n'+chinese

def getstationfile():
    # f = open('/root/qxahz/stations.txt')  # 返回一个文件对象
    f = open('stations.txt')
    tmp = ''
    line = f.readline()  # 调用文件的 readline()方法
    while line:
        tmp = line
        tmp = tmp.replace('\n', '')
        while (tmp.find(' ') != -1):
            id = tmp[0:tmp.find(' ')]
            tmp = tmp[tmp.find(' ') + 1:len(tmp)]

            name = tmp[0:tmp.find(' ')]
            tmp = tmp[tmp.find(' ') + 1:len(tmp)]

            city = tmp[0:tmp.find(' ')]
            tmp = tmp[tmp.find(' ') + 1:len(tmp)]

            lat = tmp[0:tmp.find(' ') - 1]
            tmp = tmp[tmp.find(' ') + 1:len(tmp)]

            lon = tmp[0:tmp.find(' ') - 1]
            tmp = tmp[tmp.find(' ') + 1:len(tmp)]
        print(id, name, city, lat, lon)
        weatherstation.append(station(id, name, city, lat, lon))
        line = f.readline()
    f.close()

def getcnweather(usrinput, forecast):
    print(usrinput)
    ts = time.time()
    best = False
    requeststation = []
    stationnumbers = []
    seq = []

    for i in range(0,len(weatherstation)):
        if weatherstation[i].name == usrinput:
            requeststation.append(weatherstation[i].name)
            stationnumbers.append(weatherstation[i].number)
            seq.append(i)
            best = True

    if not best:
        for i in weatherstation:
            if i.name.find(usrinput) != -1:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)
            elif usrinput.find(i.name) != -1:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)
            elif i.city == usrinput and not best:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)
            elif i.city.find(usrinput) != -1 and not best:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)
            elif usrinput.find(i.city) != -1 and not best:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)

    if best:
        if forecast:
            result = weatherstation[seq[0]].getweather(weatherstation[seq[0]].name, weatherstation[seq[0]].number, True, ts)
        else:
            result = weatherstation[seq[0]].getweather(weatherstation[seq[0]].name, weatherstation[seq[0]].number, False, ts)
        #
    else:
        try:
            result = '查找到以下相关站点，请输入选择：(例如：' + requeststation[0] + '天气)\n'
            for i in requeststation:
                if i != requeststation[len(requeststation)-1]:
                    result += i + ','
                else:
                    result += i
            return result
        except:
            return "抱歉，没有找到相关站点"
    return result

def getcnair(usrinput):
    print(usrinput)
    ts = time.time()
    best = False
    requeststation = []
    stationnumbers = []
    seq = []

    for i in range(0, len(weatherstation)):
        if weatherstation[i].name == usrinput:
            requeststation.append(weatherstation[i].name)
            stationnumbers.append(weatherstation[i].number)
            seq.append(i)
            best = True

    if not best:
        for i in weatherstation:
            if i.name.find(usrinput) != -1:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)
            elif usrinput.find(i.name) != -1:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)
            elif i.city == usrinput and not best:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)
            elif i.city.find(usrinput) != -1 and not best:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)
            elif usrinput.find(i.city) != -1 and not best:
                requeststation.append(i.name)
                stationnumbers.append(i.number)
                seq.append(i)

    if best:
        try:
            result = weatherstation[seq[0]].getair(weatherstation[seq[0]].name, weatherstation[seq[0]].number, ts)
        except:
            result = '抱歉，该城市没有空气质量数据'
            #
    else:
        try:
            result = '查找到以下相关站点，请输入选择：(例如：' + requeststation[0] + '空气)\n'
            for i in requeststation:
                if i != requeststation[len(requeststation) - 1]:
                    result += i + ','
                else:
                    result += i
            return result
        except:
            return "抱歉，没有找到相关站点"
    return result


getstationfile()

'''
def clearlog():
    #clear logs every hour
    f = open('/home/weather/hsefz_server/wxbot/record/txtrecord.txt', 'w')
    f.write('[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']record重新写入')
    f.close()  # you can omit in most cases as the destructor will call it
    print('[' + time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime()) + ']record重制完成')

scheduler = BackgroundScheduler()
scheduler.add_job(clearlog, 'interval', seconds = 3600 * 6)#间隔6小时执行一次
scheduler.start()    #这里的调度任务是独立的一个线程
'''


daily = ''

#gettoken()
daily = getdaymsg() #初始化每日一句
scheduler = BackgroundScheduler()
scheduler.add_job(getdaymsg, 'interval', seconds = 24 * 60 * 60)  # 间隔24小时执行一次
scheduler.start()  # 这里的调度任务是独立的一个线程

@robot.handler
def hello(msg):
    try:
        ts = '['+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg.time-4*60*60))+']'
        f = open('/root/qxahz/message.txt', 'a+')
        f.write(ts + '\t' + msg.source + ':\t' + msg.content + '\n')
        f.close()
        print(ts + msg.source+' --> '+msg.content)

        if msg.content == '每日一句':
            return daily
        elif msg.content[-2:len(msg.content)] == '天气' or msg.content[-2:len(msg.content)] == '气象' \
                or msg.content[-2:len(msg.content)] == '温度' or msg.content[-2:len(msg.content)] == '气温':
            return(getcnweather(msg.content[0:-2],True))
        elif msg.content[-2:len(msg.content)] == '实况' or msg.content[-2:len(msg.content)] == '实测' \
                or msg.content[-2:len(msg.content)] == '监测':
            return (getcnweather(msg.content[0:-2],False))
        elif msg.content[-2:len(msg.content)] == '空气':
            return (getcnair(msg.content[0:-2]))
        elif msg.content[-4:len(msg.content)] == '空气质量':
            return (getcnair(msg.content[0:-4]))
        elif msg.content[-3:len(msg.content)] == 'aqi' or msg.content[-3:len(msg.content)] == 'AQI':
            return (getcnair(msg.content[0:-3]))
        elif msg.content[-3:len(msg.content)] == '开发者'  or msg.content[-2:len(msg.content)] == '关于':
            '''
                [
                    "title",
                    "description",
                    "img",
                    "url"
                ],
            '''
            return [
                [
                    "开发者 Developer Louis-He",
                    "开发者Github主页 Developer Github",
                    "https://avatars0.githubusercontent.com/u/28524641?s=460&v=4",
                    "https://github.com/Louis-He"
                ]
            ]
        else:
            return ('欢迎关注中国气象爱好者～\n1.输入相关城市进行天气查询，例如："北京天气"，"上海天气"\n'
                    '2.输入相关城市进行实况要素查询，例如："广州实况"，"乌鲁木齐实况"\n'
                    '3.输入相关城市进行空气质量查询，例如："哈尔滨空气"，"厦门空气"\n' + daily)
    except:
        return ('欢迎关注中国气象爱好者～\n1.输入相关城市进行天气查询，例如："北京天气"，"上海天气"\n'
                    '2.输入相关城市进行实况要素查询，例如："广州实况"，"乌鲁木齐实况"\n'
                '3.输入相关城市进行空气质量查询，例如："哈尔滨空气"，"厦门空气"\n' + daily)

# 让服务器监听在 0.0.0.0:80
robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = 80
robot.run()

#print(getstationweather('漠河',50136, false))
