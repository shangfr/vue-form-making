# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 15:18:53 2020

@author: ShangFR
"""
import time
import json
import random
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Date, Integer, String, ForeignKey
from pyppeteer import launch
from pyppeteer.launcher import connect
from lxml import etree
import asyncio


def iPhone():
    iphone6 = {
        'name': 'iPhone 6',
        'userAgent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
        'viewport': {
            'width': 375,
            'height': 667,
            'deviceScaleFactor': 2,
            'isMobile': True,
            'hasTouch': True,
            'isLandscape': False,
        }
    }

    return iphone6


async def getBaseinfo(keyword):
    print('getBaseinfo')
    datare = {}

    # browser = await launch(headless=headless(), userDataDir=datafolder(), args=['--disable-infobars','--no-sandbox'])
    browser = await launch()
    # browser = await connect({'browserWSEndpoint': 'http://m.qcc.com'})
    page = await browser.newPage()
    await page.emulate(iPhone())
    # 设置浏览器
    await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15'
                            ' (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1')
    # 防止被识别，将webdriver设置为false
    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')

    # qcc
    await page.waitFor(5000)
    await page.goto('https://m.qcc.com/search?key=' + keyword)
    await page.waitFor(5000)
    await page.waitFor('a.a-decoration')
    normal_list = await page.xpath('//*[@class="a-decoration"]')
    url = await (await normal_list[0].getProperty('href')).jsonValue()
    await normal_list[0].click()
    await page.waitFor(random.randint(1500, 2000) - 50)
    await page.waitFor('div.basic-wrap')
    baseinfo = await page.xpath('//div[@class="basic-wrap"]')
    # print(baseinfo)
    for num in baseinfo:
        baseinfoda = await (await num.getProperty('innerHTML')).jsonValue()
        basehtmldata = etree.HTML(baseinfoda)
        ddk = basehtmldata.xpath("//div[@class='d']//text()")
        ddv = basehtmldata.xpath("//div[@class='v']//text()")
        # remove null
        for ddvit in ddv:
            if ddvit == ' ':
                ddv.remove(ddvit)

        for i in range(len(ddk)):
            datare[ddk[i].replace('\n', '').replace('\r', '').replace(' ', '')] = ddv[i].replace('\n', '').replace('\r',
                                                                                                                   '').replace(
                ' ', '')

    datare['url'] = url
    #
    contactinfos = []
    divcontactinfo = await page.xpath('//div[@class="contact-info-wrap"]//a')
    for divcontas in divcontactinfo:
        contas = await (await divcontas.getProperty('innerHTML')).jsonValue()
        print(contas)
        contactinfos.append(contas)

    datare['contactinfo'] = contactinfos

    await page.waitFor(5000)
    await page.close()
    await page.waitFor(2000)
    await browser.close()

    return datare


def headless():
    return True
    # return False


def datafolder():
    return 'spider'
    # return '/home/ubuntu/spider/chrome/data'


async def extractInv(htmltxt):
    soup = BeautifulSoup(htmltxt, "lxml")
    tablehead = soup.table.tbody.tr.find_all("th", recursive=False)
    tabletr = soup.table.tbody.find_all("tr", recursive=False)

    headarray = []
    for ahead in tablehead:
        for span in ahead('div'):
            span.decompose()
        headarray.append(ahead.get_text().replace("查看最终受益人>", "").replace('\n', '').replace('\r', '').replace(' ', ''))

    clorow = []
    for table in tabletr:
        ss = table.find_all('td', recursive=False)
        tdd = []
        for ssi in ss:
            name = ssi.find_all('h3')
            maxl = len(name)
            realname = ''
            if maxl > 0:
                realname = name[0].get_text()
            else:
                realname = ssi.get_text()

            realname = realname.replace('持股详情>', '').replace('股权链>', '').replace('\n', '').replace('\r', '').replace(
                ' ', '')
            tdd.append(realname)

        if len(tdd) > 0:
            clorow.append(tdd)

    ppp = pd.DataFrame(columns=headarray, data=clorow)

    return ppp


async def extractBTNTouz(htmltxt):
    soup = BeautifulSoup(htmltxt, "lxml")
    tablehead = soup.find_all("a", class_='btn-touzi')

    result = []
    for ahead in tablehead:
        item = {}
        item["text"] = ahead.get_text()
        item["who"] = ahead['onclick']
        result.append(item)

    return result


async def getCurinfo(url):
    print('getCurinfo')
    datare = {}
    # browserinfo = await launch(headless=headless(), userDataDir=datafolder(), args=['--disable-infobars'])
    browserinfo = await launch()
    urlcrun = url.replace('https://m.qcc.com/', 'https://www.qcc.com/')
    print(urlcrun)
    pagenew = await browserinfo.newPage()
    # width, height = screen_size()
    # 最大化窗口
    # await pagenew.emulate(iPhone())
    await pagenew.setViewport({
        "width": 1440,
        "height": 900
    })
    # 设置浏览器
    await pagenew.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 11_9_2) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')
    await pagenew.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await pagenew.setJavaScriptEnabled(False)
    await pagenew.goto(urlcrun, {'timeout': 30000})
    await pagenew.waitFor(random.randint(5000, 8000))

    tagsxp = await pagenew.xpath("//div[contains(@class,'tags')]//span[contains(@class,'ntag')]")
    ntags = []
    await pagenew.waitFor(1000)
    for tagp in tagsxp:
        tagshtml = await (await tagp.getProperty('innerHTML')).jsonValue()
        ortitle = await (await tagp.getProperty('outerHTML')).jsonValue()
        ntags.append(tagshtml)
        ntags.append(ortitle)
        # print(tagshtml)
    datare['tags'] = ntags

    # head
    headnavs = await pagenew.xpath('//div[contains(@class,"company-nav")]//a[@class="company-nav-head"]')
    for headnav in headnavs:
        baseinfoda = await (await headnav.getProperty('innerHTML')).jsonValue()
        basehtmldata = etree.HTML(baseinfoda)
        headname = basehtmldata.xpath("//h2/text()")
        headnamevava = basehtmldata.xpath("//span/text()")
        datare[headname[0].replace('\n', '').replace('\r', '')] = headnamevava[0].replace('\n', '').replace('\r', '')

    crunbasea = await pagenew.xpath(
        '//div[contains(@class,"company-nav")]/div[contains(@class,"company-nav-tab")]/div[@class="company-nav-items"]/a')
    for curuna in crunbasea:
        baseinfoda = await (await curuna.getProperty('innerHTML')).jsonValue()
        basehtmldata = etree.HTML(baseinfoda)
        etreehtmlname = basehtmldata.xpath("//text()")
        etreehtmlvalue = basehtmldata.xpath("//span")

        etreehtmlname = etreehtmlname[0].replace('\n', '').replace('\r', '').replace(' ', '')
        # etreehtmlvalue = etreehtmlname[1].replace('\n', '').replace('\r', '').replace(' ', '')

        va = "0"
        if etreehtmlvalue[0].text != None:
            va = etreehtmlvalue[0].text.replace('\n', '').replace('\r', '').replace(' ', '')

        datare[etreehtmlname] = va

    crunbasespan = await pagenew.xpath(
        '//div[contains(@class,"company-nav")]/div[contains(@class,"company-nav-tab")]/div[@class="company-nav-items"]/span')
    for curuna in crunbasespan:
        baseinfodas = await (await curuna.getProperty('innerHTML')).jsonValue()
        basehtmldata = etree.HTML(baseinfodas)
        etreehtmlname = basehtmldata.xpath("//text()")
        etreehtmlvalue = basehtmldata.xpath("//span/text()")

        etreehtmlname = etreehtmlname[0].replace('\n', '').replace('\r', '').replace(' ', '')
        etreehtmlvalue = "0"

        datare[etreehtmlname] = etreehtmlvalue

    await pagenew.waitFor(2000)

    ntables = await pagenew.xpath('//table[contains(@class,"npth")]')
    istep = 0
    for ntable in ntables:
        nhtmls = await (await ntable.getProperty('outerHTML')).jsonValue()
        investinfo = await extractInv(nhtmls)
        investtouzi = await extractBTNTouz(nhtmls)
        datare['invest_' + str(istep) + "_tdntouzi"] = investtouzi
        datare['invest_' + str(istep)] = investinfo.to_dict()
        istep = istep + 1

    await pagenew.waitFor(2000)
    await pagenew.close()
    await browserinfo.close()

    return datare


async def getQichacha(keyword):
    print('getQichacha')
    baseinfo = await getBaseinfo(keyword)
    url = baseinfo['url']
    print('baseinfo')
    print(baseinfo)
    curinfo = await getCurinfo(url)
    print('curinfo')
    print(curinfo)
    alldata = dict(baseinfo, **curinfo)
    return alldata

async def crawlmain(argvname):
    if len(argvname) > 0:
        cname = argvname
        #conn = create_engine('mysql+pymysql://opsql:123.com@localhost:3306/opsql?charset=utf8')
        conn = create_engine('mysql+pymysql://woodpecker:woodpecker@101.200.178.67:3306/woodpecker?charset=utf8')

        print(cname)
        resultcount = pd.read_sql('select count(1) as numbercount from auditsql_comp_spider where cname="' + cname + '" ', conn)
        if (resultcount.numbercount[0] == 1):
            print('公司数据存在')
        else:
            print('公司数据不存在')
            resdata = await getQichacha(cname)
            # dict to json
            datajson = json.dumps(resdata)
            metadata = MetaData(conn)
            # 连接数据表
            companytable = Table('auditsql_comp_spider', metadata, autoload=True)
            conn = conn.connect()
            # 执行语句
            result = conn.execute(companytable.insert(),{'cname':cname,'data':datajson})
            print('爬虫结束')
            print(result)
'''           
async def crawlData(name):
    if len(name) > 0:
        cname = name

        #检查是否存在

        resdata = await getQichacha(cname)
        # dict to json
        datajson = json.dumps(resdata)
        print('爬虫结束', datajson)
        return datajson


'''           
# async def crawmain

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#
#     names = ['北京顺智信科技有限公司', '北京宝贵石艺科技有限公司', '中新科技集团股份有限公司']
#     for item in names:
#         try:
#             loop.run_until_complete(crawlData(item))
#         except Exception as e:
#             print('error:%s' % e)
#
#
#     loop.close()
