<!--ts-->
      * [Варианты использования учётных данных для подключения к artifactory](#варианты-использования-учётных-данных-для-подключения-к-artifactory)
      * [Примеры использования.](#примеры-использования)
<!--te-->
## Варианты использования учётных данных для подключения к artifactory

Для использования необходимо указать в конфигурационном файле следующие параметры.
В разделе `options` укажите блок `auth` и/или блоки `user`, `password` как показано ниже:
```yaml
options:
<... пропущен ненужный блок ...>
  # можно указать все блоки, а использовать или auth или user, password
  auth:
    cmdline: auth_libs1
    env: DOWNLOAD_CI_AUTH
    secret: true

  user:
    cmdline: user
    env: DOWNLOAD_CI_USER
    secret: false

  password:
    cmdline: password
    env: DOWNLOAD_CI_PASSWORD
    secret: true
```

 - `user`, `password`, `auth` - произвольные названия переменных для авторизации.
 - `cmdline` - название аргумента при задании переменной с помощью коммандной строки.
 - `env` - название системной переменной для использования. Если переменная, указанная в cmdline не задана при запуске,
 но задана системная переменная, то будет использована значение системной переменной.
 - `secret` - отображать или нет в лог значение переменной. Если поставить значение `true`,
 то параметр не будет выводиться в лог. Для примера выше значения `auth` и `password` не будут видны в логе, а значение `user` будет:
  ```
boost: {'version': ['*', '*', '*', None, None], 'branch': '1.64-pm-icu', 'user': 'env_test_user',
'compiler': 'vc110', 'arch': 'x86', 'osname': 'win', 'user1': None, 'user2': None,
'server': 'https://repo.example.com/artifactory'}
```

 После того как переменные для авторизации указаны в разделе `options` можно использовать их в разделах `common` или `sourses`.
 Переменные задаются по имени в скобках `'{имяпеременной}'`.
 Варианты того как можно задать переменные:
 ```yaml
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple
  auth: '{auth}'

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
    auth: '{user}:{password}'
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
        - '{user1}'
        - '{password1}'
  - repo:
      - second-repo.snapshot
    auth:
        - '{user2}:{password2}'
    auth:
        - 'user:{password}'
  - repo:
      - third-repo.snapshot
    auth:
        - '{auth}'
```

## Примеры использования.

 - Можно задать системные переменные, указанные в конфигурационном файле. Например:

 `export DOWNLOAD_CI_AUTH='user:password'`

 `export DOWNLOAD_CI_USER='user'`
 `export DOWNLOAD_CI_PASSWORD='password'`

 - Можно задать в командной строке. Например:

`crosspm download -o user=user,password=password`
или
`crosspm download -o auth_libs1=user:password`
