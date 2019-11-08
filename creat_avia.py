import requests
import json
import datetime
import time
import schedule
import pandas as pd
from bs4 import BeautifulSoup
import schedule
import logging
import keys

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG,
                    filename=u'mylog.log')

interesting_cities_krk = ['IEV', 'PAR', 'PRG', 'MRS', 'BOD', 'ROM', 'FAE', 'ZRH', 'GVA', 'MMA', 'STO', 'CPH', 'VIE',
                          'LON', 'REK', 'DUB', 'TCI', 'MAD', 'BCN', 'VCE', 'MIL', 'NAP', 'FLR', 'AMS', 'OSL', 'BUD',
                          'BER', 'MUC']
interesting_cities_iev = ['KRK', 'WRO', 'WAW', 'GDN', 'PAR', 'PRG', 'MRS', 'BOD', 'ROM', 'FAE', 'ZRH', 'GVA', 'MMA',
                          'STO', 'CPH', 'VIE',
                          'LON', 'REK', 'DUB', 'TCI', 'MAD', 'BCN', 'VCE', 'MIL', 'NAP', 'FLR', 'AMS', 'OSL', 'BUD',
                          'BER', 'MUC']
interesting_cities_mow = ['KRK', 'WRO', 'WAW', 'GDN', 'PAR', 'PRG', 'MRS', 'BOD', 'ROM', 'FAE', 'ZRH', 'GVA', 'MMA',
                          'STO', 'CPH', 'VIE',
                          'LON', 'REK', 'DUB', 'TCI', 'MAD', 'BCN', 'VCE', 'MIL', 'NAP', 'FLR', 'AMS', 'OSL', 'BUD',
                          'BER', 'MUC']
interesting_cities_led = ['KRK', 'WRO', 'WAW', 'GDN', 'PAR', 'PRG', 'MRS', 'BOD', 'ROM', 'FAE', 'ZRH', 'GVA', 'MMA',
                          'STO', 'CPH', 'VIE',
                          'LON', 'REK', 'DUB', 'TCI', 'MAD', 'BCN', 'VCE', 'MIL', 'NAP', 'FLR', 'AMS', 'OSL', 'BUD',
                          'BER', 'MUC']
interesting_cities_prg = ['KRK', 'WRO', 'WAW', 'GDN', 'PAR', 'IEV', 'MRS', 'BOD', 'ROM', 'FAE', 'ZRH', 'GVA', 'MMA',
                          'STO', 'CPH', 'VIE',
                          'LON', 'REK', 'DUB', 'TCI', 'MAD', 'BCN', 'VCE', 'MIL', 'NAP', 'FLR', 'AMS', 'OSL', 'BUD',
                          'BER', 'MUC']

interesting_cities_list = {'KRK': interesting_cities_krk, 'IEV': interesting_cities_iev, 'MOW': interesting_cities_mow,
                           'LED': interesting_cities_led, 'PRG': interesting_cities_prg}

origin_list = ['KRK', 'IEV', 'MOW', 'LED', 'PRG']


# Taking token, interesting cities list and time list. And work with this.
def avia_tickets(cities_l, time_l, token):
    result = []
    # Open interesting cities list
    for citi in cities_l:
        # Time list for choosed city
        for time in time_l:
            # Taking request for choosed city in choosed month
            res = request_avia(citi, time, token)
            if len(res['data']) > 0:
                result.append(res)
    return result


# Request from travelpayouts API
def request_avia(citi, time, token):
    url = "https://api.travelpayouts.com/v1/prices/calendar"

    querystring = {"depart_date": time, "origin": origin, "destination": citi, "calendar_type": "departure_date",
                   "currency": "USD"}

    headers = {'x-access-token': token}

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()


# From json to list
def from_json(lst):
    names = ['origin', 'destination', 'price', 'transfers', 'airline', 'flight_number', 'departure_at',
             'return_at', 'expires_at']
    result = []
    for i in lst:
        for data in i['data'].items():
            inresult = []
            inresult.append(data[0])
            second = []
            for name in names:
                second.append(data[1][name])
            inresult += second
        result.append(inresult)
    return result


# Main function
def job(origin, interesting_cities):
    token = keys.avia_token
    logging.info(u'The work is starting')

    try:
        time_list = []
        time = datetime.datetime.now()
        year = time.year
        month = time.month

        # Creating month list.
        for i in range(0, 6):
            if month > 12:
                year += 1
                month = 1
            if len(str(month)) == 1:
                strmonth = '0' + str(month)
                st = str(year) + '-' + str(strmonth)
                time_list.append(st)
            else:
                st = str(year) + '-' + str(month)
                time_list.append(st)
            month += 1

        json_avia = avia_tickets(interesting_cities, time_list, token)

        list_avia = from_json(json_avia)

        # Create main dataframe
        df = pd.DataFrame(list_avia,
                          columns=['data', 'origin', 'destinaton', 'price', 'transfers', 'airline', 'flight_number',
                                   'departure_at', 'return_at', 'expires_at'])

        airline_code = pd.read_csv('airlines_codes.csv')

        # Adding full name of airline
        df = df.merge(airline_code, left_on='airline', right_on='code', how='right')
        df.dropna(inplace=True)

        city_code = pd.read_csv('cties_code.csv')

        # Adding full name of origin city
        df = df.merge(city_code, left_on='origin', right_on='citi code', how='right')
        del df['citi code']
        df.rename(columns={'citi name': 'origin citi'}, inplace=True)
        df.dropna(inplace=True)

        # Adding full name of destination city
        df = df.merge(city_code, left_on='destinaton', right_on='citi code', how='right')
        del df['citi code']
        df.rename(columns={'citi name': 'destinaton citi'}, inplace=True)
        df.dropna(inplace=True)

        del df['code']

        # Saving results
        save_name = 'avi_result_' + origin + '.csv'
        df.to_csv(save_name, index=False)
        leng = len(df)
        logging.info('The work is done, size of csv {0}'.format(leng))
    except:
        logging.exception(u'Something goes wrong')


def runer():
    for city in origin_list:
        intersting = interesting_cities_list[city]
        job(city, intersting)

    print('done')


runer()
schedule.every(4).hours.do(runer)

while True:
    schedule.run_pending()
    time.sleep(120)
