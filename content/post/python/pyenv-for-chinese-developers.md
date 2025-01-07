---
title: "Pyenv: 中国开发者必读"
description: 
date: 2024-08-21T18:59:46+08:00
image: 
math: 
license: 
hidden: false
comments: true
categories: ["python"]
tags: ["pyenv", "virtualenv"]
---

后记：把pyenv的代码下载下来才发现，这些版本居然都是硬编码，连所有的下载链接也都是写死的，所以如果Python更新了新版本，我还得先更新pyenv才能下载新版本的Python，这真是太离谱啦！

Python开发者需要解决的问题可真多啊，周边的配套设施也是真多，但不管怎么多，还是免不了受到高强的阻碍。

事情是这样的，开发服务器用的Rocky Linux8，默认的Python环境是3.6.8，太旧的了，想着安装个新版本，但用dnf安装的肯定还是很老，想着用社区的方案装一个最新的吧，又想到可能会遇到多版本的问题，找了下发现了pyenv，了解了下这个东西很像sdkman（用来管理Java相关的工具链的），可以安装不同的Python版本。按照官方文档开搞吧。

```bash
curl https://pyenv.run | bash
```

这样就可以执行`pyenv`，然后把下面这段代码放在`$HOME/.bashrc`里，就可以使用了。

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

让后如果你想安装一个Python3.12，就可以`pyenv install 3.12`，它会自动找符合这个要求的最新的版本，也就是3.12.5去下载。如果事情到这里就结束了，我想我是不会写这篇文章的。

执行之后看到了这个提示

```plaintext
--2024-08-21 07:44:27--  https://www.python.org/ftp/python/3.12.5/Python-3.12.5.tar.xz
Resolving www.python.org (www.python.org)...
```

然后就是你知道的，它永远无法执行成功了。pyenv不懂中国人啊，连k8s都知道可以设置中国区，把相关的镜像仓库都指向了阿里云。废话不多说，先看看手动怎么解决。

注意：这里不是要解决pip下载PyPI包的问题，而是要下载Python解释器。国内比较稳定的也就是阿里的了。

```plaintext
https://registry.npmmirror.com/binary.html?path=python/3.12.5/
```

还要注意，最终的下载地址并不是这样的。而是这样的

```plaintext
https://registry.npmmirror.com/-/binary/python/3.12.5/Python-3.12.5.tar.xz
```

分析之前的输出，发现它把这个包下载到了`$HOME/.pyenv/cache`目录下，那么有没有可能我们自己把它下载到这里，它就不会再去下载了呢？尝试了一下果然是可以的。那么接下来就要把这个过程自动化了。写一个简单的python脚本就可以了。别奇怪这里为什么用Python脚本，每个系统都装了Python，这里没有使用任何标准库之外的东西，所以没什么关系。


这是使用wget的版本：

```python
import os
import sys
import subprocess
from pathlib import Path

def download_file(url, filename):
    try:
        subprocess.run(["wget", "-O", str(filename), url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")
        sys.exit(1)

def main():
    # 获取用户输入的Python版本
    version = input("请输入要安装的Python版本 (例如 3.12.5): ")

    # 构建下载URL
    base_url = "https://registry.npmmirror.com/-/binary/python"
    url = f"{base_url}/{version}/Python-{version}.tar.xz"

    # 设置下载目录
    cache_dir = Path.home() / ".pyenv" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    filename = cache_dir / f"Python-{version}.tar.xz"

    print(f"正在下载 Python {version}...")
    download_file(url, filename)
    print(f"下载完成。文件保存在: {filename}")

    print(f"开始使用 pyenv 安装 Python {version}...")
    try:
        subprocess.run(["pyenv", "install", version], check=True)
        print(f"Python {version} 安装成功！")
    except subprocess.CalledProcessError as e:
        print(f"安装失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

如果你的系统没有安装wget，还可以使用curl的版本

```python
import os
import sys
import subprocess
from pathlib import Path

def download_file(url, filename):
    try:
        subprocess.run(["curl", "-L", "-o", str(filename), url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")
        sys.exit(1)

def main():
    # 获取用户输入的Python版本
    version = input("请输入要安装的Python版本 (例如 3.12.5): ")

    # 构建下载URL
    base_url = "https://registry.npmmirror.com/-/binary/python"
    url = f"{base_url}/{version}/Python-{version}.tar.xz"

    # 设置下载目录
    cache_dir = Path.home() / ".pyenv" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    filename = cache_dir / f"Python-{version}.tar.xz"

    print(f"正在下载 Python {version}...")
    download_file(url, filename)
    print(f"下载完成。文件保存在: {filename}")

    print(f"开始使用 pyenv 安装 Python {version}...")
    try:
        subprocess.run(["pyenv", "install", version], check=True)
        print(f"Python {version} 安装成功！")
    except subprocess.CalledProcessError as e:
        print(f"安装失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

其实最应该做的是让pyenv也支持自定义可用的镜像，毕竟它的识别最新小版本号的功能是可用的，现在这样需要输入很精确的版本号才能用。
