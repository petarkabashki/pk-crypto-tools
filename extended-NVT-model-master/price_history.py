import lxml.html
import requests
#from app.mdb.db import social_db, SOCIALCollections
import time
import json
etree = lxml.html.etree


# if '#' in url:
#     index = str(url).find('#') + 1
#     name = url[index:len(url)]
#     path = '//tr//a[@name="{0}"]'.format(name)
#     # table_node = tree.xpath('//tr//a[@name="'+name+'"]/following-sibling::table//div[@class="post"]')
#     table_node = tree.xpath(path)
#     txt = table_node[0].xpath('string(.)').strip('\t')
#     print(txt)
# else:


months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
          'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}


def en_zh_time(en_time):
    """
    时间转 Aug 12, 2018  转为= 20180812
    :param en_time: 英文时间
    :return:
    """
    inx = en_time.index(',')
    new_str = en_time[0:inx] + en_time[inx + 1:len(en_time)]

    mon = new_str[0:3]
    local_mon = months.get(mon)
    local_str = new_str.replace(mon, local_mon)
    spt = local_str.split()
    return spt[2] + spt[0] + spt[1]


def get_market_history_price(name=None, symbol=None, slug=None):
    try:
        header = {
            'user_aget': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/66.0.3359.181 Safari/537.36'
        }
        url = 'https://coinmarketcap.com/currencies/{0}/historical-data/?start=20130428&end=20190110'.format(slug)
        msg = requests.get(url, headers=header).text
        sel = etree.HTML(msg)
        data_path = sel.xpath('//div[@id="historical-data"]/div/div[2]/table/tbody/tr')

        data_array = []
        for x in data_path:
            td_list = x.xpath('.//td/text()')
#            print(name+'  ' + str(en_zh_time(td_list[0])))
            data = {
                'name': name,
                'symbol': symbol,
                'ts': en_zh_time(td_list[0]),
                'open': td_list[1],
                'high': td_list[2],
                'low': td_list[3],
                'close': td_list[4],
                'volume': td_list[5],
                'marketcap': td_list[6]
            }
            data_array.append(data)
            
        save_json(data_array)  
        print("Successfully get data from coinmarketcap.com!")
        return data_array
    except Exception as ee:
        print("Can not get the data from internet, data have not been saved! ")
        print(ee)

        return None
        
    


def get_market_cap_total():
    header = {
        'user_aget': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/66.0.3359.181 Safari/537.36'
    }
    url = 'https://graphs2.coinmarketcap.com/global/marketcap-total/'
    res_msg = requests.get(url=url, headers=header).json()
    market = res_msg['market_cap_by_available_supply']
    vols = res_msg['volume_usd']

    vol_dict = {}
    for vol in vols:
        tm = vol[0]
        vl = vol[1]
        times = time.strftime('%Y%m%d', time.localtime(int(tm / 1000)))
        vol_dict[times] = vl

    for im in market:
        tm = im[0]
        cap = im[1]
        times = time.strftime('%Y%m%d', time.localtime(int(tm / 1000)))
        data = {
            'day': times,
            'time': tm,
            'totalcap': cap,
            'vol_usd': vol_dict[times]
        }
        #social_db[SOCIALCollections.MARKET_CAP_TOTAL].update({'day': times}, data, upsert=True, multi=False)

def save_json(data):
    with open('btc.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(data, indent=2, ensure_ascii=False))
    

if __name__ == '__main__':
#    get_market_cap_total()
    
    data = get_market_history_price(name = 'bitcoin', symbol = 'bitcoin', slug = 'bitcoin')
#    save_json(data)
    
    
    
    
    
    
    # try:
    #     items = social_db[SOCIALCollections.MARKET_TOKEN].find().batch_size(1)
    #     for item in items:
    #         name = item['name']
    #         symbol = item['symbol']
    #         slug = item['slug']
    #
    #         cuns = social_db[SOCIALCollections.MARKET_HISTORY].count_documents({'name': name})
    #         if cuns > 0:
    #             continue
    #         get_market_history_price(name=name, symbol=symbol, slug=slug)
    #         time.sleep(10)
    # except Exception as ee:
    #     print(ee)

