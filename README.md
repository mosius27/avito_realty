# avito_realty

## Проект по сбору данных из объявлений с авито в категории недвижимость

**Для использования используется:**
- selenium chromedriver версии 103.0.5060.134

**Подключаемые python библиотеки:**
- requests
- bs4
- pyyaml
- selenium
- pydantic
- psycopg2
- loguru
- sqlalchemy
- sqlalchemy-migrate

Данные для доступа к БД заполняются в файле **parse_settings.yml**  
Категория и город поиска выбираются в файлах **locations.yml** и **categories.yml**
