# -*- coding: utf-8 -*-
import werobot
import time
import urllib
import json
import requests
from sympy import *
from apscheduler.schedulers.background import BackgroundScheduler

robot = werobot.WeRoBot(token='louishe999617')
client = robot.client

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
    return timenow+'每日一句：\n'+note+'\n'+chinese

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

def gettoken():
    client.grant_token()
    timenow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print('[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']access_token获取成功')
    return timenow

daily = ''

#gettoken()
daily = getdaymsg() #初始化每日一句
scheduler = BackgroundScheduler()
scheduler.add_job(getdaymsg, 'interval', seconds=24 * 60 * 60)  # 间隔24小时执行一次
scheduler.start()  # 这里的调度任务是独立的一个线程

@robot.handler
def hello(msg):
    ts = '['+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg.time-4*60*60))+']'
    f = open('/root/wechatbot/message.txt', 'a+')
    f.write(ts + '\t' + msg.source + ':\t' + msg.content + '\n')
    f.close()
    print(ts + msg.source+' --> '+msg.content)

    if msg.content == '天气' or msg.content == '气温' or msg.content == '气象':
        try:
            print('[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']准备发送天气信息')
            return getweather()
        except:
            return '[ERR100:内部错误]抱歉，调取最新天气失败'
    elif msg.content[0:2] == '叮咚':
        try:
            usr = str(msg.source)
            print('检测到用户：' + usr)
        except:
            usr = 'unknown'
            print('[WARNING]无法检测到用户')
        message = msg.content[2:len(msg.content)]

        try:
            print('[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']自动回复开启')
            reply = turingreply(message, usr)
            print('[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']自动回复：' + reply)
            return reply + '[auto-reply]'
        except:
            return '[ERR199:未知错误]抱歉，出现了未知错误'
    elif msg.content == '每日一句':
        return daily
    else:
        return '欢迎关注小白叮咚～欢迎和我互动哦\n1、输入叮咚求导（语法例如:叮咚求导2*x^2）返回导数\n2、输入叮咚RREF（语法例如:叮咚rref1,2;3,4）返回RREF\n' \
               '3、输入叮咚（语法例如：叮咚你好）进行机器人智能回复\n4、输入天气：查询加拿大多伦多天气[测试板块]\n'+daily

# 让服务器监听在 0.0.0.0:80
robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = 80
robot.run()
