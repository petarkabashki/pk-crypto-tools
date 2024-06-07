# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 11:46:13 2019

@author: Leo
"""
from price_history import get_market_history_price
import numpy as np
import json

from pyecharts import Line
from pyecharts import Overlap


# Moving Average
def MA_Avg(data, n):
    """ 
    对数据data进行n天的移动平均
    """
    i = 0
    N = len(data)
    ma_data = []
    while i < N:
        if i < n:
            t = np.mean(data[0:i+1])
        else:
            t= np.mean(data[i-n:i+1])
        ma_data.append(t)
        i = i+1
    return ma_data

def get_percenttile(data_list, q, ma):
    """
    get q percenttile number
    """
    p = []
    for i in range(len(data_list)):
        if i <ma:
            p.append(np.percentile(data_list[0:i+1], q))
        else:
            p.append(np.percentile(data_list[i-ma:i+1], q))
    return p
        
        

def get_data_from_json():
    
    data = get_market_history_price(name = 'bitcoin', symbol = 'bitcoin', slug = 'bitcoin')
    if data is None:
        with open("btc.json",'r') as load_f:
            data = json.load(load_f)
            print("Successfully get data from json file from local computer!")
    return data



def data_process(data):
  
    # data pre-processing
    days = len(data)
    
    volume= []   # 交易量
    marketcap = [] # 市值
    ts = [] # 时间：day
    btc_price = [] # 收盘价
    
    for d in reversed(data):
        if d['volume'] == '-' :
            volume.append(-1) #获取不到的数据用-1代替
        else:
            volume.append(float(d['volume'].replace(',','')))
        marketcap.append(float(d['marketcap'].replace(',','')))
        ts.append(int(d['ts'].replace(',','')))
        btc_price.append(float(d['close'].replace(',','')))
    
    
    # get data volume != -1
    v_index = [i for i  in range(days) if volume[i] != -1]
    volume_btc = [volume[i] for i in v_index]
    marketcap_btc = [marketcap[i] for i in v_index]
    ts_btc = [ts[i] for i in v_index]
    btc_price_nvt = [btc_price[i] for i in v_index]
    return v_index, volume_btc, marketcap_btc, ts_btc, btc_price_nvt


def cal_NVT_plot(chart_title, v_index, volume_btc, marketcap_btc, ts_btc, btc_price_nvt, ma_volume, ma_nvt):
    """ 
    计算nvt指标，然后作图展示
    """
    # calculation NVT signal
    nvt0_or = [marketcap_btc[i]/volume_btc[i] for i in range(len(v_index))] # 无 ma的nvt
    volume_MA = MA_Avg(volume_btc, ma_volume) # 移动平均volume
    nvt_or = [marketcap_btc[i]/volume_MA[i] for i in range(len(v_index))] # volume ma 之后的nvt
    nvt_MA_or = MA_Avg(nvt_or,ma_nvt) # nvt 进行ma
    
    # NVT 上下分位点  合理边界参考
#    up_bd = get_percenttile(nvt_or, 90, int(ma_nvt*2)) 
#    down_bd = get_percenttile(nvt_or,10, int(ma_nvt/2))
    

    
    nvt = [i for i in nvt_or]
    nvt0 = [i for i in nvt0_or]
    nvt_MA = [i for i in nvt_MA_or]
  
#===================================pyecharts 作图=============================================

    x_date = [str(int(i)) for i in ts_btc]
    nvt0_line = Line(chart_title)
    nvt0_line.add("NVU(original)", x_date, nvt0,
                  tooltip_tragger="axis", 
                  tooltip_axispointer_type = 'cross',
                  is_more_utils = True,
                  is_datazoom_show = True, datazoom_range = [0,100],
                  yaxis_max = 10* max(nvt0), yaxis_min = min(nvt0),
                  yaxis_type = "log", is_xaxislabel_align = True,
                  line_opacity = 0.3, line_color = 'gray',line_type = 'solid')
    
    nvt_line = Line()
    nvt_line.add("NVU(MA(U)=30)", x_date, nvt, yaxis_type = "log", line_color = 'blue', line_type = 'solid')
    
    nvt_ma_line = Line()
    nvt_ma_line.add("MA(NVU)=90", x_date, nvt_MA, yaxis_type = "log", line_color = 'red', line_type = 'solid')
    
    price_line = Line()    
    price_line.add("BTC price", x_date, btc_price_nvt,
                   is_yaxis_show = False,  yaxis_type = "log",
                   yaxis_min = min(btc_price_nvt)/100,
                   line_color = 'coral', line_type = 'solid')
        
    
    overlap = Overlap(width = 1500, height = 800)
    overlap.add(nvt0_line)
    overlap.add(nvt_line)
    overlap.add(nvt_ma_line)    
    overlap.add(price_line, yaxis_index = 1, is_add_yaxis = True)
    
#    overlap.render("my_NVU.html")

 #=================================================================================   
    
    return overlap
 

if __name__ == '__main__':
    data = get_data_from_json() # 获取数据 网站获取或者本地获取
    v_index, volume_btc, marketcap_btc, ts_btc, btc_price_nvt = data_process(data) # 数据获取以及处理
    cal_NVT_plot("", v_index, volume_btc, marketcap_btc, ts_btc, btc_price_nvt, ma_volume=28, ma_nvt=60) # 计算NVT并做图


