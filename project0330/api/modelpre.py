# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 17:11:56 2020

@author: ShangFR
"""

import re
import joblib
import numpy as np
import pandas as pd 
import lime.lime_tabular
from api.woebin import woebin_ply

my_bins = pd.read_csv('data_out/bins_df_a.csv')
my_model = joblib.load('newmodel/model__a.pkl')
cols_m = np.load('newmodel/cols_m_a.npy', allow_pickle=True)

bins_dict = {}
cols = my_bins['variable'].unique().tolist()
for col in cols:
    bins_dict[col] = my_bins[my_bins['variable'] == col]      

def model_p(jsondict):
    predict_data = pd.DataFrame(columns=cols)    
    if jsondict.get('tags'):
        getinfo = jsondict['tags']
        getinfostr = "".join(list(map(str, getinfo)))
        if getinfostr.find('高新技术企业') >= 0:
            jsondict['是否高新技术认证'] = 1
        else:
            jsondict['是否高新技术认证'] = 0
    else:
        jsondict['是否高新技术认证'] = 0
        
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
               
    test_dict = {}
    for col in cols:
        if jsondict.get(col):
            pass
        else:
            jsondict[col] = "0"
        test_dict[col] = jsondict[col]
           
    for col in cols: 
        if jsondict[col] == "-":
            jsondict[col] = "0"
        if col != '登记状态':
            predict_data.loc[0,col] = jsondict[col]
            predict_data[col] = predict_data[col].astype("int")
        else:
            predict_data.loc[0,col] = jsondict[col]

    predict_data.loc[predict_data['税务信用']>0,'税务信用'] = 1            
    #predict_data.loc[predict_data['实缴资本']>0,'实缴资本'] = 1
    
    predict_data.loc[0,'登记状态'] = jsondict['登记状态']
    #predict_data.dtypes
    reg_status = ['注销','吊销','迁出','停业','清算']
    suggest_model1 = ''
    parameter = ''
    if predict_data['登记状态'].isin(reg_status)[0]:
        maypre = 0
        gailvstr = '50万存款：该公司已注销，50万存款概率偏低；'
        parameter = '[{"name":"登记状态","score":0,"intro":"该公司已注销"}]'
    else:
        predict_woe = woebin_ply(predict_data[cols], bins_dict)
        predict_woe = predict_woe[cols_m]
        predict_woe.fillna(0,inplace=True)
        maypre = my_model.predict_proba(predict_woe)[:,1][0]
        maypre = round(maypre*100,2)

        # 评分调整

        if jsondict.get('严重违法'): 
            if jsondict['严重违法'] != '0':
                maypre = maypre*0.8

        if jsondict.get('行政处罚'): 
            if jsondict['行政处罚'] != '0':
                maypre = maypre*0.9

        if jsondict.get('失信信息'): 
            if jsondict['失信信息'] != '0':
                maypre = maypre*0.8
                
        if jsondict.get('分支机构'):
            if (jsondict['分支机构']!='-') & (jsondict['分支机构']!=''):
                if int(jsondict['分支机构']) > 1:
                    maypre = maypre + (100-maypre)*0.5
                elif int(jsondict['分支机构']) > 0:
                    maypre = maypre + (100-maypre)*0.2
                else:
                    pass
        
        
        if jsondict.get('对外投资'):
            if (jsondict['对外投资']!='-') & (jsondict['对外投资']!=''):
                if int(jsondict['对外投资']) > 1:
                    maypre = maypre + (100-maypre)*0.5
                elif int(jsondict['对外投资']) > 0:
                    maypre = maypre + (100-maypre)*0.2
                else:
                    pass
                
        if jsondict.get('企业业务'): 
            if jsondict['企业业务'] != '0':
                maypre = maypre + (100-maypre)*0.1

        if jsondict.get('实缴资本'): 
            if jsondict['实缴资本'] != 0:
                maypre = maypre + (100-maypre)*0.5

        if jsondict.get('是否高新技术认证'): 
            if jsondict['是否高新技术认证'] != 0:
                maypre = maypre + (100-maypre)*0.1
                
        if jsondict.get('作品著作权'): 
            mando = int(jsondict['作品著作权'])
            if mando > 4:
                maypre =  maypre + (100-maypre)*0.5
            elif mando > 0:
                maypre =  maypre + (100-maypre)*0.3
            else:
                pass

        if jsondict.get('供应商'): 
            mando = int(jsondict['供应商'])
            if mando > 3:
                maypre =  maypre + (100-maypre)*0.3
            elif mando > 0:
                maypre =  maypre + (100-maypre)*0.1
            else:
                pass

        if jsondict.get('分支机构'): 
            mando = int(jsondict['分支机构'])
            if mando > 10:
                maypre =  maypre + (100-maypre)*0.3
            elif mando > 0:
                maypre =  maypre + (100-maypre)*0.1
            else:
                pass

        if jsondict.get('客户'): 
            mando = int(jsondict['客户'])
            if mando > 3:
                maypre =  maypre + (100-maypre)*0.3
            elif mando > 0:
                maypre =  maypre + (100-maypre)*0.1
            else:
                pass

        if jsondict.get('税务信用'): 
            mando = int(jsondict['税务信用'])
            if mando > 0:
                maypre =  maypre + (100-maypre)*0.03
            else:
                pass

        if jsondict.get('知识产权'): 
            mando = int(jsondict['知识产权'])
            if mando > 10:
                maypre =  maypre + (100-maypre)*0.5
            elif mando > 2:
                maypre =  maypre + (100-maypre)*0.3
            else:
                pass
            
        if jsondict.get('参保人数'):
            if (jsondict['参保人数']!='-') & (jsondict['参保人数']!=''):
                if int(jsondict['参保人数']) > 200:
                    maypre = maypre + (100-maypre)*0.9
                elif int(jsondict['参保人数']) > 150:
                    maypre = maypre + (100-maypre)*0.8
                elif int(jsondict['参保人数']) > 100:
                    maypre = maypre + (100-maypre)*0.7
                elif int(jsondict['参保人数']) > 50:
                    maypre = maypre + (100-maypre)*0.6
                else:
                    pass

        if jsondict.get('企业类型'):
            qylxstr = jsondict['企业类型']
            if qylxstr.find('国有')>0:
                maypre = maypre + (100-maypre)*0.5
            elif qylxstr.find('公有'):
                maypre = maypre + (100-maypre)*0.5
            elif qylxstr.find('集体'):
                maypre = maypre + (100-maypre)*0.3
            else:
                pass
                
        if jsondict.get('限制高消费'): 
            if jsondict['限制高消费'] != '0':
                maypre = maypre*0.9
                
        if jsondict.get('黑名单'): 
            if jsondict['黑名单'] != '0':
                maypre = maypre*0.8

        if jsondict.get('资产负债表'): 
            maypre = 99.99
            
        if jsondict.get('上市信息'): 
            maypre = 99.99


            
        #模型解释
   
        desc_dict = {}
        desc_dict['所属行业'] = '考察企业所属行业竞争力。'
        desc_dict['扩展属性'] = '考察企业自身扩展属性，上市公司，高新技术企业,注销等信息。'
        desc_dict['人数规模'] = '考察企业当前人数规模。'
        desc_dict['税务信用'] = '考察企业税务信息，及税务等级。'
        desc_dict['新闻舆情'] = '考察企业网络舆情信息，正面、负面及数量。'
        desc_dict['招聘'] = '考察企业在各大招聘网站招聘情况。'
        desc_dict['对外投资'] = '考察企业对外投资情况。'
        desc_dict['商标信息'] = '考察企业知识产权相关，商标信息情况。'
        desc_dict['专利信息'] = '考察企业知识产权相关，专利信息。'
        desc_dict['证书信息'] = '考察企业知识产权相关，证书信息。'
        desc_dict['作品著作权'] = '考察企业知识产权相关，作品著作权。'
        desc_dict['软件著作权'] = '考察企业知识产权相关，软件著作权。'
        desc_dict['法律诉讼'] = '考察企业法律诉及案件情况。'
        desc_dict['主要人员'] = '考察企业管理人员情况。'
        desc_dict['股东数量'] = '考察企业股东情况。'
        desc_dict['机构股东'] = '考察企业机构股东情况。'
        desc_dict['个人股东'] = '考察企业个人股东情况。'
        desc_dict['知名机构股东'] = '考察企业是否具有知名机构股东。'
        desc_dict['风险'] = '考察企业具体风险。'
        desc_dict['限制高消费'] = '考察企业股东限制高消费情况。'
        desc_dict['失信信息'] = '考察企业股东失信信息情况。'
        desc_dict['终本案件'] = '考察企业股东终本案件情况。'  
        desc_dict['供应商'] = '考察企业供应商'
        desc_dict['经营状况'] = '考察企业经营状况'
        desc_dict['企业年报'] = '考察企业企业年报'
        desc_dict['融资信息'] = '考察企业融资信息'
        desc_dict['变更记录'] = '考察企业变更记录'
        desc_dict['双随机抽查'] = '考察企业双随机抽查'
        desc_dict['成立时长'] = '考察企业成立时长'
        desc_dict['最终受益人'] = '考察企业最终受益人'
        desc_dict['网站信息'] = '考察企业网站信息'
        desc_dict['招投标'] = '考察企业招投标'
        desc_dict['注册资本'] = '考察企业注册资本'
        desc_dict['行政许可'] = '考察企业行政许可'
        desc_dict['竞品信息'] = '考察企业竞品信息'
        desc_dict['经营风险'] = '考察企业经营风险'
        desc_dict['抽查检查'] = '考察企业抽查检查'
        desc_dict['客户'] = '考察企业客户'
        desc_dict['历史对外投资'] = '考察企业历史对外投资'
        desc_dict['历史股东'] = '考察企业历史股东'
        desc_dict['一般纳税人'] = '考察企业一般纳税人'
        desc_dict['控股企业'] = '考察企业控股企业'
        desc_dict['核心人员'] = '考察企业核心人员'
        desc_dict['工商自主公示'] = '考察企业工商自主公示'
        desc_dict['知识产权'] = '考察企业知识产权'
        desc_dict['企业业务'] = '考察企业企业业务'
        desc_dict['股东信息'] = '考察企业股东信息'
        desc_dict['企业发展'] = '考察企业企业发展'
        desc_dict['历史高管'] = '考察企业历史高管'
        desc_dict['是否高新技术认证'] = '考察企业是否高新技术认证'
        desc_dict['公告研报'] = '考察企业公告研报'
        desc_dict['经营异常'] = '考察企业经营异常'
        desc_dict['历史行政许可'] = '考察企业历史行政许可'
        
        X_train = pd.read_csv('data_out/X_train_a.csv', encoding='utf8')
        #y_train = pd.read_csv('data_out/y_train_a.csv', encoding='utf8')
        explainer = lime.lime_tabular.LimeTabularExplainer(X_train.values,
                                                           feature_names=X_train.columns.values.tolist(),
                                                           class_names=['Weak','Strong'])   
        
        predict_fn = lambda x: my_model.predict_proba(x).astype(float)
        exp = explainer.explain_instance(predict_woe.values[0], predict_fn, num_features=10)

        exp10 = exp.as_list()
        expdf = pd.DataFrame(exp10,columns=["name","score"])

        expdf["name"] = expdf.apply(lambda r: ''.join(re.findall('[\u4e00-\u9fa5]',r["name"])),axis=1)
        expdf["score"] = round(expdf["score"],2)
        expdf = expdf.sort_values(by=["score"], ascending=[False])
        expdf.reset_index(drop=True, inplace=True)
        
        expdf["intro"] = expdf["name"]
        expdf = expdf.replace({'intro': desc_dict})
        
        parameter = expdf.to_json(orient='records').encode('utf-8').decode('unicode_escape') 
        
        if len(exp10) > 0:
            zhengxiangstrggg = "【" +expdf["name"][0] + "】"
        else:
            zhengxiangstrggg = "***"

            
        if maypre < 60:
            gailvstr = '50万存款：该公司50万存款概率偏低；'
        if maypre >= 60 and maypre < 80:
            gailvstr = '50万存款：受该公司' + zhengxiangstrggg + '等维度影响，其50万存款概率中等，建议开展存款营销活动；'
        if maypre >= 80:
            gailvstr = '50万存款：受该公司' + zhengxiangstrggg + '等维度影响，其50万存款概率偏高，强烈建议进行存款类营销活动'
    
    suggest_model1 = gailvstr
    
    return maypre,parameter,suggest_model1,jsondict