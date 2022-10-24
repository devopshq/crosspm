<!--ts-->
      * [Использование CrossPM для поиска "пакетов, использующих данный пакет"](#использование-crosspm-для-поиска-пакетов-использующих-данный-пакет)
      * [Использование](#использование)
         * [Примечания](#примечания)
      * [Пример поиска deb-пакетов](#пример-поиска-deb-пакетов)
      * [Пример поиска tar-gz crosspm package](#пример-поиска-tar-gz-crosspm-package)
<!--te-->
## Использование CrossPM для поиска "пакетов, использующих данный пакет"

Иногда есть необходимость найти "пакеты, испольщующие данный пакет". Например, если вы нашли баг в пакете, нужно забанить так же пакеты, которые используют этот "плохой" пакет

За поиск отвечает секция `usedby` конфигурации
```yaml
parsers:
  common:
    usedby:
      AQL:
        "@dd.{package}.version": "{version}"
        "@dd.{package}.operator": "="

      property-parser:
        "deb.name": "package"
        "deb.version": "version"
        "qaverdict": "qaverdict"

      path-parser: 'https://(?P<server>.*?)/artifactory/(?P<repo>.*?)/(?P<package>.*?)/(?P<branch>.*?)/(?P<version>.*?)/(?P<compiler>.*?)/(?P<arch>.*?)/(?P<osname>.*?)/.*.tar.gz'

  # может быть и в секции конкретного parser
  artifactory:
    usedby: ...
```

`AQL` - тут находится правила для непосредственного поиска. Быстрее всего выполнить поиск по `Artifactory Properties` (**они должны быть выставлены предварительно сторонним инструментом)

При нахождении пакета, мы можем попробовать найти и пакеты, которые зависят от него тоже, но для этого надо вытащить колонки из артефакта в Артифактории
- `property-parser` - берем колонки из `property` Артифактория
- `path-parser` - **в разработке** берем колонки из пути к файлу в Артифактории

## Использование
Для поиска нужно создать файл `dependencies.txt` с примерно следующим содержимым и запустить поиск

```
# package version branch
packagename 1.2.3  master
```

```bash
crosspm usedby -c config.yaml
```

### Примечания
- **ВАЖНО** - `crosspm` не включает указанный в `dependencies.txt` пакет, чтобы и его найти - нужно использовать команду `crosspm lock` и соединить результаты, тогда будет "полная" картина
- Удобно получать список пакетов через [python-интерфейс](./USAGE-PYTHON) у `crosspm` или через стандартные [jinja-шаблоны](../config/output-template)

## Пример поиска deb-пакетов
Допустим, у нас есть пакеты, с примерной иерархией зависимостей:
```
package1 1.0.1
  - package2 2.0.2
  - package3 3.0.3
    - package31 31.0.1
    - package32 32.0.2
```

Мы проставляем при загрузке в артифакторий дополнительные свойства, по формату (пример для `package3`)
```
dd.package31.version: 31.0.1
dd.package31.operator: =
dd.package32.version: 32.0.2
dd.package32.operator: =
```

Теперь, если мы находит баг в пакете `package31`, мы делаем поиск (смотри выше пример cli-запуска)
```bash
>> cat dependencies.txt
# package version
package31 31.0.1

# Примерный вывод в stdout
>> crosspm usedby
Dependencies tree:
- <root>
  - package3   3.0.3
    - package1  1.0.1
```

## Пример поиска tar-gz crosspm package
Допустим, у нас есть пакеты, с примерной иерархией зависимостей (с помощью файлов `dependencies.txt.lock`, но проставление свойств должно быть реализовано сторонним инструментом)
```
package1 1.0.1
  - package2 2.0.2
  - package3 3.0.3
    - package31 31.0.1
    - package32 32.0.2
```

Мы проставляем при загрузке в артифакторий дополнительные свойства, по формату (пример для `package3`)
```
ud.package31.version: 31.0.1
ud.package32.version: 32.0.2
```

Теперь, если мы находит баг в пакете `package31`, мы делаем поиск (смотри выше пример cli-запуска)
```bash
>> cat dependencies.txt
# package version
package31 31.0.1

# Примерный вывод в stdout
>> crosspm usedby
Dependencies tree:
- <root>
  - package3   3.0.3
    - package1  1.0.1
```
