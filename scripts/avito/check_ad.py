# -*- coding: utf-8 -*-

import json
import logging

def get_ad_info(content):
    from bs4 import BeautifulSoup

    ad_info = {}
    soup = BeautifulSoup(content, 'html.parser')
    if 'Доступ с вашего IP-адреса временно ограничен' in soup.text or 'Доступ с Вашего IP временно ограничен' in soup.text: 
        ip_is_blocked = True
        return ad_info, ip_is_blocked
    else: 
        ip_is_blocked = False
    
        scripts = soup.find_all('script')
        for script in scripts:
            if 'js-ssr' in script.text:
                split_list = {'})(': -1}#, ';': 0, '=': -1}
                script = script.text
                for i in list(split_list.keys()):
                    script = script.split(i)[split_list[i]].strip()
                string = script[:-2]
                string = json.loads(string)
                break
        ad_info = json.loads(string['bx-item-view']['instances'][0]['props'][0])

        scripts = soup.find_all('script')
        for script in scripts:
            if 'window.dataLayer =' in script.text:
                adInfo = script.text.split('];')[0] + ']'
                break

        replaceList = ['window.dataLayer = ', '\n']
        for replaceItem in replaceList:
            adInfo = adInfo.replace(replaceItem, '')
        adInfo = adInfo.strip()
        adInfo = json.loads(adInfo)[1]
        ad_info['dto']['window.dataLayer'] = adInfo

        return ad_info, ip_is_blocked

class Check_ad():

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

    def check_ad_request(url: str, **kwargs):
        import requests
        try: r = requests.get(url, kwargs)
        except: return None
        ad_info, ip_is_blocked = get_ad_info(r.content)
        
        return ad_info['dto'], ip_is_blocked

    def check_ad_browser(url: str, driver, **kwargs):
        try: 
            driver.get(url)
        except: print('Не удалось загрузить страницу')
        ad_info, ip_is_blocked = get_ad_info(driver.page_source)

        return ad_info, ip_is_blocked

if __name__ == "__main__":
    # with open('driver mobile ad page source.txt', 'r', encoding='utf-8') as file:
    #     t = file.read()
    import sys
    sys.path.append('./')
    from scripts.browser.start_browser import Beginnig_browser
    driver = Beginnig_browser.chrome()
    link = ''
    ad_info = Check_ad.check_ad_browser(link, driver)
    ...