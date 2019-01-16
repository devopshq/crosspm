Import
=======
<!--ts-->
   * [Import](#import)
            * [Вынесение паролей из файла конфигурации](#вынесение-паролей-из-файла-конфигурации)
            * [Использование почти похожих файлов-конфигураций](#использование-почти-похожих-файлов-конфигураций)

<!-- Added by: aburov, at: 2019-01-16T17:11+07:00 -->

<!--te-->

Файл конфигурации  возможно разделить на несколько и импортировать недостающие части. Приведём примеры, когда это необходимо.

Механизм **import** является внутренней реализацией CrossPM, но в остальном поддерживается обычный yaml-формат. [Подробнее про yaml и anchor, которые используются на этой странице](https://learnxinyminutes.com/docs/yaml/)

#### Вынесение паролей из файла конфигурации
Чтобы не сохранять чувствительную информацию (логин\пароль от хранилища артефактов) в VCS, но иметь возможность использовать CrossPM во время сборки на сервере Continious Integration, нужно сделать следующее:

Создать файл **cred.yaml** со следующим содержимым:
```yaml
.aliases:
  - &auth_name1
      - myusername1
      - myp@ssw0rd
  - &auth_name2
      - myusername2
      - myp@ssw0rd
```

Создать файл конфигурации **crosspm.yaml**, где импортировать указанный выше файл и использовать определенный **anchor**:
```yaml
# Пропущена часть конфигурации, которая нас не интересует
# --------------
sources:
  - repo: libs-cpp-snapshot
    parser: crosspackage
    auth: *auth_name1
  - repo: nuget-repo
    parser: nuger
    auth: *auth_name2
# --------------
# Пропущена часть конфигурации, которая нас не интересует
```

Теперь добавляем в **.gitignore** файл **cred.yaml** и коммитим **crosspm.yaml**.

Добавляем в сервер CI пред-сборочный шаг по созданию **cred.yaml** из секретных переменных (реализация зависит от используемого CI-сервера)

#### Использование почти похожих файлов-конфигураций
Бывают случаи, когда вам необходимо создать примерно два одинаковых файл-конфигурации, но с отличающимися полями. Для примера - возмём два разных используемых имени **dependencies-файла**

Создаём **crosspm.main.yaml**:
```yaml
# cpm:
#  dependencies: dependencies
#  dependencies-lock: dependencies
#  prefer-local: True
  
# --------------
# Тут определён файл весь конфигурации, кроме секции cpm
# Так же допустимо использовать yaml-anchor для чувствительной информации
```

Создаём **crosspm.dependencies.yaml**
```yaml
import:
  - cred.yaml
  - crosspm.main.yaml
  
cpm:
 dependencies: dependencies.txt
 dependencies-lock: dependencies.txt.lock
 prefer-local: True
```

Создаём **crosspm.no-dependencies.yaml**
```yaml
import:
  - cred.yaml
  - crosspm.main.yaml
  
cpm:
 dependencies: no-dependencies.txt
 dependencies-lock: no-dependencies.txt.lock
 prefer-local: True
```

Запускаем **crosspm** с указанием используемого файла конфигурации:
```bash
crosspm download ^
    --options cl="vc140",arch="x86_64",os="win" ^
    --config=".\crosspm.dependencies.yaml"
    
crosspm download ^
    --options cl="vc140",arch="x86_64",os="win" ^
    --config=".\crosspm.no-dependencies.yaml"
```
