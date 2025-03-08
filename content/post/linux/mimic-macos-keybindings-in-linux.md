---
title: "Linux下模拟macOS键位绑定"
description: 
date: 2025-03-08T10:38:14+08:00
image: 
math: true
license: 
hidden: false
comments: true
categories: ["Linux", "macOS"]
tags: ["Linux", "macOS", "键位绑定", "Toshy", "VS Code", "Vim", "剪贴板"]
---


## 引言

作为一个多年macOS用户，最近切换到Linux后，最不习惯的就是键位绑定。macOS的快捷键设计非常符合我的操作习惯，而Linux的默认键位让我感到非常不适应。为了解决这个问题，我开始了寻找键位绑定解决方案的旅程。经过一番折腾，最终找到了一个相对完美的解决方案——**Toshy**。在这篇博客中，我将记录下我的解决过程，希望能帮助到有同样需求的朋友。


## 寻找解决方案

在Linux下模拟macOS键位绑定，我首先想到的是通过修改系统键位映射来实现。经过一番搜索，我发现了以下几种常见的方案：

1. **xmodmap**：这是一个经典的X11工具，可以通过修改键位映射来实现自定义键位。不过，它的功能相对基础，无法实现复杂的键位绑定逻辑。
   
2. **Toshy**：这是一个专门为Linux设计的键位映射工具，旨在将macOS的键位绑定移植到Linux上。它支持Gnome、KDE等多种桌面环境，并且配置相对简单。最终，我决定尝试Toshy。


## 安装与配置Toshy

按照Toshy的官方文档，我首先通过以下命令安装了Toshy：

```bash
git clone https://github.com/RedBearAK/toshy.git
cd toshy
./setup_toshy.py install
```

安装完成后，我启动了Toshy服务，但发现键位绑定并没有生效。于是，我查看了服务日志，发现还需要安装一个名为`xremap`的Gnome扩展。安装完成后，Toshy终于可以正常工作了。


#### 3. 解决VS Code中的快捷键冲突

虽然Toshy在大多数情况下工作良好，但在VS Code中，我发现了一些问题。例如，`Ctrl+E`本来是希望光标跳转到行末，但在终端中却执行了“查找文件”的操作。经过排查，我发现在VS Code的键位绑定中，可以通过调整`when`条件来避免这种冲突。

具体来说，我在VS Code的`keybindings.json`文件中，将`Ctrl+E`的绑定条件改为`editorTextFocused`，这样它就不会在终端中生效了。类似的，其他快捷键也可以通过调整`when`条件来避免冲突。

```json
[
    {
        "key": "ctrl+e",
        "command": "workbench.action.quickOpen",
        "when": "editorTextFocus"
    },
    {
        "key": "ctrl+e",
        "command": "-workbench.action.quickOpen"
    },
    {
        "key": "ctrl+p",
        "command": "workbench.action.quickOpen",
        "when": "editorTextFocus"
    },
    {
        "key": "ctrl+p",
        "command": "-workbench.action.quickOpen"
    },
    {
        "key": "ctrl+f",
        "command": "-workbench.action.terminal.focusFind",
        "when": "terminalFindFocused && terminalHasBeenCreated || terminalFindFocused && terminalProcessSupported || terminalFocusInAny && terminalHasBeenCreated || terminalFocusInAny && terminalProcessSupported"
    }
]
```

加上以上配置，就基本上能在终端里保持在独立终端中的体验了。

如果还不行，可能还要在user Settings里加上这行

```json
    "terminal.integrated.allowChords": false,
```

这个就是避免在终端中触发全局快捷键，比如Ctrl-K作为前缀开始的一些组合操作。这些组合操作我是完全没有用过的，所以关了能解决一些问题。


#### 4. 解决Vim模式下的剪贴板问题

在VS Code中使用Vim模式时，我发现`Ctrl+C`和`Ctrl+V`无法正常工作，需要加上`Shift`才行，但我现在也没有仔细研究toshy的实现机制，所以也没办法改配置。为了解决这个问题，我希望在Vim模式下使用系统剪贴板进行复制粘贴。

具体做法是，在Vim扩展配置中，勾选使用系统剪贴板。

![](/static/images/vscode-vim-clipboard.png)


其他app如果想使用系统剪贴板可以自行搜索，一般都很简单。

#### 5. 总结

通过Toshy，我成功地在Linux下模拟了macOS的键位绑定，解决了大部分操作习惯上的不适。虽然在VS Code和Vim模式下遇到了一些问题，但通过调整键位绑定和Vim配置，最终也找到了解决方案。

如果你也是一个从macOS切换到Linux的用户，希望这篇博客能帮助你更快地适应新的操作环境。如果你有更好的解决方案或建议，欢迎在评论区分享！


#### 参考链接

- [Toshy GitHub仓库](https://github.com/RedBearAK/toshy)
- [VS Code键位绑定文档](https://code.visualstudio.com/docs/getstarted/keybindings)
- [Vim剪贴板配置](https://vim.fandom.com/wiki/Accessing_the_system_clipboard)