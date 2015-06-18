# helloworld
[![Build Status](https://travis-ci.org/tecstack/helloworld.svg?branch=master)](https://travis-ci.org/tecstack/helloworld) [![Coverage Status](https://coveralls.io/repos/tecstack/helloworld/badge.svg?branch=master)](https://coveralls.io/r/tecstack/helloworld?branch=master) [![Download Status](https://img.shields.io/badge/download-1024%2Fmonth-green.svg)](https://github.com/tecstack/helloworld/)


Hello World for Team mgmt

## Prerequests

* python 2.7
* git
* easy_install && pip
* pyenv && pyenv-virtualenv

[参考这里](http://promisejohn.github.io/2015/04/15/PythonDevEnvSetting/)

## Usage

```bash
$ git clone https://github.com/tecstack/helloworld.git
$ cd helloworld
$ pip install -r requirements.txt
$ python src/hello/app.py
```
出现如下提示表示运行正常：

```
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
 * Restarting with stat
```

* 打开浏览器，访问："http://localhost:8080"
* 访问："http://localhost:8080/_add_numbers?a=1&b=1"


## Dev

```bash
$ git clone https://github.com/tecstack/helloworld.git
$ cd helloworld
$ tox # 多环境自动化单元测试
$ nosetests -v -s --with-coverage --cover-package=hello # 代码单元测试覆盖率
```
