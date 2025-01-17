---
title: "Jupyter Matplotlib Chinese Font"
description:
date: 2025-01-17T14:44:07+08:00
image:
math: true
license:
hidden: false
comments: true
categories: ["python"]
tags: ["python", "jupyter", "matplotlib"]
---

Jupyter Note Book是个好东西，可以很方便地写一些脚本来执行，很多时候都需要画图，但是一个很头疼的问题是画图用的matplotlib用的默认字体中不包含中文，知道可以用

```python
plt.rcParams['font.family'] = 'STHeiti'  # 替换为你选择的字体
```

这个命令来让它显示中文了，可又不知道系统里有哪些是中文字体，而且最头疼的是你安装了一个中文字体，却不知道要怎么引用它，因为字体的文件名和注册到系统中的名字是不一定一样的，好在还有一个Python脚本可以做到这个。

```python
from matplotlib import pyplot as plt
import matplotlib
a=sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist])

for i in a:
    print(i)
```

这样就可以把matplotlib能用的所有字体都打印出来，选择带heiti或者songti的就可以用了，我选择的是STHeiti，确实解决了这个问题。

![](./images/matplotlib-chinese-font.png)

简化一下，可以下面这个脚本来只打印可能是中文的字体

```python
from matplotlib import pyplot as plt
import matplotlib

# 获取所有字体
fonts = sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist])

# 筛选并打印包含特定字符串的字体
keywords = ["Noto", "Songti", "Heiti"]
filtered_fonts = [font for font in fonts if any(keyword in font for keyword in keywords)]

for font in filtered_fonts:
    print(font)
```

我系统上可用的就有`Noto Sans Mono CJK SC`，这个非常好了，Linux上也能用，Debian上只需要`sudo apt install fonts-noto-cjk`即可。
