---
title: "构建一个最简单的Python包"
description: 
date: 2024-07-08T15:04:13+08:00
image: "images/covers/python-growing.webp"
math: 
license: 
hidden: false
comments: true
---
要创建一个最简单的 Python 包来演示包的作用，你只需创建一个包含必要文件和目录结构的项目。这个示例包不会有实际的功能，但它会展示如何构建和打包一个 Python 项目。

### 目录结构

```
my_simple_package/
├── my_simple_package/
│   ├── __init__.py
│   └── simple_module.py
├── README.md
├── setup.py
└── pyproject.toml
```

### 详细步骤

1. **创建包目录**

   首先创建一个名为 `my_simple_package` 的目录，这是你的项目根目录。
1. **创建包的子目录**

   在项目根目录下，再创建一个同名的子目录 `my_simple_package`，这是实际的包目录。
1. **创建 `__init__.py` 文件**

   在 `my_simple_package` 目录下创建一个空的 `__init__.py` 文件，这个文件告诉 Python 这个目录是一个包。

```python
# my_simple_package/__init__.py
```

1. **创建一个简单的模块**

   在 `my_simple_package` 目录下创建一个名为 `simple_module.py` 的文件，并在其中添加一些简单的代码。

```python
# my_simple_package/simple_module.py

def hello():
    return "Hello, World!"
```

1. **创建 README 文件**

   在项目根目录下创建一个 `README.md` 文件，为包提供一些基本的描述。

```markdown
# My Simple Package

This is a simple package to demonstrate how to create a Python package.
```

1. **创建 `setup.py` 文件**

   在项目根目录下创建一个 `setup.py` 文件，用于设置包的元数据和安装信息。

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="my_simple_package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],  # List your package dependencies here
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple package to demonstrate packaging in Python",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="http://example.com/my_simple_package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
```

1. **创建 `pyproject.toml` 文件**

   在项目根目录下创建一个 `pyproject.toml` 文件，指定构建系统的要求。

```toml
# pyproject.toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
```

### 构建和安装

1. **构建包**

   在项目根目录下运行以下命令，生成源代码分发包和二进制分发包：

```sh
python setup.py sdist bdist_wheel
```

这将会在 `dist` 目录下生成 `.tar.gz` 和 `.whl` 文件。

1. **安装包**

   你可以使用 `pip` 安装生成的包文件：

```sh
pip install dist/my_simple_package-0.1.0-py3-none-any.whl
```

> 那么安装了之后的包去了哪里呢？参考[pip安装的包去了哪里](../pip安装的包在哪里)

### 测试包

你可以在 Python 环境中测试你的包是否正常工作：

```python
import my_simple_package.simple_module as sm

print(sm.hello())
# Output: Hello, World!
```

### 总结

这个简单的 Python 包演示了包的基本结构和构建过程。通过这个示例，你可以了解如何创建、打包和分发一个 Python 包。尽管这个包没有实际的功能，但它展示了所有必要的步骤和文件。
