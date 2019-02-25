# orbicreo

## Установка

#### Debian/Ubuntu
```bash
#!/bin/bash

git clone https://bitbucket.org/razykov/orbicreo.git

cd orbicreo
./install/mkdeb.py
dpkg -i orbicreo.deb
```
#### Others
```bash
#!/bin/bash

git clone https://bitbucket.org/razykov/orbicreo.git

cd orbicreo
mkdir /usr/bin/_orbicreo
cp -R source/* /usr/bin/_orbicreo
mv /usr/bin/_orbicreo/orbicreo /usr/bin/
```


## Написание рецептов сборки

### Именование файлов рецептов

Файлы рецептов хранятся в директории recipes. Имя файла рецепта должно удовлетворять следующему регулярному выражению `(linux|windows|bsd|minix)_(86|64).json`. Так же допускается файл с именем **`general.json`**, в котором хранятся поля общие для всех архитектур и ОС. Важно: поля из рабочего рецепта накладываются на поля из **`general.json`**. В случае коллизии полей в файле  **`general.json`** и файле собираемого рецепта они(поля) объединяются по следующим правилам:

1. строки заменяются 
2. списки объединяются
3. к вложенным элементам применяются все три правила


### Значение полей
***** помечены обязательные поля

* **`project_name*`** {string} - имя проекта
* **`project_type*`** {string} - тип проекта **`lib`|`app`**
* **`compiler_name`** {string} - название используемого компилятора. По-умолчанию используется **`gcc`**
* **`compiler_std`** {string} - стандарт языка **`с89`, `с99`, `gnu99`**. По-умолчанию используется **`gnu99`**
* **`compiler_options`** {list of strings} - список опций компилятора. Опции указываются без знака минус **`-`**
* **`dependency_includes`** {list of strings} - список заголовочных файлов C/C++ вставляемых перед экспортируемыми объявлениями заголовочных файлов библиотеки. Параметр не имеет эффекта для проектов с типом **`app`**. Экспорт происходит для объявлений, помеченных макросами используемыми [libbixi](https://github.com/codemeow/bixi) **`EXPORT`**, **`EXPORT_FROM`**, **`EXPORT_TO`**
* **`export_file_prefix`** {string} - префикс добавляемый к имени создаваемого исполняемого файла
* **`include_dirs`** {list of string} - список директорий с заголовочными файлами **`*.h`**, **`.hpp`**