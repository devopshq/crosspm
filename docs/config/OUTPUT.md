Output
======
<!--ts-->
   * [Output](#output)
      * [shell](#shell)
      * [cmd](#cmd)
      * [json](#json)
      * [python](#python)
      * [stdout](#stdout)
      * [lock](#lock)
<!--te-->

Как скачать пакеты понятно, как теперь их дальше использовать? Для этого в **crosspm** есть несколько видов **output**.

Далее будем указывать варианты вызова из командой строки, но такие же варианты допустимо указывать в [файле конфигурации](CONFIG), в секции **output**

Возможно так же создание файла с большим количеством данных, смотри подробнее [output-template](output-template)

## shell
Для использования в linux можно делать вывод формата **shell**:
```bash
crosspm download \
    --config="./crosspm.yaml" \
    --out-format="shell" \
    --output="./paths.sh"
(( $? )) && exit 1

cat ./paths.sh

source './paths.sh'

# Далее будут доступны переменные вида PACKAGE_ROOT, где PACKAGE - имя пакет в dependencies.txt.lock
echo $PACKAGENAME1_ROOT
echo $PACKAGENAME2_ROOT
python $PACKANAME1_ROOT/somepath/inside/file.py
```

Контент файла **paths.sh**:
```bash
PACKAGENAME1_ROOT=/crosspm/cache/pachagename1/branch/version
PACKAGENAME2_ROOT=/crosspm/cache/pachagename2/branch/version
```

## cmd
Для использования в Windows:
```bash
crosspm download ^
    --config=".\crosspm.yaml" ^
    --out-format="cmd" ^
    --output=".\paths.cmd" ^
IF %ERRORLEVEL% NEQ 0 GOTO badexit

CALL ".\paths.cmd"
# Далее будут доступны переменные вида PACKAGE_ROOT, где PACKAGE - имя пакет в dependencies.txt.lock
"%SOMEPACKAGE_ROOT%\converter.exe" ^
    --rules="%OTHERPACKAGE_ROOT\rules"
```
Контент файла **paths.cmd**:
```bash
set SOMEPACKAGE_ROOT=E:\crosspm\cache\packagename2\branch\version
set OTHERPACKAGE_ROOT=E:\crosspm\cache\otherpackage\branch\version
```


## json
```bash
crosspm download \
    --config="./crosspm.yaml" \
    --out-format="json" \
    --output="./paths.json"
(( $? )) && exit 1

cat ./paths.sh
```

Контент файла **paths.json**:
```json
{
 "PACKAGES_ROOT": {
  "OPENSSL_ROOT": "/test/path/package2",
  "BOOST_ROOT": "/test/path/package11"
 }
}
```


## python
[Лучшая практика использования в python](../usage/USAGE-PYTHON)

## stdout
Используется для вывода в stdout, смотри тесты

## lock
Создаёт lock-файл, используется для `crosspm lock` команды
