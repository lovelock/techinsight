---
title: "Pyproject简明介绍"
description: 
date: 2024-07-08T14:23:21+08:00
image: images/covers/python-pyproject.png
math: 
license: 
hidden: false
comments: true
tags: ["Python", "Pyproject"]
---
`pyproject.toml` 文件是 Python 项目的新标准配置文件，它遵循 PEP 517 和 PEP 518 的规范。这个文件的主要目的是定义项目构建系统的要求，从而使得项目的构建过程更加标准化和独立于具体的构建工具。

### `pyproject.toml` 的主要功能

1. **定义构建系统要求**：`pyproject.toml` 文件中可以指定项目所需的构建工具及其版本。例如：

   ```toml
   [build-system]
   requires = ["setuptools", "wheel"]
   build-backend = "setuptools.build_meta"
   ```

   这表示项目需要 `setuptools` 和 `wheel` 这两个工具来进行构建，并且使用 `setuptools.build_meta` 作为构建后端。
2. **项目元数据**：除了构建系统要求，`pyproject.toml` 还可以包含项目的其他元数据，例如项目名称、版本、作者等信息。这些信息通常在 `setup.py` 中通过 `setup()` 函数来定义。

   ```toml
   [project]
   name = "example"
   version = "0.1.0"
   description = "An example package"
   authors = [
       { name="John Doe", email="john.doe@example.com" }
   ]
   ```

3. **其他配置**：`pyproject.toml` 还可以包含其他工具的配置，例如 `pytest`、`black` 等，使得项目的配置更加集中和统一。

### 与 `setup.py` 的比较

- **标准化**：`pyproject.toml` 提供了一种标准化的方式来定义构建系统要求，使得项目的构建过程更加一致和可预测。
- **独立性**：`pyproject.toml` 使得项目的构建过程独立于具体的构建工具，用户不需要了解或修改 `setup.py` 文件，只需要安装指定的构建工具即可。
- **扩展性**：`pyproject.toml` 可以包含更多的配置信息，不仅限于构建系统要求，还可以包含项目的其他元数据和工具配置。

### 之前的构建工具定义方式

在 `pyproject.toml` 出现之前，项目的构建工具通常在 `setup.py` 文件中定义。例如：

```python
from setuptools import setup

setup(
    name='example',
    version='0.1.0',
    packages=['example'],
    install_requires=[
        'some_dependency',
    ],
    entry_points={
        'console_scripts': [
            'example-cli=example.main:main',
        ],
    },
)
```

这种方式的缺点是：

- **依赖隐式**：用户需要阅读 `setup.py` 文件才能了解项目所需的构建工具和依赖。
- **不标准化**：不同的项目可能使用不同的方式来定义构建工具，导致构建过程不一致。

### 总结

- **`pyproject.toml`**：提供了一种标准化的方式来定义构建系统要求，使得项目的构建过程更加一致和可预测。
- **功能增强**：`pyproject.toml` 不仅限于构建系统要求，还可以包含项目的其他元数据和工具配置。
- **之前的定义方式**：通常在 `setup.py` 文件中定义，依赖隐式且不标准化。

通过使用 `pyproject.toml`，Python 项目的构建过程变得更加标准化和独立于具体的构建工具，提高了项目的可维护性和可移植性。
