# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 10:10:48 2020

@author: ShangFR
"""


import os
os.chdir("E:\\opt\\deposit_model")   #修改当前工作目录
os.getcwd()

import numpy as np
import pandas as pd 

from api.var_filter import var_filter
from api.split_df import split_df

from api.woebin import woebin,woebin_ply

# GBM
from sklearn.ensemble import GradientBoostingClassifier


import joblib


deposit_data = pd.read_excel("data_in\\训练集-整理后200306.xlsx", encoding='utf8')

deposit_data['成立时长'] = (pd.to_datetime('20200101')-pd.to_datetime(deposit_data['成立日期'])).dt.days
deposit_data['成立时长'] = round(deposit_data['成立时长']/365)
deposit_data.drop(['y','公司名称','成立日期'],axis=1,inplace=True)

reg_status = ['注销','吊销','停业','清算']
deposit_data = deposit_data[~deposit_data['登记状态'].isin(reg_status)]

#dframe = pd.read_excel("data_in\\变量表.xlsx")
deposit_data.columns
deposit_data = deposit_data.replace({'经营状况': {'999+': '999'}})
deposit_data['经营状况'] = deposit_data['经营状况'].astype('int32')

deposit_data['注册资本'] = deposit_data['注册资本']/10000
deposit_data['注册资本'] = deposit_data['注册资本'].astype('int32')


deposit_data.drop(['登记状态','行业'],axis=1,inplace=True)
deposit_data.fillna(0,inplace=True)



































col_in = ['成立时长','注册资本','实缴资本','行业','商标信息',
          '分支机构','控股企业','税务信用','招投标','供应商',
          '客户','融资信息','专利信息','作品著作权','网站信息',
          '新闻舆情','法律诉讼','经营状况',
          '客户反馈结果']

deposit_data = deposit_data[col_in]
deposit_data.fillna(0,inplace=True)

deposit_data.loc[deposit_data['税务信用']>0,'税务信用'] = 1
deposit_data.loc[deposit_data['实缴资本']>0,'实缴资本'] = 1
deposit_data.loc[deposit_data['商标信息']>10,'商标信息'] = 10
deposit_data.loc[deposit_data['分支机构']>1,'分支机构'] = 2
deposit_data.loc[deposit_data['控股企业']>1,'控股企业'] = 2
deposit_data.loc[deposit_data['税务信用']>1,'税务信用'] = 1
deposit_data.loc[deposit_data['招投标']>1,'招投标'] = 1
deposit_data.loc[deposit_data['供应商']>1,'供应商'] = 1
deposit_data.loc[deposit_data['客户']>1,'客户'] = 1
deposit_data.loc[deposit_data['融资信息']>2,'融资信息'] = 2
deposit_data.loc[deposit_data['专利信息']>10,'专利信息'] = 10
deposit_data.loc[deposit_data['作品著作权']>4,'招投标'] = 4
deposit_data.loc[deposit_data['网站信息']>4,'网站信息'] = 4
deposit_data.loc[deposit_data['新闻舆情']>10,'新闻舆情'] = 10

deposit_data['成立时长']=pd.cut(deposit_data['成立时长'],bins=[0,3,7,999], labels=False,include_lowest=True)
deposit_data['注册资本']=pd.cut(deposit_data['注册资本'],bins=[0,10,100,1000,5000,999999], labels=False,include_lowest=True)
deposit_data['法律诉讼']=pd.cut(deposit_data['法律诉讼'],bins=[0,20,500,99999], labels=False,include_lowest=True)

    

mapdict = {
        "科技":"科教",
        "教育":"科教",
        "金融":"金融投资",
        "投资":"金融投资",
        "餐饮":"服务业",
        "居民服务、修理和其他服务业": "服务业"
        }


deposit_data = deposit_data.replace({'行业': mapdict})

deposit_data.loc[deposit_data['行业'] != '科教','行业'] = 0
deposit_data.loc[deposit_data['行业'] == '科教','行业'] = 1


def train_model(deposit_data,mtypes):
    # filter variable via missing rate, iv, identical value rate
    # woe binning ------
    bins = woebin(deposit_data, y="客户反馈结果")
    np.save('data_out\\bins'+mtypes+'.npy',bins)
    bins_df = pd.concat(bins, ignore_index=True)
    bins_df.to_csv('data_out\\bins_df'+mtypes+'.csv', encoding='utf8',index=False)
    train, test = split_df(deposit_data, '客户反馈结果').values()
    train_woe = woebin_ply(train, bins)
    test_woe = woebin_ply(test, bins)
    y_train = train_woe.loc[:,'客户反馈结果']
    X_train = train_woe.loc[:,train_woe.columns != '客户反馈结果']
    X_train.to_csv('data_out\\X_train'+mtypes+'.csv', encoding='utf8',index=False)
    y_train.to_csv('data_out\\y_train'+mtypes+'.csv', encoding='utf8',index=False)
    
    y_test = test_woe.loc[:,'客户反馈结果']
    X_test = test_woe.loc[:,train_woe.columns != '客户反馈结果']
    
    gbm = GradientBoostingClassifier()
    gbm.fit(X_train, y_train)
    print(gbm.score(X_test, y_test)) 
    #print(xgbc.feature_importances_)
    np.save('mymodel\\cols_m'+mtypes+'.npy',X_train.columns)
    joblib.dump(gbm, 'mymodel\\model_'+mtypes+'.pkl')
    return bins,gbm



bins_0,gbm_0 = train_model(deposit_data,mtypes='324')





my_model = joblib.load('model\\model_xgbc1.pkl')

my_bins = pd.read_csv('data_out\\bins_df1.csv')


















# 通过登记状态正常0 反馈1  注册资本大 反馈0
#deposit_data = deposit_data.loc[deposit_data['是否经营状态正常'] == 1]
# 转换字符型变量

"""
deposit_data = deposit_data.replace({'进出口': {1: 'yes', 0: 'no'},
                                     '经营异常': {1: 'yes', 0: 'no',2:'yes'},
                                     '企业业务': {1: 'yes', 0: 'no'},
                                     '是否高新技术认证': {1: 'yes', 0: 'no'},
                                     '双随机抽查': {1: 'yes', 0: 'no'},
                                     '投资机构': {1: 'yes', 0: 'no'},
                                     '一般纳税人': {1: 'yes', 0: 'no',2:'yes'},
                                     '是否科技行业': {True: 'yes', False: 'no'}
                                     })


"""

deposit_data['实缴资本'].value_counts()
deposit_data['分支机构'].value_counts()
deposit_data['经营异常'].value_counts()
deposit_data['一般纳税人'].value_counts()

deposit_data['供应商'].value_counts()


deposit_data['控股企业'].value_counts()
deposit_data['税务信用'].value_counts()
deposit_data['行业'].value_counts()

deposit_data['作品著作权'].value_counts()

#deposit_data['是否科教行业'] = list(deposit_data['行业'].isin(['科技','教育']))



deposit_data_1 = deposit_data.loc[deposit_data['行业'] == '科教']
deposit_data_0 = deposit_data.loc[~deposit_data['行业'].str.contains('科教')]


def train_model(deposit_data,mtypes):
    # filter variable via missing rate, iv, identical value rate
    dt_s = var_filter(deposit_data, y="客户反馈结果",return_rm_reason=True)
    # woe binning ------
    bins = woebin(dt_s['dt'], y="客户反馈结果")
    np.save('data_out\\bins'+mtypes+'.npy',bins)
    bins_df = pd.concat(bins, ignore_index=True)
    bins_df.to_csv('data_out\\bins_df'+mtypes+'.csv', encoding='utf8',index=False)
    train, test = split_df(dt_s['dt'], '客户反馈结果').values()
    train_woe = woebin_ply(train, bins)
    test_woe = woebin_ply(test, bins)
    y_train = train_woe.loc[:,'客户反馈结果']
    X_train = train_woe.loc[:,train_woe.columns != '客户反馈结果']
    X_train.to_csv('data_out\\X_train'+mtypes+'.csv', encoding='utf8',index=False)
    y_train.to_csv('data_out\\y_train'+mtypes+'.csv', encoding='utf8',index=False)
    
    y_test = test_woe.loc[:,'客户反馈结果']
    X_test = test_woe.loc[:,train_woe.columns != '客户反馈结果']
    
    gbm = GradientBoostingClassifier()
    gbm.fit(X_train, y_train)
    print(gbm.score(X_test, y_test)) 
    #print(xgbc.feature_importances_)
    np.save('newmodel\\cols_m'+mtypes+'.npy',X_train.columns)
    joblib.dump(gbm, 'newmodel\\model_'+mtypes+'.pkl')
    return bins,gbm


bins_1,gbm_1 = train_model(deposit_data,mtypes='_a')
bins_0,gbm_0 = train_model(deposit_data_0,mtypes='0')





my_model = joblib.load('model\\model_xgbc1.pkl')

my_bins = pd.read_csv('data_out\\bins_df1.csv')

