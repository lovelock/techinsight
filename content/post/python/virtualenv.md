---
title: "Virtualenv快速设置"
date: 2024-04-10T00:28:44+08:00
image: /images/covers/python-virtualenv.png
hidden: false
comments: true
tags: ["Python", "virtualenv"]
---
记录一下快速配置virtualenv。

## 1. 安装virtualenv

### macOS

```bash
brew install virtualenv
```

### Linux(以Debian为例)

```bash
sudo apt install virtualenv
```

## 2. 指定版本

```bash
virtualenv venv --python=3.11
```

这时会自动在 `venv`下复制一份全新的3.11的python环境

> 注意：这种写法只能使用系统已经安装的Python版本，否则需要指定Python的安装路径

## 3. 让指定的版本生效

```bash
source venv/bin/activate
```

这时命令行提示符前会有一个 `(venv)`的前缀，如下，这时在这里执行 `pip install`就不会影响到别的环境。

```
(venv) frost@debian:~/workspace/
```

## 4. 不再使用这个Python环境

```bash
deactivate
```
