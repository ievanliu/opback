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

TBD

## Dev

```bash
$ git clone https://github.com/tecstack/helloworld.git
$ cd helloworld
$ tox # 多环境自动化单元测试
$ nosetests --with-coverage --cover-package=hello # 代码单元测试覆盖率
```