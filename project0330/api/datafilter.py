# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:43:42 2020

@author: ShangFR
"""

import time
import pandas as pd
def filter_l(jsondict):
    if jsondict.get('成立日期'): 
        if jsondict['成立日期'] != '-':
            reg_date = jsondict['成立日期']
            reg_date = int(reg_date.replace('-', ''))
            jsondict['成立时长'] = (pd.to_datetime(time.strftime("%Y-%m-%d"))-pd.to_datetime(jsondict['成立日期'])).days
            jsondict['成立时长'] = round(jsondict['成立时长']/365)
        else:
            jsondict['成立日期'] = 0
            jsondict['成立时长'] = 0
            reg_date = 0
    
    if jsondict.get('注册资本'): 
        if jsondict['注册资本'] != '-':
            jsondict['注册资本'] = float(jsondict['注册资本'].replace('万元人民币', '').replace("万美元", '').replace("万澳大利亚元", ''))
            reg_capital = int(jsondict['注册资本'])
    else:
        jsondict['注册资本'] = 0
        reg_capital = 0
    
        
    if 'invest_1' in jsondict:
        jsondict['对外投资'] = str(len(jsondict['invest_1']['序号']))
    elif 'invest_0' in jsondict:
        jsondict['对外投资'] = str(len(jsondict['invest_0']['序号']))                
    else:
        jsondict['对外投资'] = '0'
    
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
    
                
    if 'contactinfo' in jsondict:
        contactinfo = jsondict['contactinfo']
        if len(contactinfo) > 0:
            contactinfoss = str(contactinfo[0])
        else:
            contactinfoss = '-'
    else:
        contactinfoss = '-'
    
    return jsondict,reg_date,reg_capital,leixing,contactinfoss


def find_industry(customer_name):   
    company_industry = ''
    mapdict = {
            "科技":["科技","信息技术","网络","技术","信息系统","软件","通信","计算机系统","数据","信息服务"],
            "投资":["投资","资产","财富","资本","基金","控股","金融"],
            "金融":["融资租赁","保险","担保","商业保理"],        
            "咨询":["咨询","顾问"],
            "房地产":["地产","置业","物业"],
            "能源":["电力","核能","矿业","电气","石油","能源","燃气","燃料","太阳能"],
            "教育":["教育"],
            "餐饮":["餐饮","饭店"],
            "实业":["实业"],
            "文化":["文化","广告","传媒","影业","体育","杂志","俱乐部","艺术","影视"],
            "医疗卫生":["医疗器械","药房","医学","医院","门诊","诊所","生物医药","医药","中医","养老","医疗","生物科技"],
            "生物医药":["医疗器械","药房","医学","医院","门诊","诊所","生物医药","医药","中医","养老","医疗","生物科技"],
            "建筑工程":["园林","环保","市政","工程开发","工程监理","建筑","装饰","建设","工程管理","安装工程"],
            "居民服务":["清洁","养老","殡葬","保洁","美容","美发","保安","健身","修理","汽车服务","殡仪","摄影","数码快印","印刷设计","开锁","清洗","图文设计","图文制作","商店","经营部","健康管理"],
            "制造业":["门窗","酒业","厂","制造","光电","数控机械","贵金属","服装","服饰","石材"],
            "酒店":["酒店","宾馆","旅店","招待所"],
            "交通运输":["停车场","物流","出租汽车","货运","运输服务"],
            "租赁":["设备租赁","汽车租赁"],
            "航空":["民航"],
            "拍卖典当":["拍卖","典当"],
            "批发零售":["贸易","商贸","电子","进出口","超市","销售","经贸","器材","科贸","电子商务"],
            "商业服务":["事务所","翻译","会计","知识产权","办公服务","会议服务","策划","人力资源","会展服务","展览","公关","供应链","商业管理","企业管理","商业服务"],
            "农业":["农业","生态"],
            "社会组织":["委员会"]
            }
    
    for (key,value) in mapdict.items():    
        for word in value:
            if customer_name.find(word) != -1:
                company_industry = key
                print(key)
                break
        else:
            continue
        break
    return company_industry
