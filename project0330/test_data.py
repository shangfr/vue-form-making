# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:48:27 2020

@author: ShangFR
"""
import os
os.chdir("E:\\opt\\deposit_model")   #修改当前工作目录
os.getcwd()

import time, datetime
import os
import math
import asyncio
import random
import json
import pandas as pd
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Date, Integer, String, ForeignKey
from crawling import crawlmain
import re
import joblib
import numpy as np
import pandas as pd 
import lime.lime_tabular
from api.woebin import woebin_ply

                
#os.environ['CORENLP_HOME']='/home/ubuntu/spider/chrome/corenlp/stanford-corenlp-full-2018-10-05'
conn = create_engine('mysql+pymysql://woodpecker:woodpecker@101.200.178.67:3306/woodpecker?charset=utf8')
print("[INFO] %s已启动，开始扫描数据库! "%time.strftime('%y/%m/%d %H:%M:%S'))

customer_name = '阿里巴巴'
asyncio.get_event_loop().run_until_complete(crawlmain(customer_name))

customer_name = '腾讯科技'
print('载入企业json数据')


resultlist = pd.read_sql('select data as datajson from spider where cname="' + customer_name + '" ',conn)
x = resultlist.datajson.iloc[0]
#x = deposit_data.iloc[2450,1]
jsondict = json.loads(x)

v_list = []           
                        
for i in range(len(deposit_data)):
    x = deposit_data.iloc[i,1]
    jsondict = json.loads(x)
    v_list.extend(list(jsondict.keys()))


v_df = pd.DataFrame(v_list,columns=['var'])


c_df = v_df['var'].value_counts()

alist = ['invest_0','invest_1','tags','contactinfo']

blist = c_df[c_df<2100].index

alist.extend(blist)



def filter_l(jsondict):
    return {k: v for k, v in jsondict.items() if k not in alist}

deposit_data['newdict']=''
for i in range(len(deposit_data)):
    x = deposit_data.iloc[i,1]
    jsondict = json.loads(x)
    
    if 'invest_1' in jsondict:
        jsondict['对外投资'] = str(len(jsondict['invest_1']['序号']))
    else:
        jsondict['对外投资'] = '0'
    
    if 'contactinfo' in jsondict:
        contactinfo = jsondict['contactinfo']
        if len(contactinfo) > 0:
            jsondict['电话'] = str(contactinfo[0])
        else:
            jsondict['电话'] = ''
    else:
        jsondict['电话'] = ''
    
    if jsondict.get('tags'):
        getinfo = jsondict['tags']
        getinfostr = "".join(list(map(str, getinfo)))
        if getinfostr.find('高新技术企业') >= 0:
            jsondict['高新认证'] = '1'
        else:
            jsondict['高新认证'] = '0'
    else:
        jsondict['高新认证'] ='0'

    if jsondict.get('所属行业'): 
        hangye = jsondict['所属行业']               
        if hangye.find('公司') >= 0:
            fangshi = jsondict['经营方式']             
            hangye = jsondict['经营范围']
            jsondict['经营范围'] = fangshi
            jsondict['所属行业'] = hangye
    newdict = filter_l(jsondict)       
    deposit_data.iloc[i,2] = json.dumps(newdict)



plist = ['对外投资','电话','高新认证']

qlist = c_df[c_df>2100].index

plist.extend(qlist)
plist.remove('tags')
plist.remove('contactinfo')
plist.remove('invest_0')

newdf = pd.DataFrame(index=range(2571),columns=plist)
newdf.to_csv('C:\\Users\\ShangFR\\Desktop\\cm_info.csv',index=False)
cm_info = pd.read_csv("C:\\Users\\ShangFR\\Desktop\\cm_info.csv", encoding='utf8')





for i in range(len(deposit_data)):
    print(deposit_data.company[i])
    newdf.loc[i,'企业名称']=deposit_data.company[i]
    x = deposit_data.iloc[i,2]
    jsondict = json.loads(x)
    for p in plist:
        if jsondict.get(p): 
            newdf.loc[i,p] = jsondict[p]
    
json.loads(deposit_data.iloc[i,2])

df = pd.DataFrame.from_dict(newdict, orient='index', columns=[deposit_data['company'][i]]) 

if jsondict.get('成立日期'): 
    reg_date = jsondict['成立日期']
    reg_date = int(reg_date.replace('-', ''))
    jsondict['成立时长'] = (pd.to_datetime(time.strftime("%Y-%m-%d"))-pd.to_datetime(jsondict['成立日期'])).days
    jsondict['成立时长'] = round(jsondict['成立时长']/365)
else:
    jsondict['成立时长'] = 0
    reg_date = 0


if jsondict.get('注册资本'): 
    if jsondict['注册资本'] != '-':
        jsondict['注册资本'] = float(jsondict['注册资本'].replace('万元人民币', '').replace("万美元", '').replace("万澳大利亚元", ''))
        reg_capital = int(jsondict['注册资本'])
else:
    jsondict['注册资本'] = 0
    reg_capital = 0



# print(jsondict)
if jsondict.get('所属行业'): 
    hangye = jsondict['所属行业']
    
    if hangye.find('公司') >= 0:
        fangshi = jsondict['经营方式']             
        hangye = jsondict['经营范围']
        jsondict['经营范围'] = fangshi
else:
    hangye = '其他'


if '企业类型' in jsondict:
    leixing = jsondict['企业类型']
else:
    leixing = '其他'





if jsondict.get('相关公告'): 
    jsondict['公告研报'] = jsondict['相关公告']
else:
    jsondict['公告研报'] = 0


if jsondict.get('实缴资本'): 
    if jsondict['实缴资本'] == '-':
        jsondict['实缴资本'] = 0
    else:
        jsondict['实缴资本'] = float(jsondict['实缴资本'].replace('万元人民币', '').replace("万美元", '').replace("万澳大利亚元", ''))
else:
    jsondict['实缴资本'] = 0


maypre = 85.21




aList = [123, 'xyz', 'zara', 'abc'];
aList










