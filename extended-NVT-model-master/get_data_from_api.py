# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 13:49:03 2019

@author: Leo
"""

import requests
import time
#import numpy as np
import json



def save_json(data):
    with open('btc_from_coinmetrics.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(data, indent=2, ensure_ascii=False))
        
def get_history_data(token_name = 'btc',time_start = '2013-04-28 00:00:00',time_end = time.time()):        
#    time_start = '2013-04-28 00:00:00'
#    time_end = time.time()
    
    temp = time.strptime(time_start, "%Y-%m-%d %H:%M:%S")
    ts = int(time.mktime(temp)) # 开始时间
    te = int(time_end)  # 结束时间
    
    item_data = ['price(usd)', 'marketcap(usd)', 'txvolume(usd)', 'adjustedtxvolume(usd)', 'activeaddresses' ,'txcount', 'exchangevolume(usd)', 'averagedifficulty']
    
    # get different data about item_data
    data ={}
    for item in item_data:
        url = 'https://coinmetrics.io/api/v1/get_asset_data_for_time_range/{0}/{1}/{2}/{3}'.format(token_name, item, ts, te)
        r = requests.get(url)
        print("Status code:", r.status_code)
        response_result = r.json()
        data[item] = response_result["result"]
        
    if data != {}:
        save_json(data) 
        print("Data has been saved as a Json file!")
    else:
        print("Have not get data!")
    
    #    data[item] = np.array(response_result["result"])
        
    # change timestamps to structural time     
    for item in item_data:
        for i in range(len(data[item])):
            data[item][i][0] = int(time.strftime("%Y%m%d",time.localtime(data[item][i][0])))
    
    # save data to json file
    save_json(data)    
    return data


if __name__ == '__main__':
    get_history_data(token_name = 'btc', time_start = '2013-04-28 00:00:00',time_end = time.time())
    
    






