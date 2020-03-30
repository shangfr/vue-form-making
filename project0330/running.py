# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 15:18:53 2020

@author: ShangFR

import os
os.chdir("C:\\Users\\ShangFR\\Desktop\\vue-form-making\\project0330")   #修改当前工作目录
os.getcwd()
"""
import time
import math
import asyncio
import json
import pandas as pd

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Date, Integer, String, ForeignKey

from api.crawling import crawlmain
from api.datafilter import filter_l,find_industry
from api.modelpre import model_p
          
#os.environ['CORENLP_HOME']='/home/ubuntu/spider/chrome/corenlp/stanford-corenlp-full-2018-10-05'
conn = create_engine('mysql+pymysql://woodpecker:woodpecker@101.200.178.67:3306/woodpecker?charset=utf8')
print("[INFO] %s已启动，开始扫描数据库! "%time.strftime('%y/%m/%d %H:%M:%S'))

metadata = MetaData(conn)
customertab= Table('customer', metadata,
                    Column('customer_id', Integer),
                    Column('reg_time',Integer),
                    Column('registered_capital',Integer),
                    Column('old_report', String(2048)),
                    Column('company_type', String(64)),
                    Column('industry', String(64)),
                    Column('tel', String(64)),
                    Column('status',Integer),
                    )
          
customertable = Table('customer_model', metadata, autoload=True)
    
    # In[1]:
def do_main(task_row):

    row = task_row
    task_id = row['task_id']
    customer_id_str = row['customer_id_str']
    model_id_str = row['model_id_str']

    customer_id_l = json.loads(customer_id_str)
    for cudid in customer_id_l:
        #cudid=23
        resultcus = pd.read_sql('select customer_id,status,customer_name from customer where customer_id="' + str(cudid) + '" ', conn)
        if len(resultcus)==1:
            customer_id = resultcus['customer_id'][0]
            customer_name = resultcus['customer_name'][0]
            print(customer_id,customer_name)
            try:
                asyncio.get_event_loop().run_until_complete(crawlmain(customer_name))
            except:
                print("[INFO] 爬虫 %s执行失败! "%str(customer_name))
                updatsql = customertab.update().where(customertab.c.customer_id == customer_id).values(status=2)
                conn.execute(updatsql)
                #customer_name = '北京金泰尚美家具有限公司'
            print('载入企业json数据')
            resultlist = pd.read_sql('select data as datajson from auditsql_comp_spider where cname="' + customer_name + '" ',conn)
            x = resultlist.datajson.iloc[0]
            x = x.replace('999+', '999')
            jsondict = json.loads(x)
            jsondict,reg_date,reg_capital,leixing,contactinfoss = filter_l(jsondict)
            company_industry = find_industry(customer_name)
            ##################################
            #更新customer表 行业基本信息
            jsonstr = {"desc":'desc',"w50":'',"w5":'',"renshu":'',"fengxian":'',"guoji":''}
            updatsql = customertab.update().where(customertab.c.customer_id == customer_id)\
                .values(reg_time=reg_date, old_report=json.dumps(jsonstr), status=1,industry=company_industry,registered_capital=reg_capital, company_type=leixing,tel=contactinfoss)
            conn.execute(updatsql)
            print('完成customer表更新-行业基本信息')
            ##################################
            #更新customer_model表 模型判断信息

            # model_id = 1     
            maypre,parameter,suggest_model1,jsondict = model_p(jsondict)
            grade = 0
            if maypre >= 80:
                grade = 1
            elif maypre >= 60:
                grade = 2
            elif maypre >= 40:
                grade = 3
            else:
                grade = 4
                
            
            # model_id = 2
            
            if maypre >= 10:
                suggest_model2 = '该公司具备5万存款能力'
            else:
                suggest_model2 = '该公司不具备5万存款能力'
            
            # model_id = 3
            if jsondict.get('参保人数'): 
                sbre = jsondict['参保人数']
            else:
                sbre = '0'
            
            suggest_model3 = ''
                
            renyuanstrj = ""
            if sbre == "-":
                sbre = 0
            if int(sbre) <= 10:
                renyuanstrj = '人员规模：该公司人员规模较少；'
            if int(sbre) > 10 and int(sbre) <= 100:
                renyuanstrj = '人员规模：该公司人员规模中等，建议开展人数规模相关营销活动；'
                
            if int(sbre) > 100:
                renyuanstrj = '人员规模：该公司人员规模较多，强烈建议开展人数规模相关营销活动；'
            suggest_model3 = renyuanstrj
            score_model3 = int(sbre)

            # model_id = 4
            inexport = []
            if jsondict.get('进出口企业代码'): 
                falv2 = jsondict['进出口企业代码']
                if falv2 != '-':
                    inexport.append('进出口-进出口企业代码')

            if jsondict.get('经营范围'): 
                falv3 = jsondict['经营范围']
                if falv3.find('进出口') >= 0:
                    inexport.append("进出口")
    
                if customer_name.find('进出口') >= 0:
                    inexport.append('进出口-名称')
    
                if customer_name.find('国际') >= 0:
                    inexport.append('进出口-国际')
    
                if customer_name.find('中国') >= 0:
                    inexport.append('进出口-中国')
            else:
                falv3 = '-'           
            
            if 'invest_0' in jsondict:
                falv4 = jsondict['invest_0']
                falv4 = json.dumps(falv4, ensure_ascii=False)
                if falv4.find('进出口') >= 0:
                    inexport.append('进出口-名称-股东')
    
                if falv4.find('国际') >= 0:
                    inexport.append('进出口-国际-股东')
    
                if falv4.find('中国') >= 0:
                    inexport.append('进出口-中国-股东')
            else:
                falv4 = ''
                
            if 'invest_1' in jsondict:
                falv5 = jsondict['invest_1']
                falv5 = json.dumps(falv5, ensure_ascii=False)
                if falv5.find('进出口') >= 0:
                    inexport.append('进出口-名称-投资')
    
                if falv5.find('国际') >= 0:
                    inexport.append('进出口-国际-投资')
    
                if falv5.find('中国') >= 0:
                    inexport.append('进出口-中国-投资')
            else:
                falv5 = ''
          
            jck = len(inexport)
            if jck > 0:
                jck = 1
                
            jckppstr = []
            if jck == 1:
                for ipo in inexport:
                    if ipo.find("投资") >= 0:
                        jckppstr.append("【投资的企业的经营业务范围】")
                    if ipo.find("股东") >= 0:
                        jckppstr.append("【股东经营业务范围】")
                    else:
                        jckppstr.append("【经营业务范围】")  
                        
            jckstrj = ""
            if jck == 1:
                jckstrj = "国际业务：参考该公司" + (
                    ",".join(jckppstr)) + "等信息，其开展国际业务的可能性较高，建议开展国际业务相关营销活动；"
            else:
                jckstrj = "国际业务：该公司国际业务可能性偏低；"

            suggest_model4 = jckstrj
            score_model4 = jck
            
            
            # model_id = 5
            datainiiiisp = []
            if jsondict.get('tags'):
                kget = jsondict['tags']
                kgetstr = "".join(list(map(str, kget)))
                if kgetstr.find('失信') >= 0:
                    datainiiiisp.append("失信")
                    kget = 1
                if kgetstr.find('注销') >= 0:
                    datainiiiisp.append("注销")
                if kgetstr.find('经营异常') >= 0:
                    datainiiiisp.append("经营异常")
                if kgetstr.find('吊销') >= 0:
                    datainiiiisp.append("吊销")
                else:
                    kget = 0
            if jsondict.get('法律诉讼'):            
                falv = jsondict['法律诉讼']
                if int(falv) > 0:
                    datainiiiisp.append("法律诉讼")

            allv = 1
            falvfengxianstr = []
            if len(datainiiiisp) > 0:
                if '注销' in datainiiiisp or '吊销' in datainiiiisp:
                    allv = allv + 60
                    falvfengxianstr.append("【注销】")

                if '失信' in datainiiiisp:
                    allv = allv + 20
                    falvfengxianstr.append("【失信人】")

                if '经营异常' in datainiiiisp:
                    allv = allv + 5
                    falvfengxianstr.append("【经营异常】")

                if '法律诉讼' in datainiiiisp:
                    allv = allv + 15
                    falvfengxianstr.append("【法律诉讼】")
    
            fengxian = round(math.log(allv, 100) * 100)

            fengxianstrjj = ''
            if fengxian >= 0 and fengxian <= 40:
                fengxianstrjj = "行政法务风险：该公司行政法务风险偏低，基本无违法现象；"
            if fengxian > 40 and fengxian <= 70:
                fengxianstrjj = "行政法务风险：该公司行政法务风险偏中，可能存在少量" + (",".join(falvfengxianstr)) + "行为；"
            if fengxian > 70:
                fengxianstrjj = "行政法务风险：该公司行政法务风险偏高，可能存在" + (",".join(falvfengxianstr)) + "风险；"
            suggest_model5 = fengxianstrjj
            
            score_model1 = maypre
            if maypre > 50:
                score_model2 = maypre+(100-maypre)*0.5
            elif maypre > 0:
                score_model2 = maypre+(100-maypre)*0.2
            else:
                score_model2 = 0
            score_model5 = fengxian
            
            if score_model1 > 99.99:
                score_model1 = 99.99
            if score_model2 > 99.99:
                score_model2 = 99.99       
                
            suggest_dict = {'1': suggest_model1, '2': suggest_model2, '3': suggest_model3, '4': suggest_model4, '5': suggest_model5}
            score_dict = {'1': score_model1, '2': score_model2, '3': score_model3, '4': score_model4, '5': score_model5}



            model_id_l = json.loads(model_id_str)


            for mid in model_id_l:
                model_id = str(mid)
                suggest = suggest_dict[model_id]
                score = score_dict[model_id]
                print(model_id)
                #插入customer_model
                # 连接数据表
                conn.connect()
                updatsql = customertable.update().where(customertable.c.customer_id == customer_id).where(customertable.c.model_id == model_id).values({'customer_id':str(customer_id),'model_id':model_id,'score':str(round(score,2)),'add_time':int(time.time()),'parameter':parameter,'suggest':suggest,'grade':str(grade)})
                conn.execute(updatsql).rowcount
                #updatsql = customertable.update().where(customer_id == task_id).values(status=1)
                #conn.execute(customertable.insert(),{'customer_id':str(customer_id),'model_id':model_id,'score':str(maypre),'add_time':int(time.time()),'parameter':parameter,'suggest':suggest,'grade':str(grade)})

    #更细task 表数据
    #task
    updatesql = "update task set status=1 where task_id = "+str(task_id)
    #updatsql = customertab.update().where(tasktab.c.task_id == task_id).values(status=1)
    conn.execute(updatesql).rowcount
    print('[INFO] 任务已完成')

    # In[2]:
if __name__ == '__main__':

    while True:
        process_info = pd.read_sql('select task_id,customer_id_str,model_id_str from task where status=0 order by add_time asc ', conn)
        if len(process_info) > 0:
            print('[INFO] %s开始执行主程序'%time.strftime('%y/%m/%d %H:%M:%S'))
            try:
                #result = pd.read_sql('select task_id,customer_id_str,model_id_str from task where status=0 order by add_time asc ', conn)
                for index, row in process_info.iterrows():
                    task_id = row['task_id']
                    do_main(row)
            except:
                #更细task 表数据
                #task
                updatesql = "update task set status=2 where task_id = "+str(task_id)
                conn.execute(updatesql)
                print("[INFO] task_id %s执行失败! "%str(task_id))
                time.sleep(2)
        else:
            time.sleep(5)
            pass