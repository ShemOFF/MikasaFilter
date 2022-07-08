# MikasaFilter
***
![MikasaFilter](https://citaty.info/files/characters/142539.png "Mikasa")

Фильтр open-source пакетов с внешних репозиториев

## Поддержка пакетных менеджеров
***
- pip (Python)
- npm (Node.js)

## Реализовано
***
- Фиксированная дата фильтрации (стандартное значение до 18.02.2022)
>Все пакеты с зависимостями вышедшие после или равными данной даты не будут доступны для загрузки

- Динамическая дата фильтрации в GET запросе (день, месяц)
>Все пакеты с зависимостями вышедшие после или равными динамической даты не будут доступны для загрузки

- Просмотр доступных библиотек с датой релиза по фильтрации (список, json)
- Просмотр всех библиотек с датой релиза (список, json)

## Планы
***
- Добавление "антирусского" списка библиотек в исключения
- Добавить белый список библиотек в исключения
- maven
- deb
- docker
- Менеджер для конфигурации под конкретный проект

## Фиксированная дата фильтрации
***
Из актуальной даты вычитается значение переменной "DEFAULT_MORATORIUM_DATE" из
"app/project_config.py" (18.02.2022) и предоставляются пакеты с меньшей датой релиза.

## Изменение фиксированной даты фильтрации
***
В "app/project_config.py" изменить значение переменной "DEFAULT_MORATORIUM_DATE"
и перезапустить проект.

Синтаксис "DEFAULT_MORATORIUM_DATE": 'день-месяц-год'.

## Динамическая дата фильтрации
***
Из актуальной даты вычитается день-месяц введение пользователем 
и предоставляются пакеты с меньшей датой релиза.
Вводимые параметры:
- День не больше 31 и не меньше 0
- Месяц не больше 96 и не меньше 0

## Работа фильтра
***
  - ### Фиксированная дата фильтрации:
    - ### pip: 
    ```
    http://<url>:<port>/pypi-api/simple/<package_name>/
    ```
        
    - ### npm:
    ```
    http://<url>:<port>/npm-api/package/<package_name>
    ```
  
  - ### Отображение подходящих пакетов и даты релиза с фиксированной датой фильтрации:
    - ### pip:
      - ### Пользовательское
          ```
          http://<url>:<port>/pypi-api/date-upload-moratorium/<package_name>
          ```
      - ### Json
          ```
          http://<url>:<port>/pypi-api/date-upload-moratorium/json/<package_name>
          ```

    - ### npm:
      - ### Пользовательское
          ```
          http://<url>:<port>/npm-api/date-upload-moratorium/<package_name>
          ```
      - ### Json
          ```
          http://<url>:<port>/npm-api/date-upload-moratorium/json/<package_name>
          ```
    
  - ### Динамическая дата фильтрации:
     - ### pip:
    ```
    http://<url>:<port>/pypi-api/день-месяц/simple/<package_name>
    ```

     - ### npm: 
    ```
    http://<url>:<port>/npm-api/день-месяц/package/<package_name>
    ```
  
  - ### Отображение подходящих пакетов и даты релиза с динамической датой фильтрации:
     - ### pip:
       - ### Пользовательское
       ```
       http://<url>:<port>/pypi-api/день-месяц/date-upload-moratorium/<package_name>
       ```

       - ### Json
       ```
       http://<url>:<port>/pypi-api/день-месяц/date-upload-moratorium/json/<package_name>
       ```
     - ### npm: 
       - ### Пользовательское
       ```
       http://<url>:<port>/npm-api/день-месяц/date-upload-moratorium/<package_name>
       ```
       - ### Json
       ```
       http://<url>:<port>/npm-api/день-месяц/date-upload-moratorium/json/<package_name>
       ```
  - ### Отображение всех пакетов с датой публикации (Без фильтрации)
    - ### pip
    ```
    http://<url>:<port>/pypi-api/date-upload-all/<package_name>
    ```
    - ### npm
    ```
    http://<url>:<port>/npm-api/date-upload-all/<package_name>
    ```
    
## Запуск фильтра
***
- ### Windows:
```bash
# python >= 3.9
 
pip install -r app\requirements.txt
python app\app.py
```

- ### Docker-compose:
```bash
docker-compose up -d
```
## Настройка пакетных менеджеров для работы
***
### __Во всех ниже перечисленных методах можно использовать динамическую фильтрацию, а не фиксированную.__
## pip:

- ### Terminal:

```bash
pip ... --index-url http://<url>:<port>/pypi-api/simple/pycurl/
```

- ### Config:
```bash
# in Windows %USERPROFILE%/pip/pip.conf
vi ~/.pip/pip.conf 

[global]
index-url = http://<url>:<port>/pypi-api/simple
```

## npm:
- ### Terminal:
```bash
npm ... --registry https://<url>:<port>/npm-api/package
```

- ### Config:
```bash
# in Windows %USERPROFILE%/.npmrc
vi ~/.npmrc


registry=https://<url>:<port>/npm-api/package
```
