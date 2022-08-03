# -*- coding: utf-8 -*-

from pydantic import BaseModel
import sys
sys.path.append('./')
import scripts.other.read_write_files as working_with_file

class ParseSettings(BaseModel):
    parse_settings = working_with_file.load_yaml('./parse_settings.yml')
    log_level: str='info'
    deep_scan: bool=parse_settings['deep_scan']
    look_up_date: int=parse_settings['look_up_date']
    save_checked_ads: bool=parse_settings['save_checked_ads']
    check_new_ad_on_processed: bool=parse_settings['check_new_ad_on_processed']
    delay_from: dict=parse_settings['delay']['from']
    delay_to: dict=parse_settings['delay']['to']
    use_proxy: bool=parse_settings['use_proxy']
    work_mode: str=parse_settings['work_mode']
    db_access: dict=parse_settings['db_access']
    use_multiprocessing: bool=parse_settings['use_multiprocessing']
    num_process: int=parse_settings['num_process']

class Paths(BaseModel):
    paths_settings = working_with_file.load_yaml('./settings/paths.yml')
    ads_link: str=paths_settings['ads_link']
    processed_links: str=paths_settings['processed_links']
    browser_settings: str=paths_settings['browser_settings']
    create_search_link_settings: str=paths_settings['create_search_link_settings']
    locations: str=paths_settings['locations']
    categories: str=paths_settings['categories']
    proxy: str=paths_settings['proxy']
    log_folder: str=paths_settings['log_folder']

class Ad_Data(BaseModel):
    Дата_публикации: str
    Заголовок: str
    Тип_недвижимости: str
    Описание: str
    Цена: str
    Регион: str
    Город: str
    Адрес: str
    Url: str
    Изображения: str