

def createSearchLink(settings, category, location):
    search_link = f'https://www.avito.ru/web/1/js/items?_=&{settings["Категории"][category]}&{settings["Локация"][location]}'

    return search_link