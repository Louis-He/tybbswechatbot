# -*- coding: utf-8 -*-

import os
from searchsession import *
from weatherstation import *
from apistatics import *
import werobot
import time
import urllib
import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler
global weatherstation

weatherstation = []
onlinesession = [] # list to store the information of chatting
robot = werobot.WeRoBot(token='louishe999617')
#client = robot.client

#DEVELOPING...
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

#DEVELOPING...
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

#DEVELOPING...
def getweather():
    source = 'EC'
    iodata = getData(source, -79.399, 43.663)
    result = analyze(source, iodata)
    print('[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']发送天气信息完成')
    return result

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
    # f = open('/root/qxahz/stations.txt')
    f = open('stations.txt')#读入站点文件
    tmp = ''
    line = f.readline()
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

def addplotmission(userinput):
    i = userinput.replace('，',',')
    i = i.replace('。', '.')
    i = i.replace('e', 'E')
    i = i.replace('c', 'C')
    i = i.replace('g', 'G')
    i = i.replace('f', 'F')
    i = i.replace('s', 'S')
    i = i.replace('v', 'V')

    try:
        source = i[0:i.find(',')]
        i = i[i.find(',')+1:len(i)]
        plottype = i[0:i.find(',')]
        i = i[i.find(',') + 1:len(i)]
        lon = i[0:i.find(',')]
        i = i[i.find(',') + 1:len(i)]
        lat = i[0:len(i)]

        if plottype == 'G':
            plottype = 'ground'
        elif plottype == 'V':
            plottype = 'vertical'
        '''
        print('!![LON]!!' + lon)
        print('!![LAT]!!' + lat)
        print('!![SOURCE]!!' + source)
        print('!![PLOT_TYPE]!!' + plottype)
        '''
        f = open('/root/station_forecast/website/waitlistmission.sh', 'a+')
        f.write('python3 main.py --lon ' + lon + ' --lat ' + lat + ' --source ' + source + ' --type ' + plottype + '\n')
        f.close()
        return '[操作成功]任务添加成功，输入"Tybbsget列表"查看任务进程。'
    except:
        return '[操作失败]任务添加失败，请检查输入语法或联系管理员。'

def getfunc(userinput):
    userinput = userinput.replace('Pic','pic')
    if userinput[0:2] == '列表':
        path = '/root/station_forecast/website/static/images/'
        files = os.listdir(path)
        #finallist = []
        result = ''
        count = 1
        for file in files:
            if file[-3:] == 'png':
                #finallist.append(file)
                if count < len(files):
                    result = result + str(count) + '. ' + file + '\n'
                else:
                    result = result + str(count) + '. ' + file + '\n输入Tybbsget（图片编号）获取图片，例如：Tybbsgetpic1'
            count += 1
        return result

    if userinput[0:3] == 'pic':
        picnum = userinput[3:len(userinput)]
        path = '/root/station_forecast/website/static/images/'
        files = os.listdir(path)
        # finallist = []
        result = ''
        count = 1
        try:
            for file in files:
                if file[-3:] == 'png' and count == int(picnum):
                    return [
                        [
                            "图形产品返回结果",
                            "图形产品，编号："+picnum+"，产品名："+file,
                            "http://138.68.4.232:8084/static/images/" + file,
                            "http://138.68.4.232:8084/static/images/" + file
                        ]
                    ]
        except:
            return "获取图形产品失败，请检查"



#import and analyze the weather station infomation file
getstationfile()

#initialize statistic variables
minbrowse = 0
statistic = statics()

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

daily = ''

#gettoken()
daily = getdaymsg() #daily message
scheduler = BackgroundScheduler()
scheduler.add_job(getdaymsg, 'interval', seconds = 24 * 60 * 60)  # 24hr
scheduler.start()

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
            return [
                [
                    "开发者 Developer Louis-He",
                    "开发者Github主页 Developer Github",
                    "https://avatars0.githubusercontent.com/u/28524641?s=460&v=4",
                    "https://github.com/Louis-He"
                ]
            ]
        elif msg.content[-4:len(msg.content)] == '污染地图'  or msg.content[-6:len(msg.content)] == '空气污染地图':
            return [
                [
                    "中国地区污染地图",
                    "中国地区污染地图",
                    "http://138.68.4.232:8083/static/images/aqi.png",
                    "http://138.68.4.232:8083/index"
                ]
            ]
        elif msg.content[-2:len(msg.content)] == '管理':
            return('服务器运行正常')
        elif msg.content[0:2] == '绘图':
            return('输入语法：Tybbsplot,(机构),(类型),(经度),(纬度)，例如：Tybbsplot,EC,G,121.25,31.45')
        elif msg.content[0:9] == 'Tybbsplot':
            return addplotmission(msg.content[10:len(msg.content)])
        elif msg.content[0:8] == 'Tybbsget':
            return getfunc(msg.content[8:len(msg.content)])
        else:
            getwebresource(msg.content)
    except:
        return ('欢迎关注中国气象爱好者～\n*.[新功能]输入"污染地图"查看全国空气质量地图\n1.输入相关城市进行天气查询，例如："北京天气"，"上海天气"\n'
                    '2.输入相关城市进行实况要素查询，例如："广州实况"，"乌鲁木齐实况"\n'
                '3.输入相关城市进行空气质量查询，例如："哈尔滨空气"，"厦门空气"\n' + daily)


# let the server listen at the port 0.0.0.0:80
robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = 80
robot.run()


#debug section
#getwebresource('上海')