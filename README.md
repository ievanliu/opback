# opback
[![Build Status](https://travis-ci.org/tecstack/opback.svg?branch=develop)](https://travis-ci.org/tecstack/opback) [![Coverage Status](https://coveralls.io/repos/tecstack/opback/badge.svg?branch=develop)](https://coveralls.io/r/tecstack/opback?branch=develop) [![Download Status](https://img.shields.io/badge/download-1024%2Fmonth-green.svg)](https://github.com/tecstack/opback/)


Hello World for Team mgmt

## Prerequests

* python 2.7
* git
* easy_install && pip
* pyenv && pyenv-virtualenv

[参考这里](http://promisejohn.github.io/2015/04/15/PythonDevEnvSetting/)

## Usage

### 基本用法

```bash
$ git clone https://github.com/tecstack/opback.git
$ cd opback
$ pip install -r requirements.txt
$ python src/hello/app.py
```
出现如下提示表示运行正常：

```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
```

* 打开浏览器，访问："http://localhost:5000"
* 访问："http://localhost:5000/_add_numbers?a=1&b=1"


### Dev时用到的一些命令：

```bash
$ git clone https://github.com/tecstack/opback.git
$ cd opback
$ flake8 # 检查语法合规性，参照业内PEP8规范
$ tox # 多环境自动化单元测试
$ nosetests -v --with-coverage --cover-package=tecstack # 代码单元测试覆盖率
$ python scripts/manager.py runserver # 通过manager启动
$ python scripts/manager.py shell # 通过shell调测，自动import app, db, models
$ python scripts/manager.py initdb # 初始化数据库: .data/app.db
$ python scripts/manager.py dropdb # 删除数据库: .data/app.db
$ python scripts/manager.py db migrate # 修改models之后通过migrate检测模型变更
$ python scripts/manager.py db upgrade # 根据自动检测变化更新数据库
$ python scripts/manager.py db downgrade # 数据库版本降级
$ autopep8 src/tecstack/xxx.py # 自动根据PEP8规范输出修改正代码
$ autopep8 -i src/tecstack/xxx.py # 自动根据PEP8规范修正代码，不会调整单行长度等
```

## 开发中的规约：

* `pip freeze`生成目前python环境依赖的类库，推荐pyenv独立环境（flask）内导出依赖库。
* `gitchangelog`生成git提交记录，由发布者写入changelog发布。
* `flake8`检查当前所写python的语法合规性，于业内规范PEP8做校验对比，不能有错误提示。
* `nosetests -v --with-coverage --cover-package=tecstack`执行单元测试，\
    要求通过所有写的测试。
* `tox`自动创建独立的python运行环境，并在每个独立环境内执行语法、单元测试任务，用于自动集成。
* 所有代码 **本地** 提交之前建议通过flake8和nosetests检查错误，无误后可以提交到本地仓库。
* 所有代码 **远程** 提交之前必须通过tox测试，无误后可以push到远程develop分支。
* **Never** use manager.py to do database operation in **Production Environment**.
* 单元测试中数据库采用.data/test.db，每个测试用例都会重新创建数据库
