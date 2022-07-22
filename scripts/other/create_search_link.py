

def createSearchLink(settings):
    search_link = 'https://www.avito.ru/web/1/js/items?_='
    num = 1
    d1 = {}
    for cat in settings['Категории']:
        print(f'{num} - {cat}')
        d1[str(num)] = cat
        num += 1
    category = input('Выберите раздел поиска: ')

    d2 = {}
    num = 1
    for sub in settings['Категории'][d1[category]]:
        print(f'{num} - {sub}')
        d2[str(num)] = sub
        num += 1

    subCategory = input('Выберите категорию поиска: ')
    search_link += f"&categoryId={settings['Категории'][d1[category]][d2[subCategory]]['categoryId']}"

    l = {}
    num = 1
    for loc in settings['Локация']:
        print(f'{num} - {loc}')
        l[str(num)] = loc
        num += 1
    
    location = input('Выберите локацию поиска: ')
    search_link += f'&locationId={settings["Локация"][l[location]]}'

    return search_link