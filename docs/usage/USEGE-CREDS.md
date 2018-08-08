##Варианты использования учётных данных для подключения к artifactory

Для использования необходимо указать в конфигурационном файле следующие параметры.
В разделе options:
```yaml
options:
<... пропущен ненужный блок ...>
  user:
    cmdline: user
    env: DOWNLOAD_CI_USER
    default:
    secret: false
  
  password:
    cmdline: password
    env: DOWNLOAD_CI_PASSWORD
    default: 
    secret: true
  
  auth: 
    cmdline: auth_libs1
    env: DOWNLOAD_CI_AUTH
    default: true
    secret: true
```
 - `user`, `password`, `auth` - произвольные названия для переменных для авторизации.
 - `cmdline` - название аргумента при задании переменной с помощью коммандной строки.
 - `env` - название системной переменной для использования.
 - `default` - значение по умолчанию. Если не хотите задавать - оставьте поле пустым. 
 - `secret` - отображать или нет введёное значение при поиске пакета. Обычно это выводится следующим образом:
 ```
boost: {'version': ['*', '*', '*', None, None], 'branch': '1.64-pm-icu', 'user': 'env_test_user', 
'compiler': 'vc110', 'arch': 'x86', 'osname': 'win', 'user1': None, 'user2': None, 
'server': 'https://repo.example.com/artifactory'}
```
 Как видно в данном примере - параметр user виден, а остальные скрыты. 
 
 После задания переменных для авторизации - переменные можно использовать в разделах `common` или `sourses`.
 Переменные задаются по имени с добавлением в начале знака $.
 Варианты задания:
 ```yaml
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple
  auth: $auth
  
sources:
  - repo:
      - some-repo.snapshot 
```

```yaml
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple
  
sources:
  - repo:
      - another-repo.snapshot
    auth: $user:$password
``` 
 
```yaml
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple
  
sources:
  - repo:
      - first-repo.snapshot
    auth: 
        - $user1
        - $password1         
  - repo:
      - second-repo.snapshot
    auth: 
        - $user2:$password2
  - repo:
      - third-repo.snapshot
    auth: 
        - $auth
```
Как видно в примерах - переменные можно задававать в виде сочетания `user:password`. 
Это касается и сочетаний в конфигурации и самих значений значений.

##Примеры использования.

 - Можно задать системные переменные, указанные в конфигурационном файле
 - Можно задать в командной строке:
 
`crosspm download -o user=user,password=password<...>`

`crosspm download -o auth=user:password<...>`

 