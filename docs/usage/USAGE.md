<!--ts-->
   * [Usage](./docs/usage/USAGE.md#usage)
         * [crosspm lock](./docs/usage/USAGE.md#crosspm-lock)

<!-- Added by: aburov, at: 2019-01-16T16:33+07:00 -->

<!--te-->
Usage
=======
Идея CrossPM (как пакетного менеджера) примерно такая же, как и других популярных пакетных менеджеров (npm, pyenv, etc).

Можно придерживаться примерно следующего алгоритма:
1. Создаете файл **dependencies.txt** - список пакетов, которые нужно скачать. Поддерживаются маски в версиях, свойства артефактов.
2. Ищем пакеты и фиксируем их командой `crosspm lock` - создает файл **dependencies.txt.lock**. Он хранит список пакетов последней версии, которые нашел `crosspm`. Условия для поиска задаются в [файле конфигурации crosspm.yaml\config.yaml](../config/CONFIG)
3. Скачиваем пакеты `crosspm download` - пакеты из **lock**-файла выкачиются рекурсивно (если есть **lock**-файл в скаченном архиве, он скачает все пакеты у пакета)
4. Используем скачанные пакеты: используем сразу в [Cmake](../usage/USAGE-CMAKE), импортируем переменные из [sh, cmd, json, или stdout](../config/OUTPUT), настраиваем [свой формат файлов](../config/output-template.md)

`crosspm download` может включает в себя `lock` команду, т.е. если вы используете файл с масками, то он ищет последние при загрузке.

### crosspm lock
Команда `crosspm lock` фиксирует текущие версии удовлетворяющие маскам, указанным в файле `dependencies.txt`. Фиксирует версии в выходной файл, обычно, `dependencies.txt.lock`.
Разработчик запускает команду, сохраняет новый файл `dependencies.txt.lock` в гит-репозитория для повторяемости сборки.

Имея, например, следующий файл манифест **dependencies.txt**:
```bash
boost                *                    1.55-pm
poco                 *-                   1.46-pm
openssl              1.0.20-              1.0.1i-pm
log4cplus            1.1.6                1.1-pm
pyyaml               3.10.115             3.10-python-3.4
protobuf             0.>=1.*              default
gtest                0.0.6                default
gmock                0.0.5                default
```
Выполним команду **lock**:
```bash
crosspm lock dependencies.txt dependencies.txt.lock
```
Будет получен следующий файл **dependencies.txt.lock**:
```bash
boost                1.55.0                            1.55-pm
poco                 1.46.11075-develop-vc110-x86      1.46-pm
openssl              1.0.20-develop                    1.0.1i-pm
log4cplus            1.1.6                             1.1-pm
pyyaml               3.10.115                          3.10-python-3.4
protobuf             1.10.343                          default
gtest                0.0.6                             default
gmock                0.0.5                             default
```
