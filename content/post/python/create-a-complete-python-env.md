---
title: "创建一个完整的可移植的Python运行环境"
description: 
date: 2024-07-09T11:31:01+08:00
image: "images/covers/python-growing.webp"
math: 
license: 
hidden: false
comments: true
---
有几种方法可以将 Python 解释器和您的应用程序一起打包，以创建一个完全独立的可执行文件。以下是几种常见的方法：

### 1. **PyInstaller**

PyInstaller 是一个流行的工具，可以将 Python 应用程序及其所有依赖项打包成一个独立的可执行文件，适用于 Windows、Mac 和 Linux。

#### 安装 PyInstaller

```sh
pip install pyinstaller
```

#### 使用 PyInstaller

```sh
pyinstaller --onefile your_script.py
```

`--onefile` 选项将所有内容打包成一个单独的可执行文件。

如果没有特别的要求，目前来看PyInstaller还是第一位的选择。

如果要将一些二进制文件比如ffmpeg也打包进来，可以使用 `--add-binary`来进行添加，具体参数是这样 `--add-binary='/path/to/ffmpeg:.`，其中 `/path/to/ffmpeg`是二进制文件的实际路径，而后面的 `.`表示要打包到当前路径下，如果就多个就跟多个 `--add-binary`。

完整的命令是这样的

```bash
pyinstaller --onefile --add-binary='/opt/homebrew/Cellar/ffmpeg/7.0.1/bin/ffmpeg:.' --add-binary='/opt/homebrew/Cellar/ffmpeg/7.0.1/bin/ffprobe:.' hello.py
```

执行完之后会在当前路径下生成一个 `hello.spec`，就是把上面指定的这些东西保存到配置文件了，后面如果你再需要添加就直接往配置文件里添加即可。然后直接执行 `pyinstaller hello.spec`，就可以使用里面的所有配置了。

### 2. **Nuitka**

Nuitka 是一个 Python 到 C++ 的编译器，可以将 Python 代码编译成高度优化的可执行文件。

#### 安装 Nuitka

```sh
pip install nuitka
```

#### 使用 Nuitka

```sh
nuitka --standalone --onefile your_script.py
```

`--standalone` 选项生成一个独立的可执行文件，`--onefile` 选项将其打包成一个文件。

### 3. **PyOxidizer**

PyOxidizer 是一个工具，可以将 Python 应用程序及其所有依赖项打包成一个独立的可执行文件，支持 Windows、Mac 和 Linux。

#### 安装 PyOxidizer

```sh
cargo install pyoxidizer
```

#### 使用 PyOxidizer

```sh
pyoxidizer build --release
```

这将生成一个独立的可执行文件。

> 实际上pyoxidizer需要一个还挺复杂的配置文件，详情还得查看对应的官方文档。不过我发现pyinstaller和nuitka已经可以满足需求了，就没有继续研究这个了。

### 4. **shiv 与 Docker**

虽然 `shiv` 本身不包含 Python 解释器，但您可以结合 Docker 来创建一个包含所有依赖项的容器镜像。

#### 创建 Dockerfile

```Dockerfile
FROM python:3.8-slim

COPY . /app
WORKDIR /app

RUN pip install shiv
RUN shiv -o my_app.pyz -c my_app .

CMD ["python", "my_app.pyz"]
```

#### 构建 Docker 镜像

```sh
docker build -t my_app_image .
```

#### 运行 Docker 容器

```sh
docker run -it my_app_image
```

这种方法将 Python 解释器和应用程序及其依赖项打包在一个 Docker 容器中。

### 总结

以上方法都可以将 Python 解释器和应用程序一起打包，创建一个完全独立的可执行文件。选择哪种方法取决于您的具体需求和目标平台。

但是测试发现PyInstaller和Nuitka打包成的可执行文件，在启动时都有一个明显的延迟，这里是[解释](../可执行文件启动慢的原因分析)
