Frequently Asked Questions
==========================

## Как запретить в конфиге рекурсивное выкачивание пакетов?
Можно задать неправильные имена файлов dependencies, тогда он не найдет их и не пойдет глубже
```yaml
cpm:
  dependencies: no-dependencies.txt
  dependencies-lock: no-dependencies.txt.lock
```
И вызывать с указанием правильного файла:
```bash
crosspm download --depslock-path=./dependencies.txt.lock
```

## CrossPM вылетает с ошибкой при поиске в репозитории с анонимным доступом (type: artifactory-aql)
Это ограничение запросов AQL в Artifactory - их возможно использовать только с авторизацией. Добавьте в конфиг любые учетные данные для доступа к этим репозиториям

## Как отфильтровать пакеты, чтобы выбирались только БЕЗ feature в версии?
Если формат версии в конфиге определен так:
```yaml
 columns:
  version: "{int}.{int}.{int}[-{str}]"
```
то в dependencies можно указать, что необязательной части шаблона быть не должно. Для этого нужно добавить разделитель из необязательной части в конце маски версии. Несколько вариантов для примера:
```
PackageName    *-         R14.1    >=snapshot
PackageName    *.*.*-     R14.1    >=snapshot
PackageName    14.*.*-    R14.1    >=snapshot
```

## А как отфильтровать пакеты, чтобы выбирались ТОЛЬКО feature версии?
Если формат версии в конфиге определен так:
```yaml
 columns:
  version: "{int}.{int}.{int}[-{str}]"
```
то в dependencies можно указать, что необязательная часть шаблона должна быть. Для этого нужно добавить эту необязательную часть в конце маски версии. В таком случае CrossPM не будет брать версии без feature. Несколько вариантов для примера:
```
Agent    *-*            R14.1    >=snapshot
Agent    *-develop      R14.1    >=snapshot
Agent    *.*.*-*        R14.1    >=snapshot
Agent    14.*.*-*       R14.1    >=snapshot
Agent    14.*.*-CERT*   R14.1    >=snapshot
```

## Как скачать два пакеты с разной версией, но один именем?

Нужно создать "псевдоуникальное имя пакета". Пример файла **dependencies.txt.lock**
```
PackageRelease17 Package 17.0.*
PackageRelease161 Package 16.1.*
OtherPackage OtherPackage *
```
И добавить в конфиг строки

```yaml
columns: "*uniquename, package, version" # Указание в какой колонке указано имя пакета

output: # Для упрощения дебага в stdout
  tree:
    - uniquename: 25
    - version: 0
```


## Один модуль ищется 5 минут, как ускорить поиск? (type: artifactory)
Данная проблема могла наблюдаться в адаптере **artifactory**, нужно поменять его на **artifactory-aql**
```yaml
type: artifactory-aql
```

## Как вынести пароль из файла конфигурации?
С помощью [разделения на два файла конфигурации и использования import](config/IMPORT)


## Как сделать проверку что все используемые пакеты имеют одинаковую версию? Например, что все используют последнюю версию openssl?

Если нужно проверить, что все пакеты используют одну версию пакетов, **но** загрузить только файлы, указанные непосредственно в **dependencies.txt**, можно поступить следующим образом:
1. [Разделить файлы конфигурации](config/IMPORT) на **crosspm.main.yaml**, **crosspm.download.yaml**, **crosspm.lock.yaml**
2. В **lock**-конфигурации указать существующий **dependencies.txt.lock**
3. В **download**-конфигурации указать НЕ существующий **no-dependencies.txt.lock**
4. Запустить crosspm с указанием разных конфигураций:

```bash
# CrossPM: lock and recursive check packages
# Попытается сделать lock-файл для пакетов из dep.txt, при этом проверит его зависимости на использование одной версии пакетов
crosspm lock \
    dependencies.txt dependencies.txt.lock \
    --recursive \
    --options cl="gcc-5.1",arch="x86_64",os="debian-8" \
    --config=".\crosspm.lock.yaml"
(( $? )) && exit 1

# CrossPM: downloading packages
# Скачает только пакеты, которые указаны в dependencies.txt
crosspm download \
    --config=".\crosspm.download.yaml" \
    --lock-on-success \
    --deps-path=".\dependencies.txt" \
    --out-format="cmd" \
    --output=".\klmn.cmd" \
    --options cl="gcc-5.1",arch="x86_64",os="debian-8" \
(( $? )) && exit 1
```
