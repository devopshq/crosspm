# -*- coding: utf-8 -*-
#
# (c) Positive Technologies, 2018.

from crosspm import CrossPM

import os

MainConfig = """
cpm:
  description: Configuration for ExtLibs project (cred.yaml needed)
  dependencies: dependencies.txt
  dependencies-lock: dependencies.txt.lock
  prefer-local: True

cache:
  cmdline: cache
  env: CROSSPM_CACHE_ROOT
  default:
  storage:
    packed: '{package}/{branch}/{version}/{compiler}/{arch}/{osname}/{package}.{version}.tar.gz'
    unpacked: '{package}/{branch}/{version}/{compiler}/{arch}/{osname}'

columns: '*package, version, branch'

options:
  compiler:
    cmdline: cl
    env: CROSSPM_COMPILER
    default: vc110

  arch:
    cmdline: arch
    env: CROSSPM_ARCH
    default: x86

  osname:
    cmdline: os
    env: CROSSPM_OS
    default: win
    
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

  user1:
    cmdline: user1
    env: DOWNLOAD_CI_USER1
    default:
    secret: false

  password1:
    cmdline: password1
    env: DOWNLOAD_CI_PASSWORD1
    default: 
    secret: true

  user2:
    cmdline: user2
    env: DOWNLOAD_CI_USER2
    default:
    secret: false

  password2:
    cmdline: password2
    env: DOWNLOAD_CI_PASSWORD2
    default: 
    secret: true

  auth_libs1: 
    cmdline: auth_libs1
    env: DOWNLOAD_CI_AUTH
    default: true
    secret: true

defaults:
  branch: '*'

parsers:
  common:
    columns:
      version: "{int}.{int}.{int}[.{int}][-{str}]"
    sort:
      - version
      - '*'
    index: -1

  artifactory:
    path: "{server}/{repo}/{branch}/{compiler|any}/{arch|any}/{osname}/{package}.{version}[.zip|.tar.gz|.nupkg]"
    properties: ""
    
"""

auth = 'env_auth_user:env_auth_password'
user = 'env_test_user'
password = 'env_test_password'
os.environ['DOWNLOAD_CI_AUTH'] = auth
os.environ['DOWNLOAD_CI_USER'] = user
os.environ['DOWNLOAD_CI_PASSWORD'] = password


def test_auth_cmd():
    with open("dependencies.txt.lock", 'w') as depF:
        depF.write('boost * 1.64-pm-icu')

    Config = """   
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple
  auth: $auth_libs1

sources:
  - repo:
      - some-repo.snapshot 
    """

    testConfig = MainConfig + Config
    print(testConfig)
    with open("config.yaml", 'w') as conF:
        conF.write(testConfig)

    if os.path.isfile(os.path.join(os.getcwd(), 'config.yaml')):
        configFile = os.path.join(os.getcwd(), 'config.yaml')
    else:
        print('Noooooo')

    dep = 'dependencies.txt.lock'
    cmd_auth = 'auth_testuser:auth_testpassword'

    argv = 'download --config="{configFile}" --depslock-path="{dep}" -o auth_libs1={cmd_auth}'.format(**locals())
    cpm = CrossPM(argv, return_result='raw')
    cpm.run()

    assert cpm._config._sources[0].args['auth'] == ['auth_testuser', 'auth_testpassword']


def test_auth_env():
    with open("dependencies.txt.lock", 'w') as depF:
        depF.write('boost * 1.64-pm-icu')

    Config = """
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple
  auth: $auth_libs1

sources:
  - repo:
      - some-repo.snapshot 
    """

    testConfig = MainConfig + Config

    with open("config.yaml", 'w') as conF:
        conF.write(testConfig)

    if os.path.isfile(os.path.join(os.getcwd(), 'config.yaml')):
        configFile = os.path.join(os.getcwd(), 'config.yaml')
    else:
        print('Noooooo')

    dep = 'dependencies.txt.lock'

    argv = 'download --config="{configFile}" --depslock-path="{dep}"'.format(**locals())
    cpm = CrossPM(argv, return_result='raw')
    cpm.run()

    assert cpm._config._sources[0].args['auth'] == ['env_auth_user', 'env_auth_password']


def test_userPass_env():
    with open("dependencies.txt.lock", 'w') as depF:
        depF.write('boost * 1.64-pm-icu')

    Config = """
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple

sources:
  - repo:
      - another-repo.snapshot
    auth: $user:$password    
    """
    testConfig = MainConfig + Config

    with open("config.yaml", 'w') as conF:
        conF.write(testConfig)

    if os.path.isfile(os.path.join(os.getcwd(), 'config.yaml')):
        configFile = os.path.join(os.getcwd(), 'config.yaml')
    else:
        print('Noooooo')

    dep = 'dependencies.txt.lock'

    argv = 'download --config="{configFile}" --depslock-path="{dep}"'.format(**locals())
    cpm = CrossPM(argv, return_result='raw')
    cpm.run()

    print('12455')

    assert cpm._config._sources[0].args['auth'] == ['env_test_user', 'env_test_password']


def test_userPass_cmd():
    with open("dependencies.txt.lock", 'w') as depF:
        depF.write('boost * 1.64-pm-icu')

    Config = """
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple

sources:
  - repo:
      - another-repo.snapshot
    auth: $user:$password    
    """

    testConfig = MainConfig + Config

    with open("config.yaml", 'w') as conF:
        conF.write(testConfig)

    if os.path.isfile(os.path.join(os.getcwd(), 'config.yaml')):
        configFile = os.path.join(os.getcwd(), 'config.yaml')
    else:
        print('Noooooo')

    dep = 'dependencies.txt.lock'
    cmd_user = 'test_user'
    cmd_password = 'test_password'

    argv = 'download --config="{configFile}" --depslock-path="{dep}" -o user={cmd_user},' \
           'password={cmd_password}'.format(**locals())
    cpm = CrossPM(argv, return_result='raw')
    cpm.run()

    assert cpm._config._sources[0].args['auth'] == ['test_user', 'test_password']


def test_userPass_cmd_base():
    with open("dependencies.txt.lock", 'w') as depF:
        depF.write('boost * 1.64-pm-icu')

    Config = """
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple

sources:
  - repo:
      - another-repo.snapshot
    auth: 
        - $user
        - $password    
    """
    testConfig = MainConfig + Config

    with open("config.yaml", 'w') as conF:
        conF.write(testConfig)

    if os.path.isfile(os.path.join(os.getcwd(), 'config.yaml')):
        configFile = os.path.join(os.getcwd(), 'config.yaml')
    else:
        print('Noooooo')

    dep = 'dependencies.txt.lock'
    base_user = 'test_user_base'
    base_password = 'test_password_base'

    argv = 'download --config="{configFile}" --depslock-path="{dep}" -o user={base_user},' \
           'password={base_password}'.format(**locals())
    cpm = CrossPM(argv, return_result='raw')
    cpm.run()

    assert cpm._config._sources[0].args['auth'] == ['test_user_base', 'test_password_base']


def test_userPass_cmd_direct():
    with open("dependencies.txt.lock", 'w') as depF:
        depF.write('boost * 1.64-pm-icu')

    Config = """
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple

sources:
  - repo:
      - another-repo.snapshot
    auth: 
        - direct_user
        - direct_password    
    """
    testConfig = MainConfig + Config

    with open("config.yaml", 'w') as conF:
        conF.write(testConfig)

    if os.path.isfile(os.path.join(os.getcwd(), 'config.yaml')):
        configFile = os.path.join(os.getcwd(), 'config.yaml')
    else:
        print('Noooooo')

    dep = 'dependencies.txt.lock'

    argv = 'download --config="{configFile}" --depslock-path="{dep}"'.format(**locals())
    cpm = CrossPM(argv, return_result='raw')
    cpm.run()

    assert cpm._config._sources[0].args['auth'] == ['direct_user', 'direct_password']


def test_two_Repo_direct():
        with open("dependencies.txt.lock", 'w') as depF:
            depF.write('boost * 1.64-pm-icu')

        Config = """
common:
  server: https://repo.example.com/artifactory
  parser: artifactory
  type: jfrog-artifactory-aql
  auth_type: simple

sources:
  - repo:
      - first-repo.snapshot
    auth: 
        - direct_user1
        - direct_password1         
  - repo:
      - second-repo.snapshot
    auth: 
        - direct_user2
        - direct_password2    
        """

        testConfig = MainConfig + Config
        with open("config.yaml", 'w') as conF:
            conF.write(testConfig)

        if os.path.isfile(os.path.join(os.getcwd(), 'config.yaml')):
            configFile = os.path.join(os.getcwd(), 'config.yaml')
        else:
            print('Noooooo')

        dep = 'dependencies.txt.lock'

        argv = 'download --config="{configFile}" --depslock-path="{dep}"'.format(**locals())
        cpm = CrossPM(argv, return_result='raw')
        cpm.run()

        assert cpm._config._sources[0].args['auth'] == ['direct_user1', 'direct_password1']
        assert cpm._config._sources[1].args['auth'] == ['direct_user2', 'direct_password2']


def test_two_Repo_env():
    with open("dependencies.txt.lock", 'w') as depF:
        depF.write('boost * 1.64-pm-icu')

    Config = """
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
        - $user2
        - $password2    

        """
    testConfig = MainConfig + Config
    with open("config.yaml", 'w') as conF:
        conF.write(testConfig)
    os.environ['DOWNLOAD_CI_USER1'] = 'env_user1'
    os.environ['DOWNLOAD_CI_PASSWORD1'] = 'env_password1'
    os.environ['DOWNLOAD_CI_USER2'] = 'env_user2'
    os.environ['DOWNLOAD_CI_PASSWORD2'] = 'env_password2'
    if os.path.isfile(os.path.join(os.getcwd(), 'config.yaml')):
        configFile = os.path.join(os.getcwd(), 'config.yaml')
    else:
        print('Noooooo')

    dep = 'dependencies.txt.lock'

    argv = 'download --config="{configFile}" --depslock-path="{dep}"'.format(**locals())
    cpm = CrossPM(argv, return_result='raw')
    cpm.run()

    assert cpm._config._sources[0].args['auth'] == ['env_user1', 'env_password1']
    assert cpm._config._sources[1].args['auth'] == ['env_user2', 'env_password2']


def test_two_Repo_cmd():
    with open("dependencies.txt.lock", 'w') as depF:
        depF.write('boost * 1.64-pm-icu')

    Config = """
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
        - $user2
        - $password2    

        """
    testConfig = MainConfig + Config
    with open("config.yaml", 'w') as conF:
        conF.write(testConfig)
    user1 = 'cmd_user1'
    password1 = 'cmd_password1'
    user2 = 'cmd_user2'
    password2 = 'cmd_password2'
    if os.path.isfile(os.path.join(os.getcwd(), 'config.yaml')):
        configFile = os.path.join(os.getcwd(), 'config.yaml')
    else:
        print('Noooooo')

    dep = 'dependencies.txt.lock'

    argv = 'download --config="{configFile}" --depslock-path="{dep}" -o user1={user1},password1={password1},' \
           'user2={user2},password2={password2}'.format(**locals())
    cpm = CrossPM(argv, return_result='raw')
    cpm.run()

    assert cpm._config._sources[0].args['auth'] == [user1, password1]
    assert cpm._config._sources[1].args['auth'] == [user2, password2]
