# -*- coding: utf-8 -*-

from pydantic import BaseModel
import sys
sys.path.append('./')
import scripts.other.read_write_files as working_with_file

class ParseSettings(BaseModel):
    parse_settings = working_with_file.load_yaml('./parse_settings.yml')
    location: int=parse_settings['location']
    category: int=parse_settings['category']
    log_level: str='info'
    deep_scan: bool=parse_settings['deep_scan']
    look_up_date: int=parse_settings['look_up_date']
    result_format: str=parse_settings['result_format']
    save_checked_ads: bool=parse_settings['save_checked_ads']
    check_new_ad_on_processed: bool=parse_settings['check_new_ad_on_processed']
    delay_from: dict=parse_settings['delay']['from']
    delay_to: dict=parse_settings['delay']['to']
    use_proxy: bool=parse_settings['use_proxy']
    work_mode: str=parse_settings['work_mode']

class Paths(BaseModel):
    paths_settings = working_with_file.load_yaml('./settings/paths.yml')
    ads_link: str=paths_settings['ads_link']
    processed_links: str=paths_settings['processed_links']
    browser_settings: str=paths_settings['browser_settings']
    create_search_link_settings: str=paths_settings['create_search_link_settings']
    multiprocess_settings: str=paths_settings['multiprocess_settings']
    proxy: str=paths_settings['proxy']
    log_folder: str=paths_settings['log_folder']

class Ad_Data(BaseModel):
    date_published: str
    title: str
    type_realty: str
    description: str
    price: int
    region: str
    city: str
    address: str
    url: str
    urls_image: str
    params: dict