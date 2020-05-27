Output template
===============
<!--ts-->
   * [Output template](#output-template)
      * [Доступные встроенные шаблоны](#доступные-встроенные-шаблоны)
         * [crosspm.template.ALL_YAML](#crosspmtemplateall_yaml)
         * [crosspm.template.GUS - Global Update Server](#crosspmtemplategus---global-update-server)
      * [Вызов для своего шаблона](#вызов-для-своего-шаблона)
      * [Распространение шаблонов через pypi](#распространение-шаблонов-через-pypi)
<!--te-->

`crosspm` умеет выводить информацию о скачанных\найденных пакетов в разные форматы, с помощью `jinja2`-шаблонов

Генерация шаблонов доступна в командах `lock` и `download`


## Доступные встроенные шаблоны
### crosspm.template.ALL_YAML
Можно вывести всю инфомацию о пакете в `yaml`-файл по формату ниже.

Для этого нужно вызывать:
```bash
crosspm download --deps-path dependencies.txt --config config.yaml --out-format jinja --output yaml.yaml --output-template crosspm.template.ALL_YAML
```

```yaml
- 'name': 'boost'
  'packed_path': 'C:\crosspm\archive\boost\1.64-pm-icu\1.64.388\vc140\x86_64\win\boost.1.64.388.tar.gz'
  'unpacked_path': 'C:\crosspm\cache\boost\1.64-pm-icu\1.64.388\vc140\x86_64\win'
  'duplicated': 'C:\crosspm\cache\boost\1.64-pm-icu\1.64.388\vc140\x86_64\win'
  'url': 'https://repo.artifactory.com/artifactory/libs-cpp-release.snapshot/boost/1.64-pm-icu/1.64.388/vc140/x86_64/win/boost.1.64.388.tar.gz'
  'md5': 'c3140673778ba01eed812304da3a5af9'
  'params':
    'osname': 'win'
    'branch': '1.64-pm-icu'
    'package': 'boost'
    'server': 'https://repo.artifactory.com/artifactory'
    'compiler': 'vc140'
    'filename': 'boost.1.64.388.tar.gz'
    'version': '1.64.388'
    'repo': 'libs-cpp-release.snapshot'
    'arch': 'x86_64'
- 'name': 'log4cplus'
  'packed_path': 'C:\crosspm\archive\log4cplus\1.2.0-pm\1.2.0.149\vc140\x86_64\win\log4cplus.1.2.0.149.tar.gz'
   ...
```
### crosspm.template.GUS - Global Update Server
Можно вызвать crosspm, чтобы он нашел нужные пакеты и сгенерировал `GUS` manifest.yaml.

```bash
crosspm download --deps-path dependencies.txt --config config.yaml --out-format jinja --output yaml.yaml --output-template crosspm.template.GUS
```

```yaml
artifacts:
  - src_path : "/boost/1.64-pm-icu/1.64.388/vc140/x86_64/win/boost.1.64.388.tar.gz"
    dest_path: "boost.1.64.388.tar.gz"
    md5hash: "c3140673778ba01eed812304da3a5af9"
    version: "1.64.388"
    src_repo_name: "libs-cpp-release.snapshot"
  - src_path : "/log4cplus/1.2.0-pm/1.2.0.149/vc140/x86_64/win/log4cplus.1.2.0.149.tar.gz"
    dest_path: "log4cplus.1.2.0.149.tar.gz"
    md5hash: "90bb506b44c4e388c565a0af435f8c71"
    version: "1.2.0.149"
    src_repo_name: "libs-cpp-release.snapshot"
  - src_path : "/poco/1.7.9-pm/1.7.9.315/vc140/x86_64/win/poco.1.7.9.315.tar.gz"
    dest_path: "poco.1.7.9.315.tar.gz"
    md5hash: "1e9c92f79df6cfd143c7d99c3d7cc868"
    version: "1.7.9.315"
    src_repo_name: "libs-cpp-release.snapshot"
```

## Вызов для своего шаблона
Можно сделать любой свой шаблон и генерировать на выход файлы

В шаблон передаётся переменная `packages`, которая содержит верхний уровень всех пакетов (подробнее смотри [usage python](../usage/USAGE-PYTHON))

Например, мы хотим получить следующий формат для передачи в скрипт установки `deb`-пакетов

Для этого, мы создаём файл `deb.j2` со следующим содержимым

```
{% for package in packages.values() %}
{{package.pkg.name}} = {{package.get_params(merged=True)['version']}}
{% endfor %}
```

Вызываем `crosspm`:

```bash
download --deps-path dependencies.txt --out-format jinja --output depends.txt --output-template /path/to/template/deb.j2
```

Получаем на выходе:

```
package-name1 = 1.2.123
package-name2 = 1.2.111
```


## Распространение шаблонов через pypi
Допустимо шаблоны распространять через `pypi`-пакеты (смотри подробнее [cpmconfig](../cpmconfig))

Для этого, нужно вызвать `crosspm` со следующими параметрами

```bash
download --deps-path dependencies.txt --out-format jinja --output depends.txt --output-template module1.module2.VARIABLE_NAME
```

где:
- `module1.module2` - имя модулей (с файлами `__init__.py`)
- `VARIABLE_NAME` - имя переменной, в которой хранится полный (или относительный текущей директории) путь до jinja-шаблона

Т.е. в обычном python-файле у вас должно работать следующее:
```python
from module1.module2 import VARIABLE_NAME
print(VARIABLE_NAME)
#C:\Python34\Lib\site-packages\module1\module2\my_template_name.j2
```

Пример распространения и настройки смотри в `crosspm.template`
