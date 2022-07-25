# -*- coding: utf-8 -*-

import json
from os import link
import logging

from bs4 import BeautifulSoup

def defenition_tag(func):
    def wrapper(url, *args, **kwargs):
        if '/api/' in url or '/js/' in url: kwargs['tag'] = 'query'
        else: kwargs['tag'] = 'default'
        result, is_lastPage = func(url, *args, **kwargs)
        return result, is_lastPage
    return wrapper

def query_tag(content):
    soup = BeautifulSoup(content, 'html.parser')
    j = soup.find('body').text
    content = json.loads(j)

    if 'error' in list(content.keys()):
        print(f'Не удалось открыть страницу по причине: {content["error"]["message"]}')
        return None

    try: items = content['catalog']['items']
    except: return None

    ads = {'data_type': 'query', 'items': []}
    if content['itemsOnPage'] < 50: is_lastPage = True
    else: is_lastPage = False
    links = []
    for item in items:
        # ads['items'].append(item)
        try: links.append(f"https://avito.ru{item['urlPath']}")
        except: pass

    return links, is_lastPage

def default_tag(content):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(content, 'html.parser')

    try: ads_section = soup.find('div', {'data-marker': 'catalog-serp'})
    except: return None

    items = ads_section.find_all('div', {'data-marker': 'item'})
    ads = {'data_type': 'default', 'items': []}

    links = []
    if soup.find_all('a', {'class': 'pagination-page'})[-1].text.lower() != 'Последняя'.lower(): is_lastPage = True
    else: is_lastPage = False
    for item in items:
        links.append(f"https://avito.ru{item.find('div', {'class': 'iva-item-titleStep-pdebR'}).find('a').get('href')}")

    return links, is_lastPage

class Get_ads():

    def initLogger(path: str, logLvl: str):
        with open(path, 'w', encoding='utf-8') as file: pass

        logger = logging.getLogger()
        formatter= logging.Formatter('log time - %(asctime)s | log level - %(levelname)s | [%(filename)s: line - %(lineno)d in function %(funcName)s] | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')#, level=logLvl.upper())

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logLvl.upper())
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(filename=path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logLvl.upper())
        logger.addHandler(file_handler)

        console_handler.setLevel(logLvl.upper())
        file_handler.setLevel(logLvl.upper())
        logger.setLevel(logLvl.upper())

        return logger

    @defenition_tag
    def get_ads_request(url: str, **kwargs):
        import requests

        try: q = requests.get(url, kwargs)
        except: return None

        if kwargs['tag'] == 'query': result = query_tag(json.loads(q.content))
        if kwargs['tag'] == 'default': result = default_tag(q.text)
        else: print('Неизвестный формат ссылки')

        return result

    @defenition_tag
    def get_ads_browser(url: str, driver, **kwargs):
        try: driver.get(url)
        except: return None

        if kwargs['tag'] == 'query': result, is_lastPage = query_tag(driver.page_source)
        elif kwargs['tag'] == 'default': result, is_lastPage = default_tag(driver.page_source)
        else: print('Неизвестный формат ссылки')
        
        return result, is_lastPage

if __name__ == "__main__":
    avito = Get_ads
    avito.get_ads_request('https://www.avito.ru/moskva/avtomobili/land_rover_range_rover_sport_2009_2394381622')