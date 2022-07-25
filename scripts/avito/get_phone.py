# -*- coding: utf-8 -*-

import json
import logging

# def processing_phone(func):
#     def wrapper(url:str, driver, *args, **kwargs):
        
#         result = func
#         return result
#     return wrapper

class Get_phone():

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

    def get_phone_request(url:str, **kwargs):
        import requests

        ad_id = url.split('_')[-1]
        requestLink = f'https://m.avito.ru/api/1/items/{ad_id}/phone?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'
        request = requests.get(requestLink, kwargs)
        response = json.loads(request.content)
        try:
            if response['code'] == 403: print(f"Не удалось получить номер телефона по причине: {response['error']['message']}")
        except: pass
        phone = response['result']['action']['uri'].replace('%2B', '+').split('=')[-1]
        for ch in ['+7', '(', ')', '-', ' ']:
            if ch == '+7' and ch in phone:
                phone = phone.replace(ch, '7')
            elif ch in phone:
                phone = phone.replace(ch, '')
        return phone

    def get_phone_browser(url:str, driver, **kwargs):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time

        if driver != None and driver.current_url.replace('https://m.', 'https://www.') != url:
            try: driver.get(url)
            except: print('Не удалось открыть страницу')
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-marker="item-contact-bar/call"]')))
        except:
            return None
        driver.find_element_by_xpath('//button[@data-marker="item-contact-bar/call"]').click()
        
        time.sleep(1)
        try:
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="VgFFy"]')))
        except:
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//span[@data-marker="phone-popup/phone-number"]')))
            phone = driver.find_element_by_xpath('//span[@data-marker="phone-popup/phone-number"]').text
            for ch in ['+7', '(', ')', '-', ' ']:
                if ch == '+7' and ch in phone:
                    phone = phone.replace(ch, '7')
                elif ch in phone:
                    phone = phone.replace(ch, '')
        return phone
