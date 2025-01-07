---
title: "使用Ninja作为CMake的后端"
date: 2024-04-04T22:00:30+08:00
image: /images/covers/CMake-with-Ninja-cover.png
hidden: false
tags: ["cmake", "ninja"]
categories: ["in-action"]
---

使用CMake的小伙伴可能大部分都是在（类）Unix环境下，所以一般都是用Unix Makefile作为默认后端，我这两天在修改一个多年前的C项目，把它从一坨Automake、Autoconf中拯救出来，改成了CMake的形式，清爽多了。

为什么这么说呢？是因为原先的方式就是把项目本身的代码放在根目录，然后几个依赖放在和自己的代码同一级的文件夹里，对于这几个依赖也是动态链接的方式，所以就需要先手动按顺序编译、安装这些依赖，然后再编译自己的代码。而改成CMake之后就变成静态依赖了，编译过程简化不少。

但问题也来了，我发现每次编译都要花挺长时间，那么有没有办法加速呢？这时候我想到了在很多开源项目都会用到的Ninja，于是了解了下，发现像Chromium、Android（部分）都是用它编译的，主打一个**增量编译**，说白了就是只编译修改了的部分，它能够更智能地决定哪些部分需要重新构建，从而减少不必要的编译。

## 使用方法

首先当然是安装了，在Debian上的名字叫`ninja-build`，其他系统可以参考这个名字。

正常使用CMake是这样的：

```bash
mkdir build
cd build
cmake ..
cmake --build
```

而对比使用Ninja作为状态后端，流程是这样的

```bash
mkdir build
cd build
cmake -G "Ninja"
cmake --build
```

区别就在于加了`-G "Ninja"`，一定注意这里要大写，否则你可以试试。

由于代码量比较少，所以比较下来区别不大，但公司的那个C项目，实际使用时还是有点明显的。

![CMake with Ninja build time](/images/CMake-with-Ninja-build-time.png)
![CMake with Unix Makefiles build time](/images/CMake-with-Unix-Makefiles-build-time.png)

查了一下Help，如下

```plaintext
Generators

The following generators are available on this platform (* marks default):
  Green Hills MULTI            = Generates Green Hills MULTI files
                                 (experimental, work-in-progress).
* Unix Makefiles               = Generates standard UNIX makefiles.
  Ninja                        = Generates build.ninja files.
  Ninja Multi-Config           = Generates build-<Config>.ninja files.
  Watcom WMake                 = Generates Watcom WMake makefiles.
  CodeBlocks - Ninja           = Generates CodeBlocks project files.
  CodeBlocks - Unix Makefiles  = Generates CodeBlocks project files.
  CodeLite - Ninja             = Generates CodeLite project files.
  CodeLite - Unix Makefiles    = Generates CodeLite project files.
  Eclipse CDT4 - Ninja         = Generates Eclipse CDT 4.0 project files.
  Eclipse CDT4 - Unix Makefiles= Generates Eclipse CDT 4.0 project files.
  Kate - Ninja                 = Generates Kate project files.
  Kate - Unix Makefiles        = Generates Kate project files.
  Sublime Text 2 - Ninja       = Generates Sublime Text 2 project files.
  Sublime Text 2 - Unix Makefiles
                               = Generates Sublime Text 2 project files.
```

所以`-G`其实就是指定generator，默认是`Unix Makefiles`。

## 再进一步

前面`mkdir build && cd build`这些步骤其实有点初级，可以改成这样的

```bash
cmake -G "Ninja" -B build
cmake --build build
```

第一行的意思是指定Ninja作为generator，指定build作为编译用的目录，如果build目录不存在就会自动创建。
第二行的意思是在build目录里执行编译过程。

这就更适合自己写一个编译脚本来执行了。

## 总结

Ninja的优势主要表现在以下几个方面：

1. 速度：Ninja被设计为比Make更快。Ninja的设计重点是实现高性能，这意味着它能够更快地开始编译过程并更高效地执行构建。
1. 简化的构建文件：Ninja的构建文件通常比Makefiles更加简单和易于理解。这是因为CMake负责生成这些文件，而Ninja仅仅执行它们。
1. 并行构建：虽然Make也支持并行构建（例如通过make -j 参数），但Ninja通常在并行构建方面更加高效和智能，它会自动推断出最优的任务数来使用所有可用的处理器核心。
1. 更好的构建进度估计：Ninja提供了更准确的构建进度信息，这对于长时间的构建过程来说非常有用。
1. 更少的重新构建：Ninja更智能地处理构建文件的生成，从而避免了一些不必要的重新构建，这可能发生在Makefiles中。
1. 快速的无操作构建：当没有任何东西需要构建时（即所有目标都是最新的），Ninja可以更快地确定没有工作要做，并立即完成构建过程。

总的来说，虽然Make和Ninja都支持增量构建，但Ninja在执行构建任务时通常会更快，尤其是对于大型项目。这不仅节省了开发者的时间，也提高了构建系统的整体效率。对于有大量源文件的复杂项目，采用Ninja可能会显著减少构建的时间。
