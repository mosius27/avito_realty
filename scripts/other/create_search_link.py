# -*- coding: utf-8 -*-

def createSearchLink(settings, categories, locations):
    search_links = []
    for location in locations:
        for category in categories:
            search_links.append(f'https://www.avito.ru/web/1/js/items?_=&categoryId={settings["Категории"][category]["value"]}&locationId={settings["Локация"][location]["value"]}&radius=0')

    return search_links