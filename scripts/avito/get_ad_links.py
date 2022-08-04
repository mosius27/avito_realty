# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

def defenition_tag(func):
    def wrapper(url, *args, **kwargs):
        if '/api/' in url or '/js/' in url: kwargs['tag'] = 'query'
        else: kwargs['tag'] = 'default'
        result, is_lastPage, ip_is_blocked = func(url, *args, **kwargs)
        return result, is_lastPage, ip_is_blocked
    return wrapper

def query_tag(content):
    soup = BeautifulSoup(content, 'html.parser')
    if 'Доступ с вашего IP-адреса временно ограничен' in soup.text or 'Доступ с Вашего IP временно ограничен' in soup.text: 
        links = []
        is_lastPage = False
        ip_is_blocked = True
        return links, is_lastPage, ip_is_blocked
    else: 
        ip_is_blocked = False
        j = soup.find('body').text
        content = json.loads(j)

        if 'error' in list(content.keys()):
            print(f'Не удалось открыть страницу по причине: {content["result"]["message"]}')
            links = []
            is_lastPage = False
            ip_is_blocked = True
            return links, is_lastPage, ip_is_blocked
        else: 
            ip_is_blocked = False
            try: items = content['catalog']['items']
            except: links = []

            ads = {'data_type': 'query', 'items': []}
            if content['itemsOnPage'] < 50 or  soup.text == {}: is_lastPage = True
            else: is_lastPage = False
            links = []
            for item in items:
                d = {}
                # ads['items'].append(item)
                try:
                    d['link'] = f"https://avito.ru{item['urlPath']}"
                    d['date_published'] = item['iva']['DateInfoStep'][0]['payload']['absolute']

                    links.append(d)
                except: pass

            return links, is_lastPage, ip_is_blocked

def default_tag(content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    if 'Доступ с вашего IP-адреса временно ограничен' in soup.text or 'Доступ с Вашего IP временно ограничен' in soup.text: 
        links = []
        is_lastPage = False
        ip_is_blocked = True
        return links, is_lastPage, ip_is_blocked
    else: 
        ip_is_blocked = False
        try: ads_section = soup.find('div', {'data-marker': 'catalog-serp'})
        except: return None

        items = ads_section.find_all('div', {'data-marker': 'item'})
        ads = {'data_type': 'default', 'items': []}

        links = []
        if soup.find_all('a', {'class': 'pagination-page'})[-1].text.lower() != 'Последняя'.lower(): is_lastPage = True
        else: is_lastPage = False
        for item in items:
            d = {}
            d['link'] = f"https://avito.ru{item.find('div', {'class': 'iva-item-titleStep-pdebR'}).find('a').get('href')}"
            links.append(d)

        return links, is_lastPage, ip_is_blocked

class Get_ads():

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

        try: 
            driver.get(url)
        except: print('Не удалось загрузить страницу')

        if kwargs['tag'] == 'query': result, is_lastPage, ip_is_blocked = query_tag(driver.page_source)
        elif kwargs['tag'] == 'default': result, is_lastPage, ip_is_blocked = default_tag(driver.page_source)
        else: print('Неизвестный формат ссылки')
        
        return result, is_lastPage, ip_is_blocked

if __name__ == "__main__":
    avito = Get_ads
    avito.get_ads_request('https://www.avito.ru/moskva/avtomobili/land_rover_range_rover_sport_2009_2394381622')