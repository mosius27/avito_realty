

def createSearchLink(settings, category, location):
    search_link = f'https://www.avito.ru/web/1/js/items?_=&{settings["Категории"][category]["value"]}&{settings["Локация"][location]["value"]}'

    return search_link