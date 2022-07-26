# -*- coding: utf-8 -*-

import json
import time
import random
import traceback
from datetime import datetime, timedelta
from multiprocessing import Process, RLock, Manager, Queue

from bs4 import BeautifulSoup
import scripts.other.read_write_files as working_with_file
import scripts.other.create_search_link as create_search_link
import scripts.other.datas as datas
import scripts.other.logger as log
from scripts.db.init_db import DB
log.Logging()

def time_wait():
    return random.randint(datas.ParseSettings().delay_from, datas.ParseSettings().delay_to)

# Функция запуска selenium браузера
@log.logger.catch
def startBrowser(self):
    from scripts.browser import Beginnig_browser

    try: 
        self.driver.close()
        self.driver.quit()
    except: pass

    if datas.ParseSettings().use_proxy == True:
        if list(self.proxyes) != []:
            with self.lock:
                proxy = self.proxyes.pop(0)
                self.proxyes.append(proxy)
                log.logger.info('Применения прокси {} для запуска браузера'.format(proxy))
            self.driver = Beginnig_browser.chrome(proxy=proxy, settings_path=datas.Paths().browser_settings)
        else: self.driver = Beginnig_browser.chrome(settings_path=datas.Paths().browser_settings)
    else: self.driver = Beginnig_browser.chrome(settings_path=datas.Paths().browser_settings)

def beginning_programm(self):
    with self.lock:
        self.db = DB()
    if datas.ParseSettings().work_mode == 'get_ads' or datas.ParseSettings().work_mode == 'all':
        with self.lock:
            if self.search_links_list.qsize() == 0:
                self.checkNumAds()
    startBrowser(self)
    if datas.ParseSettings().work_mode == 'get_ads':
        self.get_ads()

    if datas.ParseSettings().work_mode == 'ads_data':
        self.ads_data()

    if datas.ParseSettings().work_mode == 'all':
        self.get_ads()
        self.ads_data()

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
        
        manager = Manager()
        self.proxyes = manager.list(read_write_data(self, path=datas.Paths().proxy, action='read'))
        generator_links_settings = read_write_data(self, path=datas.Paths().create_search_link_settings, action='read')
        category = read_write_data(self, path=datas.Paths().categories, action='read')
        location = read_write_data(self, path=datas.Paths().locations, action='read')
        self.search_links = create_search_link.createSearchLink(generator_links_settings, category['category'], location['location'])

        self.checked_page = manager.list([])
        if datas.ParseSettings().work_mode == 'get_ads' or datas.ParseSettings().work_mode == 'all':
            self.search_links_list = Queue()
        
    def start(self):
        if datas.ParseSettings().use_multiprocessing == True:
            self.startProcess()
        else: beginning_programm()

    @log.logger.catch
    def get_ads(self):
        from scripts.avito import Get_ads
        months = {
            'янв': 1,
            'фев': 2,
            'мар': 3,
            'апр': 4,
            'мая': 5,
            'июн': 6,
            'июл': 7,
            'авг': 8,
            'сент': 9,
            'окт': 10,
            'ноя': 11,
            'дек': 12
        }
        
        log.logger.info('Начало сбора ссылок на объявления')
        if datas.ParseSettings().deep_scan == True:
            while self.search_links_list.qsize() > 0:
                elem = self.search_links_list.get()
                if elem in self.checked_page: continue
                try:
                    with self.lock:
                        if datas.ParseSettings().save_checked_ads == True or datas.ParseSettings().check_new_ad_on_processed == True:
                            processed = read_write_data(self, path=datas.Paths().processed_links, action='read')
                        ads = read_write_data(self, path=datas.Paths().ads_link, action='read')

                    url = elem
                    log.logger.info('Сбор объявлений со страницы: {}'.format(url))

                    newAds, is_lastPage, ip_is_blocked = Get_ads.get_ads_browser(url=f'{url}', driver=self.driver)
                    
                    if ip_is_blocked == True: 
                        self.search_links_list.put(url)
                        log.logger.info('IP адрес заблокирован на авито. Перезагрузка chromedriver для смены ip/proxy')
                        self.driver = startBrowser(self)
                        continue

                    for ad in newAds:
                        ad = ad['link']
                        if datas.ParseSettings().check_new_ad_on_processed == True:
                            if ad not in ads and ad not in processed:
                                ads.append(ad)
                        else:
                            if ad not in ads:
                                ads.append(ad)
                    self.checked_page.append(elem)

                except: 
                    self.search_links_list.put(url)
                    log.logger.info('Не удалось загрузить страницу\n{}'.format(traceback.format_exc()))
                finally:
                    with self.lock:
                        if datas.ParseSettings().save_checked_ads == True or datas.ParseSettings().check_new_ad_on_processed == True:
                            processed = read_write_data(self, path=datas.Paths().processed_links, action='read')
                            saved_ads = read_write_data(self, path=datas.Paths().ads_link, action='read')
                            saved_ads += processed
                        else:
                            saved_ads = read_write_data(self, path=datas.Paths().ads_link, action='read')
                        ads = list(set(ads) - set(saved_ads))
                        ads = saved_ads + ads
                        log.logger.info(f'Собрано ссылок: {len(ads)}')
                        log.logger.debug('Сохраняемые объявления {}'.format(ads))
                        read_write_data(self, path=datas.Paths().ads_link, var=ads, action='write')
                    time_pause = time_wait()
                    log.logger.info(f'Ожидание: {time_pause} сек')
                    time.sleep(time_pause)

        elif datas.ParseSettings().deep_scan == False:
            
            while self.search_links_list.qsize() > 0:
                elem = self.search_links_list.get()
                if elem in self.checked_page: continue
                try:
                    with self.lock:
                        if datas.ParseSettings().save_checked_ads == True or datas.ParseSettings().check_new_ad_on_processed == True:
                            processed = read_write_data(self, path=datas.Paths().processed_links, action='read')
                        ads = read_write_data(self, path=datas.Paths().ads_link, action='read')
                    url = elem
                    log.logger.info('Сбор объявлений со страницы: {}'.format(url))

                    newAds, is_lastPage, ip_is_blocked = Get_ads.get_ads_browser(url=f'{url}&s=104', driver=self.driver)
                    
                    if ip_is_blocked == True: 
                        self.search_links_list.put(url)
                        log.logger.info('IP адрес заблокирован на авито. Перезагрузка chromedriver для смены ip/proxy')
                        self.driver = startBrowser(self)
                        continue

                    for ad in newAds:
                        date_published = ad['date_published']
                        ad = ad['link']
                        for m in months:
                            for date in date_published.split(' '):
                                if m.lower() in date.lower():
                                    date_published = date_published.replace(date, f'{str(months[m])} {datetime.now().year}')
                        try:
                            d = datetime.strptime(date_published, '%d %m %Y %H:%M').strftime('%Y-%m-%d')
                            d = datetime.strptime(d, '%Y-%m-%d')
                            now = datetime.now().strftime('%Y-%m-%d')
                            now = datetime.strptime(now, '%Y-%m-%d')
                            days_on_avito = (now - d).seconds // 3600
                        except: days_on_avito = 0
                        if days_on_avito > datas.ParseSettings().look_up_date:
                            continue
                        if datas.ParseSettings().check_new_ad_on_processed == True:
                            if ad not in ads and ad not in processed:
                                ads.append(ad)
                        else:
                            if ad not in ads:
                                ads.append(ad)
                    self.checked_page.append(elem)

                except: 
                    self.search_links_list.put(url)
                    log.logger.info('Не удалось загрузить страницу\n{}'.format(traceback.format_exc()))
                finally:
                    with self.lock:
                        if datas.ParseSettings().save_checked_ads == True or datas.ParseSettings().check_new_ad_on_processed == True:
                            processed = read_write_data(self, path=datas.Paths().processed_links, action='read')
                            saved_ads = read_write_data(self, path=datas.Paths().ads_link, action='read')
                            saved_ads += processed
                        else:
                            saved_ads = read_write_data(self, path=datas.Paths().ads_link, action='read')
                        ads = list(set(ads) - set(saved_ads))
                        ads = saved_ads + ads
                        log.logger.info(f'Собрано ссылок: {len(ads)}')
                        log.logger.debug('Сохраняемые объявления {}'.format(ads))
                        read_write_data(self, path=datas.Paths().ads_link, var=ads, action='write')
                    time_pause = time_wait()
                    log.logger.info(f'Ожидание: {time_pause} сек')
                    time.sleep(time_pause)

    @log.logger.catch
    def ads_data(self):
        from scripts.avito import Check_ad

        log.logger.info('Начало проверки объявлений')
        ads = read_write_data(self, path=datas.Paths().ads_link, action='read')
        while ads:
            with self.lock:
                if datas.ParseSettings().save_checked_ads == True or datas.ParseSettings().check_new_ad_on_processed == True:
                    processed = read_write_data(self, path=datas.Paths().processed_links, action='read')
                ads = read_write_data(self, path=datas.Paths().ads_link, action='read')
                ad = ads.pop(0)
                log.logger.info('Проверка объявления {}'.format(ad))
                read_write_data(self, path=datas.Paths().ads_link, var=ads, action='write')
                processed.append(ad)
                read_write_data(self, path=datas.Paths().processed_links, var=processed, action='write')
            
            try:
                ad_info, ip_is_blocked = Check_ad.check_ad_browser(url=ad, driver=self.driver)

                if ip_is_blocked == True: 
                    log.logger.info('IP адрес заблокирован на авито. Перезагрузка chromedriver для смены ip/proxy')
                    self.driver = startBrowser(self)
                    with self.lock:
                        ads = read_write_data(self, path=datas.Paths().ads_link, action='read')
                        ads.append(ad)
                        read_write_data(self, path=datas.Paths().ads_link, var=ads, action='write')
                        processed = read_write_data(self, path=datas.Paths().processed_links, action='read')
                        processed.remove(ad)
                        read_write_data(self, path=datas.Paths().processed_links, var=processed, action='write')
                    continue

            except:
                with self.lock:
                    ads = read_write_data(self, path=datas.Paths().ads_link, action='read')
                    ads.append(ad)
                    read_write_data(self, path=datas.Paths().ads_link, var=ads, action='write')
                    processed = read_write_data(self, path=datas.Paths().processed_links, action='read')
                    processed.remove(ad)
                    read_write_data(self, path=datas.Paths().processed_links, var=processed, action='write')

                log.logger.error('Не удалось получить данные объявления {}'.format(traceback.format_exc()))

                time_pause = time_wait()
                log.logger.info(f'Ожидание: {time_pause} сек')
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
                            log.logger.debug('Не найдено изображение с разрешением 1280x960')
                            continue

                    params = ad_info['paramsDto']['items']
                    param_str = ''
                    with self.lock:

                        param_dict = {}
                        for param in params:
                            param['title'] = param["title"].strip().replace(' ', '_')
                            try:
                                if '*' in param['description']: param_dict[param["title"]] = ad_info["contextItem"]["raw_params"][str(params[param]["attributeId"]).replace("&nbsp;", " ")]
                                else: param_dict[param["title"]] = param["description"].replace("&nbsp;", " ")
                            except: 
                                log.logger.info('Не удалось обработать параметр {}'.format(param))
                                continue

                    description = ad_info['contextItem']['description']
                    tag_for_delete = {'<p>': '', '</p>': '\n', '<b>': '', '</b>': '', '<br>': '', '</br>': '', '<li>': '', '</li>': '\n', '<ul>': '\n', '</ul>': '', '<br />': '', ';': ''}
                    log.logger.info('Очистка html тегов из описания')
                    for tag in list(tag_for_delete.keys()):
                        description = description.replace(tag, tag_for_delete[tag])

                    region = ''
                    if 'республика ' in ad_info["item"]["address"].lower() or 'область,' in ad_info["item"]["address"].lower():
                        addres_values = ad_info["item"]["address"].split(',')
                        for v in addres_values:
                            if'республика ' in ad_info["item"]["address"].lower() or 'область,' in ad_info["item"]["address"].lower():
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

                    for param in param_dict:
                        data[param] = param_dict[param]

                    with self.lock:
                        log.logger.info('Полученные данные объявления {}'.format(data))
                        self.db.insert_data(data)

            except: log.logger.error('Ошибка при сохранении данных\n{}'.format(traceback.format_exc()))
            finally:
                time_pause = time_wait()
                log.logger.info(f'Ожидание: {time_pause} сек')
                time.sleep(time_pause)

    @log.logger.catch
    def checkNumAds(self):
        log.logger.info('Формирование очереди ссылок')
        startBrowser(self)
        for search_link in self.search_links:
            check_count_ad_link = search_link
            self.driver.get(check_count_ad_link)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            j = json.loads(soup.text)
            total_ads = j['totalCount']
            minPrice_filter = 0
            maxPrice_filter = 0
            step_price = 1000000
            if total_ads > 5000:
                result_ads = 0
                maxPrice_filter += step_price
                while result_ads < total_ads:
                    soup = j = ''
                    try:
                        link = f'{search_link}&pmin={minPrice_filter}&pmax={maxPrice_filter}'
                        self.driver.get(link)
                        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        j = json.loads(soup.text)
                    except: 
                        log.logger.info('Не удалось получить данные')
                        continue
                    count_ads = j['totalCount']
                    if (count_ads in range(4000, 5000) and (total_ads - result_ads) > 5000) or (result_ads + count_ads) >= total_ads:
                        if (count_ads % 50)  != 0:
                            for p in range(count_ads//50 + 1):
                                self.search_links_list.put(f'{link}&p={p+1}')
                        elif (count_ads % 50)  == 0:
                            for p in range(1, count_ads//50):
                                self.search_links_list.put(f'{link}&p={p+1}')
                        log.logger.info(f'В очередь добавлены ссылки с диапозном цен: {minPrice_filter} - {maxPrice_filter}')
                        step_price = 1000000
                        minPrice_filter = maxPrice_filter + 1
                        maxPrice_filter += step_price
                        result_ads += count_ads
                    elif count_ads > 5000:
                        step_price //= 2
                        maxPrice_filter = maxPrice_filter - step_price
                    elif 3000 < count_ads < 4000:
                        maxPrice_filter += step_price
                    elif count_ads < 3000:
                        step_price *= 2
                        maxPrice_filter += step_price

            else: 
                if (total_ads % 50)  != 0:
                    for p in range(total_ads//50 + 1):
                        self.search_links_list.put(f'{check_count_ad_link}&p={p+1}')
                elif (total_ads % 50)  == 0:
                    for p in range(1, total_ads//50):
                        self.search_links_list.put(f'{check_count_ad_link}&p={p+1}')
        log.logger.info('Завершение формирование очереди ссылок. Закрытие selenium барузера')
        self.driver.close()
        self.driver.quit()
        # return search_links_list

    def startProcess(self):
        procs = []
        for i in range(datas.ParseSettings().num_process):
            proc = Process(target=beginning_programm, args=(self,), name=f'Process-{i+1}')
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

if __name__ == "__main__":
    carprice = AvitoRealty()
    carprice.start()