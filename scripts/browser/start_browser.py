# encoding utf-8

import yaml
import os
import time
import multiprocessing
import other.logger as log
log.Logging()

class Beginnig_browser():

    @log.logger.catch
    def chrome(proxy: str = None, settings_path: str = f'{os.path.dirname(os.path.abspath(__file__))}\\settings debug.yml', logLvl: str = 'debug', logPath: str = f"{os.path.dirname(os.path.abspath(__file__))}\\logs\\{multiprocessing.current_process().name}.log", *args, **kwargs):
        from selenium.webdriver import Chrome
        from selenium.webdriver import ChromeOptions as Options
        import sys

        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        extentsion = None
        options = Options()
        
        with open(settings_path, 'r') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)['chrome']
            
        # Добавление аргументов запуска для браузера
        if proxy != None:
            log.logger.info('добавление прокси {}'.format(proxy))
            from proxy import create_ext
            if len(proxy.split(':')) == 4:
                proxy = proxy.split(':')
                extentsion = create_ext('./scripts/chrome_proxy.zip', proxy[0], proxy[1], proxy[2], proxy[3])
                options.add_extension(extentsion)
            if len(proxy.split(':')) == 2: options.add_argument(f'--proxy-server={proxy}')

        for arg in config['arguments']:
            log.logger.info('Добавление аргумента {}'.format(arg))
            keys = config['arguments'][arg]
            if keys['activity'] == True:
                if len(keys) < 3:
                    options.add_argument(f'{keys["name"]}')
                    continue
                options.add_argument(f'{keys["name"]}={keys["value"]}')

        prefs_dict = {}
        for pref in config['experimental option']:
            log.logger.info('Добавление experimental option: {}'.format(pref))
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
            options.add_experimental_option(key, prefs_dict[key])
            
        log.logger.info('Запуск selenium браузера')
        driver = Chrome(executable_path=f'{os.path.dirname(os.path.abspath(__file__))}\\chromedriver.exe'.replace('\\', '/'), options=options)

        return driver

if __name__ == "__main__":
    import time
    driver = Beginnig_browser.chrome()
    time.sleep(99999)