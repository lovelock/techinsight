---
title: "创建一个和你系统安装版本不同的Python解释器"
description: 
date: 2024-07-12T21:26:36+08:00
image: "images/covers/python-growing.webp"
math: 
license: 
hidden: false
comments: true
---

有时候在网上找一些Python项目来运行，需要用到的Python环境版本和本地已经安装好的不同，又不想真的重新安装一个，这时候就需要本文提到的方法了。

在macOS上创建一个临时的Python 3.8虚拟环境，即使系统上已经安装了更高版本的Python（如3.12），你可以使用`pyenv`配合`virtualenv`来完成这个任务。这里是如何做到的：

1. **安装 pyenv**：
   使用`Homebrew`来安装`pyenv`，可以让你在macOS上轻松地管理多个Python版本。

   打开终端并运行：

   ```bash
   brew update
   brew install pyenv
   ```

2. **安装 Python 3.8**：
   使用`pyenv`安装Python 3.8版本。

   ```bash
   pyenv install 3.8.12  # 选择一个3.8.x的版本
   ```

3. **设置 pyenv 版本**：
   设置你的终端会话使用刚才通过`pyenv`安装的Python版本。

   ```bash
   pyenv shell 3.8.12
   ```

4. **创建虚拟环境**：
   使用Python自带的模块`venv`来创建虚拟环境。

   ```bash
   python -m venv myenv
   ```

   或者，如果你喜欢`virtualenv`：

   首先安装`virtualenv`（如果还没有安装的话）：

   ```bash
   pip install virtualenv
   ```

   然后创建一个新的虚拟环境：

   ```bash
   virtualenv myenv
   ```

5. **激活虚拟环境**：

   ```bash
   source myenv/bin/activate
   ```

现在，你应该在名为`myenv`的虚拟环境中，并且使用的是Python 3.8版本。当你完成工作后，可以通过命令`deactivate`退出虚拟环境。

如果你想确保虚拟环境被创建为临时的，只需在完成工作后删除`myenv`虚拟环境所在的文件夹即可。
