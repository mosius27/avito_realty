# -*- coding: utf-8 -*-

import time
import random
import logging
import traceback
import multiprocessing
import os
import sys
from datetime import datetime, timedelta
from multiprocessing import Process, RLock, Manager
import other.read_write_files as working_with_file
import other.create_search_link as create_search_link
import other.datas as datas

def time_wait():
    return random.randint(datas.ParseSettings().delay_from, datas.ParseSettings().delay_to)

# Функция запуска selenium браузера
def startBrowser(self):
    from browser import Beginnig_browser

    try: 
        self.driver.close()
        self.driver.quit()
    except: pass

    if datas.ParseSettings().use_proxy == True:
        if list(self.proxyes) != []:
            proxy = self.proxyes.pop(0)
            self.proxyes.append(proxy)
            print(proxy)
            self.driver = Beginnig_browser.chrome(proxy=proxy, settings_path=datas.Paths().browser_settings)
        else: self.driver = Beginnig_browser.chrome(settings_path=datas.Paths().browser_settings)
    else: self.driver = Beginnig_browser.chrome(settings_path=datas.Paths().browser_settings)

# Функция инициализирующая logger
def initLogger(path: str, logLvl: str):
    with open(path, 'w', encoding='utf-8') as file: pass

    logger = logging.getLogger()
    formatter= logging.Formatter('{processName} | log time - %(asctime)s | log level - %(levelname)s | [%(filename)s: line - %(lineno)d in function %(funcName)s] | %(message)s'.format(processName=multiprocessing.current_process().name), datefmt='%Y-%m-%d %H:%M:%S')

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

# Функция для чтения и записи файлов
def read_write_data(self, **kwargs):
    with self.lock:
        if kwargs['action'] == 'read':
            if '.json' in kwargs['path']:
                return working_with_file.read_json(kwargs['path'])

            if '.txt' in kwargs['path']:
                return working_with_file.read_txt(path=kwargs['path'])
            
            if '.yml' in kwargs['path']:
                return working_with_file.load_yaml(path=kwargs['path'])

        if kwargs['action'] == 'write':
            if '.json' in kwargs['path']:
                working_with_file.write_json(path=kwargs['path'], var=kwargs['var'])

            if '.csv' in kwargs['path']:
                working_with_file.write_csv(path=kwargs['path'], var=kwargs['var'], fieldnames=kwargs['header'])

            if '.xlsx' in kwargs['path']:
                working_with_file.write_line_excel(path=kwargs['path'], var=kwargs['var'])
            
            if '.txt' in kwargs['path']:
                working_with_file.write_list_in_txt(path=kwargs['path'], var=kwargs['var'])


class AvitoRealty():
    
    def __init__(self):
        self.lock = RLock()
        self.logger = initLogger(path=f'{os.path.abspath(datas.Paths().log_folder)}\\{multiprocessing.current_process().name}.log', logLvl=datas.ParseSettings().log_level)
        self.manager = Manager()
        self.proxyes = self.manager.list(read_write_data(self, path=datas.Paths().proxy, action='read'))
        if datas.ParseSettings().check_new_ad_on_processed == True:
            self.processed = self.manager.list(read_write_data(self, path=datas.Paths().processed_links, action='read'))
        generator_links_settings = read_write_data(self, path=datas.Paths().create_search_link_settings, action='read')
        category = read_write_data(self, path=datas.Paths().categories, action='read')
        location = read_write_data(self, path=datas.Paths().locations, action='read')
        self.search_link = create_search_link.createSearchLink(generator_links_settings, category, location)
        self.search_links_list = self.checkNumAds()
        data = {'Дата_публикации': 'Дата_публикации',
            'Заголовок': 'Заголовок',
            'Тип_недвижимости': 'Тип_недвижимости',
            'Описание': 'Описание',
            'Цена': 'Цена',
            'Регион': 'Регион',
            'Город': 'Город',
            'Адрес': 'Адрес',
            'Url': 'Url',
            'Изображения': 'Изображения'
            }
        data = datas.Ad_Data(**data)
        working_with_file.create_table_PostgresSQL(datas.ParseSettings().db_access, data)

    def start(self):
        if datas.ParseSettings().work_mode == 'get_ads':
            self.get_ads()

        if datas.ParseSettings().work_mode == 'ads_data':
            self.ads = self.manager.list(read_write_data(self, path=datas.Paths().ads_link, action='read'))
            self.ads_data()

        if datas.ParseSettings().work_mode == 'all':
            self.get_ads()
            self.ads = self.manager.list(read_write_data(self, path=datas.Paths().ads_link, action='read'))
            self.ads_data()
    
    def get_ads(self):
        from avito import Get_ads
        
        self.logger.info('Начало сбора ссылок на объявления')
        if datas.ParseSettings().deep_scan == True:
            page = self.manager.Value('', value=1)
            for search_link in self.search_links_list:
                while True:
                    try: 
                        if ip_is_blocked == True: page -= 1
                    except: pass
                    ads = read_write_data(self, path=self.paths['ads link'], action='read')
                    processed = read_write_data(self, path=self.paths['processed links'], action='read')
                    self.logger.info(f'Номер страницы: {page}')
                    try:
                        url = f'{self.search_link}&p={page}'

                        if self.method.value == 'selenium':
                            newAds, is_lastPage, ip_is_blocked = Get_ads.get_ads_browser(url=url, driver=self.driver)
                        
                        if ip_is_blocked == True: 
                            self.num_error = 0
                            self.logger.info('IP адрес заблокирован на авито. Перезагрузка chromedriver для смены ip/proxy')
                            self.driver = startBrowser(self)
                            continue

                        for ad in newAds:
                            if self.parse_settings['check new ad on processed'] == True:
                                if ad not in ads and ad not in processed:
                                    ads.append(ad)
                            else:
                                if ad not in ads:
                                    ads.append(ad)

                        self.logger.info(f'Собрано ссылок: {len(ads)}')
                    except: self.logger.info('Не удалось загрузить страницу\n{}'.format(traceback.format_exc()))
                    finally:
                        if self.parse_settings['check new ad on processed'] == True:
                            processed = read_write_data(self, path=self.paths['processed links'], action='read')
                            ads = list(set(ads) - set(processed))
                        self.logger.debug('Сохраняемые объявления {}'.format(ads))
                        read_write_data(self, path=self.paths['ads link'], var=ads, action='write')
                        time_pause = time_wait(self.delay.value)
                        self.logger.info(f'Ожидание: {time_pause} сек')
                        time.sleep(time_pause)
                        if is_lastPage: break
                        page += 1

        if datas.ParseSettings().deep_scan == True:
            
            for search_link in self.search_links_list:
                page = self.manager.Value('', value=1)
                try:
                    url = f'{self.search_link}&p={page}&s=104'

                    if self.method.value == 'selenium':
                        newAds, is_lastPage, ip_is_blocked = Get_ads.get_ads_browser(url=url, driver=self.driver)
                    
                    if ip_is_blocked == True: 
                        self.num_error = 0
                        self.logger.info('IP адрес заблокирован на авито. Перезагрузка chromedriver для смены ip/proxy')
                        self.driver = startBrowser(self)
                        continue

                    for ad in newAds:
                        if self.parse_settings['check new ad on processed'] == True:
                            if ad not in ads and ad not in processed:
                                ads.append(ad)
                        else:
                            if ad not in ads:
                                ads.append(ad)

                    self.logger.info(f'Собрано ссылок: {len(ads)}')
                except: self.logger.info('Не удалось загрузить страницу\n{}'.format(traceback.format_exc()))
    def ads_data(self):
        from avito import Check_ad

        self.logger.info('Начало проверки объявлений')
        while self.ads:
            ad = self.ads.pop(0)
            self.logger.info('Проверка объявления {}'.format(ad))
            with self.lock:
                read_write_data(self, path=datas.Paths().ads_link, var=self.ads, action='write')
                if datas.ParseSettings().save_checked_ads == True:
                    processed = read_write_data(self, path=datas.Paths().processed_links, action='read')
                    processed.append(ad)
                    read_write_data(self, path=datas.Paths().processed_links, var=processed, action='write')
            try:
                ad_info, ip_is_blocked = Check_ad.check_ad_browser(url=ad, driver=self.driver)

                if ip_is_blocked == True: 
                    self.num_error = 0
                    self.logger.info('IP адрес заблокирован на авито. Перезагрузка chromedriver для смены ip/proxy')
                    self.driver = startBrowser(self)                    
                    with self.lock:
                        self.ads = read_write_data(self, path=self.paths['ads link'], action='read')
                        self.ads.append(ad)
                        read_write_data(self, path=self.paths['ads link'], var=self.ads, action='write')
                        processed = read_write_data(self, path=self.paths['processed links'], action='read')
                        processed.remove(ad)
                        read_write_data(self, path=self.paths['processed links'], var=processed, action='write')
                    continue

            except:
                with self.lock:
                    self.ads = read_write_data(self, path=self.paths['ads link'], action='read')
                    self.ads.append(ad)
                    read_write_data(self, path=self.paths['ads link'], var=self.ads, action='write')
                    processed = read_write_data(self, path=self.paths['processed links'], action='read')
                    processed.remove(ad)
                    read_write_data(self, path=self.paths['processed links'], var=processed, action='write')

                self.logger.error('Не удалось получить данные объявления {}'.format(traceback.format_exc()))

                time_pause = time_wait(self.delay.value)
                self.logger.info(f'Ожидание: {time_pause} сек')
                time.sleep(time_pause)
                continue
            try:
                ad_info = ad_info['dto']
                if ad_info['item']['isActive'] == True:
                    images = ad_info['item']['imageUrls']
                    images_str = ''
                    for image in images:
                        try: images_str += f'{image["1280x960"]}\n'
                        except: 
                            self.logger.debug('Не найдено изображение с разрешением 1280x960')
                            continue

                    params = ad_info['paramsDto']['items']
                    param_str = ''
                    with self.lock:
                        
                        param_dict = {}
                        for param in params:

                            if working_with_file.check_exists_collumn_postgresSQL(datas.ParseSettings().db_access, param["title"]) == False:
                                working_with_file.add_column_PostgresSQL(datas.ParseSettings().db_access, param["title"])
                            try:
                                if '*' in param['description']: param_dict[param["title"]] = ad_info["contextItem"]["raw_params"][str(params[param]["attributeId"]).replace("&nbsp;", " ")]
                                else: param_dict[param["title"]] = param["description"].replace("&nbsp;", " ")
                            except: 
                                self.logger.info('Не удалось обработать параметр {}'.format(param))
                                continue

                    description = ad_info['contextItem']['description']
                    tag_for_delete = {'<p>': '', '</p>': '\n', '<b>': '', '</b>': '', '<br>': '', '</br>': '', '<li>': '', '</li>': '\n', '<ul>': '\n', '</ul>': '', '<br />': '', ';': ''}
                    self.logger.info('Очистка html тегов из описания')
                    for tag in list(tag_for_delete.keys()):
                        description = description.replace(tag, tag_for_delete[tag])

                    region = ''
                    if 'республика,' in ad_info["item"]["address"].lower() or 'область,' in ad_info["item"]["address"].lower():
                        addres_values = ad_info["item"]["address"].split(',')
                        for v in addres_values:
                            if'республика,' in ad_info["item"]["address"].lower() or 'область,' in ad_info["item"]["address"].lower():
                                region = v
                                break
                    
                    data = {'Дата_публикации': (datetime.utcfromtimestamp(ad_info["contextItem"]["date_unix"]) + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                        'Заголовок': ad_info["contextItem"]["title"],
                        'Тип_недвижимости': ad_info["contextItem"]["category"]['name'],
                        'Описание': description,
                        'Цена': ad_info["window.dataLayer"]["itemPrice"],
                        'Регион': region,
                        'Город': ad_info["item"]["location"]["name"],
                        'Адрес': ad_info["item"]["address"],
                        'Url': ad,
                        'Изображения': images_str,
                        }

                    ad_data = datas.Ad_Data(**data)

                    with self.lock:
                        self.logger.info('Полученные данные объявления {}'.format(data))
                        working_with_file.insert_table_PostgresSQL(datas.ParseSettings().db_access, ad_data, param_dict)

            except: self.logger.error('Ошибка при сохранении данных\n{}'.format(traceback.format_exc()))
            finally:
                time_pause = time_wait(self.delay.value)
                self.logger.info(f'Ожидание: {time_pause} сек')
                time.sleep(time_pause)

    def checkNumAds(self):
        search_links_list = []
        check_count_ad_link = f'{self.search_link}&countOnly=1'
        driver = startBrowser(self)
        
        return search_links_list

    def startProcess(self):
        procs = []

if __name__ == "__main__":
    # carprice = AvitoRealty()
    # carprice.get_ads()
    data = {'Дата_публикации': '2022-07-29 13:57:53',
            'Заголовок': 'Заголовок',
            'Тип_недвижимости': 'Тип_недвижимости',
            'Описание': 'Описание',
            'Цена': 1,
            'Регион': 'Регион',
            'Город': 'Город',
            'Адрес': 'Адрес',
            'Url': 'Url',
            'Изображения': 'Изображения'
            }
    data = datas.Ad_Data(**data)
    params = {'qwe': 'qwe', 'adszxc': 'adszxc'}
    # working_with_file.add_column_PostgresSQL(datas.ParseSettings().db_access, 'qwe')
    # working_with_file.add_column_PostgresSQL(datas.ParseSettings().db_access, 'adszxc')

    working_with_file.insert_table_PostgresSQL(datas.ParseSettings().db_access, dict(data), params)
    ...