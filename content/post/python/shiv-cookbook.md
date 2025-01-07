---
title: "Python shiv简明教程"
description: 
date: 2024-07-08T08:49:34+08:00
image: images/covers/python-shiv.png
math: 
license: 
hidden: false
comments: true
tags: ["Python","shiv"]
---
引用一下Flutter中的章节，说明需要用到shiv的地方。

我们知道，用Go语言写出来的程序是平台**有关**的二进制文件，随便复制到相同的平台下都可以运行，但Python很多时候不是，因为用PyPI（pip）安装的包并不会打到Python脚本里去，直接拿一个引用了很多其他包的脚本放在其他机器上是无法执行的，所以需要一个把整个运行环境都复制出来可随处移动的工具，而Shiv就是干这个用的。

## Python 项目管理方式介绍

这是理解shiv的工作原理的重点，希望能仔细理解。

### `setup.py`

这应该是最传统的方式了，把基础信息和包的信息都写在一个py脚本里，基本的样式如下

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name='example',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'example-cli=example.main:main',
        ],
    },
)
```

简单介绍一下这些字段的含义。

`name`就是项目名了，注意是项目名，而不是最终生成的可执行文件的名字，`version`是版本号，不再过多解释。

`packages=find_packages()` 值得解释一下。正常来说这里是要手写一些包的，但这里使用了一个方法来动态查找这些包。

那么问题来了，什么是包呢？

在其他语言里，通常一级目录就是一个包了，但Python里并不是，还需要一个通常为空的文件 `__init__.py`，可以查一下为什么要有这个文件。当存在这个文件的时候才认为这是一个包，比如说我们有一个包 `example`，就需要是这样的结构

```
-- example_project
	-- setup.py
	-- example
		-- __init__.py
		-- main.py

```

正常来说，这时候在 `packages`处应该填写的是 `['example']`，但由于这个规则的存在，可以使用 `find_packages`方法查找整个目录下所有存在 `__init__.py`的目录，把它们的名字放在 `packages`里。当然这个方法还有别的参数，这里就不再赘述。

下面就是程序的**可执行文件**了。顾名思义，`console_scripts`就是在终端能直接使用的脚本名，作为脚本语言，Python有两种写法

```python
print('hello world')
```

这时候直接 `python main.py`是可以的，但在标准化的项目里，通常是像下面这样的写法

```python
def main():
	print('hello world')

if __name__ == '__main__':
	main()
```

这里就定义了一个 `main`方法，其实就类似于C系列语言中的main函数了。

问题讨论到这里就已经很清晰了，我们有了包名 `example`，里面有一个 `hello`模块，其实就是 `hello.py`，现在又有了方法名 `main`，其实已经可以引用它了，没错就是 `example.hello:main`

搞清楚了这些问题，就可以看看Python包的安装和使用了。

```bash
pip install setuptools
python setup.py
pip install .
```

如果当前使用的Python环境是用virtualenv安装的，这时候就会在 `venv/bin/`下生成相应的可执行文件，对应上面的例子，就是 `example-cli`。执行 `venv/bin/example-cli`就能运行上面的代码了。

到这里终于把前置的问题都说清楚了，现在可以讨论shiv的问题了。

### 其他方式

#### `setup.cfg`

后面又发展除了 `setup.cfg`，用ini的语法来写一些静态的内容，没有解决什么核心的问题。

```ini
# setup.cfg
[metadata]
name = example
version = 0.1

[options]
packages = find:

[options.entry_points]
console_scripts =
    example-cli = example.main:main
```

#### `pyproject.toml`

pyproject.toml是一个新的标准，用于定义构建系统的要求。它使用TOML格式，并且旨在取代setup.py和setup.cfg。pyproject.toml文件可以包含构建工具的配置，如setuptools、wheel、flit等。

```toml
# pyproject.toml
[build-system]
requires = ["setuptools", "wheel"]

[project]
name = "example"
version = "0.1"

[project.scripts]
example-cli = "example:main"
```

这个看起来就有点Cargo.toml的味道了。

## shiv解决了什么问题？

简单来讲，就是把当前程序和它的所有依赖打成一个包，让它成为一个**相对独立**的发行版本。有点类似Java的fatjar。

注意这里说的是相对独立，因为Python的很多包其实是一个Wrapper，也就是对其他可执行文件/库的Python**封装**，而不是实现，所以如果你引用的包是一个Wrapper，那么用shiv也不能解决这个问题。

### 简单的例子

新建一个目录叫 `shiv_demo`，写一个脚本叫 `hello.py`，内容如下

```python
import simplejson as json

def main():
    r = json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
    print(r)

if __name__ == '__main__':
    main()
```

可以看到依赖 `simplejson`，安装它

```python
pip install simplejson shiv
```

配置一个 `setup.py`

```python
from setuptools import setup

setup(
    name="hello-world",
    version="0.0.1",
    description="Greet the world.",
    py_modules=["hello"],
    entry_points={
        "console_scripts": ["hello=hello:main"],
    },
)
```

这时候就可以给它打包了

```python
shiv -c hello -o hello.pyz .
```

这时候打包生成了一个 `hello.pyz`文件，就可以把这个文件拿到别处去执行了，然后你就会发现报错。。。

到这里验证的时候我才发现，其实shiv解决的问题非常有限，参考这里[shiv解决了什么问题](../shiv解决了什么问题)，但起码它可以让你的程序在安装了相同的Python执行器的机器之间移植。下面测试一下，在另外一个目录里再执行

```python
virtualenv venv --python=3.12
source venv/bin/activate
```

然后执行刚刚打包生成的 `hello.pyz`，结果还是报错

```
❯ ./hello
Traceback (most recent call last):
  File "/private/tmp/shiv3/./hello/_bootstrap/__init__.py", line 76, in import_string
  File "/Users/qingchun3/.shiv/hello_e90513a0cebd72cf33c783fbb6faeb3783e9e41fd501901ce8b27f69a16aef65/site-packages/hello.py", line 1, in <module>
    import simplejson as json
ModuleNotFoundError: No module named 'simplejson'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/private/tmp/shiv3/./hello/__main__.py", line 3, in <module>
  File "/private/tmp/shiv3/./hello/_bootstrap/__init__.py", line 253, in bootstrap
  File "/private/tmp/shiv3/./hello/_bootstrap/__init__.py", line 81, in import_string
  File "/private/tmp/shiv3/./hello/_bootstrap/__init__.py", line 59, in import_string
  File "/opt/homebrew/Cellar/python@3.12/3.12.4/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/Users/qingchun3/.shiv/hello_e90513a0cebd72cf33c783fbb6faeb3783e9e41fd501901ce8b27f69a16aef65/site-packages/hello.py", line 1, in <module>
    import simplejson as json
ModuleNotFoundError: No module named 'simplejson'
```

唉？不是说好的会把依赖也打包进来吗？为什么没有？原来是因为没有添加

```
-r requirements.txt
```

选项，那么这个文件从哪里来呢？如果你已经通过pip安装了所有依赖，通过执行 `pip freeze > requirements.txt`就可以了。

完整命令就是

```
shiv -c hello -o hello.pyz -r requirements.txt .
```

再测试就通过了。

## 总结

其实到最后我是很失望的，因为一开始并没有完全搞清楚shiv到底解决了什么问题，我想做的是完全的可移植性，在一台机器上将环境配置好之后拿到同平台的其他机器上直接可以执行的那种，但明显shiv并不符合我的要求，这时候我突然就发现了Java和Golang的厉害之处了，Java可以一个jar包走天下，只要有JRE就能运行，而Golang更厉害了，甚至什么都不需要，直接就是一个包含所有依赖的二进制文件。

但是，问题还是要解决，再问问GPT，继续踏上征程吧。
