# encoding utf-8

import yaml
import os
import time
import logging
import multiprocessing

def initLogger(path: str, logLvl: str):
    with open(path, 'w', encoding='utf-8') as file: pass

    logger = logging.getLogger(__name__)
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

class Beginnig_browser():

    def chrome(proxy: str = None, settings_path: str = f'{os.path.dirname(os.path.abspath(__file__))}\\settings debug.yml', logLvl: str = 'debug', logPath: str = f"{os.path.dirname(os.path.abspath(__file__))}\\logs\\{multiprocessing.current_process().name}.log", *args, **kwargs):
        from selenium.webdriver import Chrome
        from selenium.webdriver import ChromeOptions as Options
        import sys

        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        extentsion = None
        options = Options()

        logger = initLogger(logPath, logLvl=logLvl)
        
        logger.debug('Загрузка настроек запуска selenium браузера chrome')
        with open(settings_path, 'r') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)['chrome']
            
        # Добавление аргументов запуска для браузера
        if proxy != None:
            logger.debug('Добавление прокси '.format(proxy))
            from proxy import create_ext
            if len(proxy.split(':')) == 4:
                proxy = proxy.split(':')
                extentsion = create_ext('./scripts/chrome_proxy.zip', proxy[0], proxy[1], proxy[2], proxy[3])
                options.add_extension(extentsion)
            if len(proxy.split(':')) == 2: options.add_argument(f'--proxy-server={proxy}')

        for arg in config['arguments']:
            logger.debug('Добавление аргументов запуска {}'.format(arg))
            keys = config['arguments'][arg]
            if keys['activity'] == True:
                if len(keys) < 3:
                    options.add_argument(f'{keys["name"]}')
                    continue
                options.add_argument(f'{keys["name"]}={keys["value"]}')

        prefs_dict = {}
        for pref in config['experimental option']:
            keys = config['experimental option'][pref]
            try:
                if keys['activity'] == True and keys['value'] != 'None':
                    try: prefs_dict[keys['category']][keys['name']] = keys['value']
                    except:
                        prefs_dict[keys['category']] = {}
                        prefs_dict[keys['category']][keys['name']] = keys['value']
                elif keys['activity'] == True and keys['value'] == 'None':
                    try: prefs_dict[keys['category']].append(keys['value'])
                    except: 
                        prefs_dict[keys['category']] = []
                        prefs_dict[keys['category']].append(keys['name'])
            except: pass

        for key in list(prefs_dict.keys()):
            logger.debug('Добавление к selenium драйверу эксперементальной опции {}'.format(key))
            options.add_experimental_option(key, prefs_dict[key])
            
        driver = Chrome(executable_path=f'{os.path.dirname(os.path.abspath(__file__))}\\chromedriver.exe'.replace('\\', '/'), options=options)

        # time.sleep(9999)

        return driver

if __name__ == "__main__":
    import time
    driver = Beginnig_browser.chrome()# , settings_path = f'{os.path.dirname(os.path.abspath(__file__))}\\settings.yml')
    time.sleep(99999)