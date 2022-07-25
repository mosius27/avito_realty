# -*- coding: utf-8 -*-

import time
import random
import logging
import other.read_write_files as working_with_file
import other.create_search_link as create_search_link
import os
import sys
import traceback
import multiprocessing
from multiprocessing import Process, RLock
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def time_wait(delay):
    return random.randint(delay['from'], delay['to'])

def start_browser(self):
    from browser import Beginnig_browser

    try: 
        self.driver.close()
        self.driver.quit()
    except: pass

    if self.proxyes != []:
        proxy = self.proxyes.pop(0)
        self.proxyes.append(proxy)
        print(proxy)
        self.driver = Beginnig_browser.chrome(proxy=proxy, settings_path=self.paths['browser settings'])
    else: self.driver = Beginnig_browser.chrome( settings_path=self.paths['browser settings'])
    return self.driver

def Backup(self, backup, paths: str):
    import shutil
    for file in backup['backup files']:
        try: shutil.copy(paths[file], backup['backup folder'])
        except: self.logger.info(f'Файл {paths[file].split("/")[-1]} по указанному пути {paths[file]} не обнаружен')

def work_process(self, target):
    self.logger = AvitoRealty.initLogger(path=f"{os.path.abspath(self.paths['log folder'])}\\{multiprocessing.current_process().name}.log", logLvl=self.parse_settings['log level'])
    with self.lock:
        if self.method.value == 'selenium':
            self.driver = start_browser(self)
    if target == 'get ads':
        if self.numCycles.value == 0:
            self.logger.info('Начало выполнения цикла пока не будет закрыта программа')
            while True:
                self.get_and_save_links_on_ad()
                self.logger.info(f'Цикл сбора ссылок завершен. Ожидание {self.parse_settings["cycles"]["delay_between_cycles"]} сек.')
                self.event.set()
                time.sleep(self.parse_settings["cycles"]["delay_between_cycles"])
        elif self.numCycles.value > 0:
            self.logger.info('Начало выполнения {} кол-ва циклов'.format(self.numCycles.value))
            for i in range(int(self.numCycles.value)):
                self.get_and_save_links_on_ad()
                self.logger.info(f'Цикл сбора ссылок завершен. Ожидание {self.parse_settings["cycles"]["delay_between_cycles"]} сек.')
                self.event.set()
                time.sleep(self.parse_settings["cycles"]["delay_between_cycles"])
        
        elif self.numCycles.value < 0:
            self.logger.info('Значение cycles/nums в файле self.parse_settings не может быть отрицательным')

    elif target == 'ad info':
        self.event.wait()
        self.ads = read_write_data(self, path=self.paths['ads link'], action='read')
        self.get_and_save_ads_info()

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

    def __init__(self):
        self.parse_settings = working_with_file.load_yaml('./settings/parse_settings.yml')
        self.paths = self.parse_settings['paths']

        # при выставлении в настройках True будут создаваться резервные копии указанных файлов
        self.lock = RLock()

        manager = multiprocessing.Manager()

        self.proxyes = manager.list(read_write_data(self, path=self.paths['proxy'], action='read'))
        self.proxyes = read_write_data(self, path=self.paths['proxy'], action='read')
        self.generator_search_link = read_write_data(self, path=self.paths['create search link settings'], action='read')
        self.search_link = create_search_link.createSearchLink(self.generator_search_link)
        self.multiprocess_settings = read_write_data(self, path=self.paths['multiprocess settings'], action='read')
        # self.search_links = read_write_data(self, path=self.parse_settings['paths']['links for get data'], action='read')
        self.header = manager.Value('', value=self.parse_settings['headers'])
        if self.parse_settings['result format'] == 'csv' and (self.parse_settings['clear prev result'] == True or f'{self.paths["result"].split("/")[-1]}.csv' not in os.listdir('./data/result/')):
            working_with_file.create_csv(f'{self.paths["result"]}.csv', self.header)
        
        if self.parse_settings['result format'] == 'excel' and (self.parse_settings['clear prev result'] == True or f'{self.paths["result"].split("/")[-1]}.xlsx' not in os.listdir('./data/result/')):
            working_with_file.create_excel(path=f'{self.paths["result"]}.xlsx')
            working_with_file.write_line_excel(path=f'{self.paths["result"]}.xlsx', var=self.header.value, num_row=1)

        if self.parse_settings['result format'] == 'json' and (self.parse_settings['clear prev result'] == True or f'{self.paths["result"].split("/")[-1]}.json' not in os.listdir('./data/result/')):
            read_write_data(self, path=f'{self.paths["result"]}.json', var=[], action='write')

        self.numCycles = manager.Value('', self.parse_settings['cycles']['nums'])
        self.delay = manager.Value('', self.parse_settings['delay'])
        self.method = manager.Value('', self.parse_settings['method'])

    def cycle(self):
        if self.method.value == 'selenium':
            self.driver = start_browser(self)

        queue_parse = self.parse_settings['cycles']['run_queue']
        self.event.set()
        for i in queue_parse:
            if i == 'get ads':
                self.get_and_save_links_on_ad()
            elif i == 'ad info':
                self.ads = read_write_data(self, path=self.paths['ads link'], action='read')
                self.get_and_save_ads_info()

        self.logger.info(f'Цикл сбора ссылок завершен. Ожидание {self.parse_settings["cycles"]["delay_between_cycles"]} сек.')
        time.sleep(self.parse_settings["cycles"]["delay_between_cycles"])

    def start(self):
        self.event = multiprocessing.Event()
        if self.multiprocess_settings['use multiprocessing'] == False:
            self.logger = AvitoRealty.initLogger(path=f"{os.path.abspath(self.paths['log folder'])}\\{multiprocessing.current_process().name}.log", logLvl=self.parse_settings['log level'])
            self.logger.info('Начало выполнения программы в один процесс')
            if self.numCycles.value == 0:
                self.logger.info('Начало выполнения цикла пока не будет закрыта программа')
                while True:
                    self.cycle()

            elif self.numCycles.value > 0:
                self.logger.info('Начало выполнения {} кол-ва циклов'.format(self.numCycles.value))
                for i in range(int(self.numCycles.value)):
                    self.cycle()
            
            elif self.numCycles.value < 0:
                self.logger.info('Значение cycles/nums в файле self.parse_settings не может быть отрицательным')
                exit()
        
        else:
            if self.multiprocess_settings['num process'] > 1:
                self.process()
            elif self.multiprocess_settings['num process'] == 1:
                self.logger = AvitoRealty.initLogger(path=f"{os.path.abspath(self.paths['log folder'])}\\{multiprocessing.current_process().name}.log", logLvl=self.parse_settings['log level'])
                self.logger.info('Начало выполнения программы в один процесс')
                if self.numCycles.value == 0:
                    self.logger.info('Начало выполнения цикла пока не будет закрыта программа')
                    while True:
                        self.cycle()

                elif self.numCycles.value > 0:
                    self.logger.info('Начало выполнения {} кол-ва циклов'.format(self.numCycles.value))
                    for i in range(int(self.numCycles.value)):
                        self.cycle()
                
                elif self.numCycles.value < 0:
                    self.logger.info('Значение cycles/nums в файле self.parse_settings не может быть отрицательным')
                    exit()

            if self.multiprocess_settings['num process'] < 1:
                self.logger.error('Не верно указано количество процессов: {}'.format(self.multiprocess_settings['num process']))
                exit()


    # Функция по сбору и сохранению данных об объявлении
    def get_and_save_ads_info(self):
        from avito import Check_ad

        processed = read_write_data(self, path=self.paths['processed links'], action='read')
        
        while self.ads:
            
            if multiprocessing.current_process().is_alive() == False:
                multiprocessing.current_process().terminate
            with self.lock:
                self.event.wait()
                self.ads = read_write_data(self, path=self.paths['ads link'], action='read')
                if len(self.ads) == 0: 
                    self.logger.info('Список объявлений пуст')
                    break
                ad = self.ads.pop(0)
                self.logger.info('Проверяемое объявление {}'.format(ad))
                read_write_data(self, path=self.paths['ads link'], var=self.ads, action='write')

                processed = read_write_data(self, path=self.paths['processed links'], action='read')
                processed.append(ad)
                read_write_data(self, path=self.paths['processed links'], var=processed, action='write')

            try: ad_info = Check_ad.check_ad_browser(url=ad, driver=self.driver)
            except:
                self.logger.error('Не удалось получить данные объявления {}'.format(traceback.format_exc()))
                time_pause = time_wait(self.delay.value)
                self.logger.info(f'Ожидание: {time_pause} сек')
                time.sleep(time_pause)
                continue
            try:
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
                        header = self.header.value.split(';')
                        param_dict = {}
                        for param in params:
                            if param["title"] not in header:
                                self.header.value += f';{param["title"]}'
                                working_with_file.write_line_excel(path=f'{self.paths["result"]}.xlsx', var=self.header.value, num_row=1)
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
                    
                    ad_dict = {}
                    for value in self.header.value.split(';'):
                        ad_dict[value] = ''

                    ad_dict['Дата публикации'] = (datetime.utcfromtimestamp(ad_info["contextItem"]["date_unix"]) + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S') 
                    ad_dict['Заголовок'] = ad_info["contextItem"]["title"]
                    ad_dict['Описание'] = description
                    ad_dict['Цена'] = ad_info["window.dataLayer"]["itemPrice"]
                    ad_dict['Регион'] = region
                    ad_dict['Город'] = ad_info["item"]["location"]["name"]
                    ad_dict['Адрес'] = ad_info["item"]["address"]
                    ad_dict['Url'] = ad
                    ad_dict['Изображения'] = images_str

                    for param in list(param_dict):
                        ad_dict[param] = param_dict[param]

                    with self.lock:
                        self.logger.info('Полученные данные объявления {}'.format(ad_dict))
                        if self.parse_settings['result format'] == 'csv':
                            self.logger.info('Сохранение данных в файл {}'.format(f'{self.paths["result"]}.csv'))
                            read_write_data(self, path=f'{self.paths["result"]}.csv', var=ad_dict, header=self.parse_settings['headers'], action='write')

                        if self.parse_settings['result format'] == 'excel':
                            self.logger.info('Сохранение данных в файл {}'.format(f'{self.paths["result"]}.xlsx'))
                            line = ''
                            for key in list(ad_dict.keys()):
                                line += f'{ad_dict[key]};'
                            read_write_data(self, path=f'{self.paths["result"]}.xlsx', var=line, action='write')

                        if self.parse_settings['result format'] == 'json':
                            self.logger.info('Сохранение данных в файл {}'.format(f'{self.paths["result"]}.json'))
                            data = read_write_data(self, path=f'{self.paths["result"]}.json', action='read')
                            data.append(ad_dict)
                            read_write_data(self, path=f'{self.paths["result"]}.json', var=data, action='write')

            except: self.logger.error('непредвиденная ошибка при сохранении данных\n{}'.format(traceback.format_exc()))
            finally:
                time_pause = time_wait(self.delay.value)
                self.logger.info(f'Ожидание: {time_pause} сек')
                time.sleep(time_pause)

    # Функция по сбору и сохранению ссылок на объявления
    def get_and_save_links_on_ad(self):
        from avito import Get_ads

        if self.parse_settings['num_pages'] > 0:
            ads = read_write_data(self, path=self.paths['ads link'], action='read')
            if len(ads) == 0:
                self.event.clear()
            else:
                self.event.set()
            processed = read_write_data(self, path=self.paths['processed links'], action='read')
            for page in range (1, self.parse_settings['num_pages'] + 1):
                self.logger.info(f'Номер страницы: {page}')
                try:
                    url = f'{self.search_link}&p={page}'

                    if self.method.value == 'selenium':
                        newAds, is_lastPage = Get_ads.get_ads_browser(url=url, driver=self.driver)

                    for ad in newAds:
                        if ad not in ads:
                            ads.append(ad)

                    self.logger.info(f'Всего ссылок на объявления: {len(ads)}')
                except: self.logger.info('Не удалось загрузить страницу\n{}'.format(traceback.format_exc()))
                finally:
                    self.event.clear()
                    if self.parse_settings['check new ad on processed'] == True:
                        processed = read_write_data(self, path=self.paths['processed links'], action='read')
                        ads = list(set(ads) - set(processed))
                    self.logger.debug('Сохраняемые объявления {}'.format(ads))
                    read_write_data(self, path=self.paths['ads link'], var=ads, action='write')
                    if len(ads) == 0:
                        self.event.clear()
                    else:
                        self.event.set()
                    time_pause = time_wait(self.delay.value)
                    self.logger.info(f'Ожидание: {time_pause} сек')
                    time.sleep(time_pause)
                    if is_lastPage: break

        if self.parse_settings['num_pages'] == 0:
            startPage = 1
            while True:
                ads = read_write_data(self, path=self.paths['ads link'], action='read')
                processed = read_write_data(self, path=self.paths['processed links'], action='read')
                self.logger.info(f'Номер страницы: {page}')
                try:
                    url = f'{self.search_link}&p={page}'

                    if self.method.value == 'selenium':
                        newAds, is_lastPage = Get_ads.get_ads_browser(url=url, driver=self.driver)

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
                    self.event.clear()
                    if self.parse_settings['check new ad on processed'] == True:
                        processed = read_write_data(self, path=self.paths['processed links'], action='read')
                        ads = list(set(ads) - set(processed))
                    self.logger.debug('Сохраняемые объявления {}'.format(ads))
                    read_write_data(self, path=self.paths['ads link'], var=ads, action='write')
                    if len(ads) == 0:
                        self.event.clear()
                    else:
                        self.event.set()
                    time_pause = time_wait(self.delay.value)
                    self.logger.info(f'Ожидание: {time_pause} сек')
                    time.sleep(time_pause)
                    if is_lastPage: break
        else:
            pass

        # Перемешивать собранные объявления перед сохранением
        if self.parse_settings['shuffle ads'] == True:
            random.shuffle(ads)

        read_write_data(self, path=self.paths['ads link'], var=ads, action='write')

    def process(self):
        procs = []
        for i in range(self.multiprocess_settings['num process']):
            if i == 0:
                proc = Process(target=work_process, args=(self, 'get ads',), name=f'Process-{i+1}')
            else:
                proc = Process(target=work_process, args=(self, 'ad info',), name=f'Process-{i+1}')
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

if __name__ == "__main__":
    carprice = AvitoRealty()
    carprice.start()