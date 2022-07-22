# Описание модуля

#* MODULES -------------------------------------------
# Standart
from ast import arg
import zipfile

# Data

# Modules

#* GLOBAL --------------------------------------------
manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    }
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                host: "%s",
                port: parseInt(%s)
            }
        }
    };

chrome.proxy.settings.set({
    value: config,
    scope: "regular"
}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    {urls: ["<all_urls>"]
    },
    ['blocking']
);
"""

#* FUNCTIONS -----------------------------------------
def create_ext(extension_path, *args, **kwargs):

    print(f'Создание прокси-расширения: {args[0]}, {args[1]}, {args[2]}, {args[3]}')

    extension = extension_path

    with zipfile.ZipFile(extension, 'w') as zip:
        zip.writestr('manifest.json', manifest_json)
        zip.writestr('background.js', background_js % (args[0], args[1], args[2], args[3]))


    return extension
#* VARIABLES -----------------------------------------


#* CODE ----------------------------------------------