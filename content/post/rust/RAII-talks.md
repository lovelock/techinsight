---
title: "从C++和Rust聊聊RAII"
description:
date: 2025-01-23T09:21:25+08:00
image:
math: true
license:
hidden: false
comments: true
categories: ["Rust"]
tags: ["Rust", "RAII", "C++"]
---

在一些介绍Rust的文章中经常会说Rust具有RAII的机制，所谓的Resource Acquisition Is Initialization，也即"资源获取即初始化"，那到底什么是RAII呢？我们从**资源管理**最初的问题开始说起。

## 没有RAII时C++是如何管理资源的

```cpp
#include <iostream>
#include <fstream>
#include <string>

int main() {
    // 创建一个文件流对象
    std::ifstream inputFile;

    // 打开文件
    inputFile.open("example.txt");

    // 检查文件是否成功打开
    if (!inputFile) {
        std::cerr << "无法打开文件!" << std::endl;
        return 1; // 返回错误代码
    }

    // 处理文件内容

    // 关闭文件
    inputFile.close(); // 关闭文件流

    return 0; // 正常结束程序
}
```

可以看到，打开资源之后还要手动进行关闭，否则就会产生资源泄漏，这是为什么呢？

### 什么是资源？

资源可以理解为程序在运行时锁使用的任何外部或内部的实体，包括但不限于：

1. 内存：动态分配的内存块（例如通过new或者malloc分配的内存）
2. 文件句柄：打开的文件，涉及读写操作
3. 网络连接：与外部服务或设备的连接
4. 数据库连接：与数据库的链接，执行查询和事务
5. 锁：在并发编程中，用于保护共享资源的机制

资源通过是有限的，程序需要合理地管理这些资源，以避免资源泄漏或者触发系统限制。

### 实现RAII最简单的形式

我们知道很多面向对象的语言都有**构造函数**和**析构函数**，这不就是天然的创建和释放**资源**的方法吗？如果把资源的创建放在构造函数里，在析构函数里释放它，就可以通过这个**包装对象**来自动管理资源了。

### 自定义一个对象来包装资源

```cpp
class Resource {
public:
    Resource() {
        inputFile.open("example.txt");
    }
    ~Resource() {
        inputFile.close();
    }

private:
    std::ifstream inputFile;
}
```

这就是RAII最基本的形式了。

### 使用C++内置的智能指针来包装资源

但如果这样是不是就太麻烦了，要给每个对象定义一个包装类，再去写它的构造函数和析构函数，有没有更简单的用法呢？

```cpp
#include <iostream>
#include <fstream>
#include <memory>

int main() {
    // 使用智能指针管理文件流
    std::unique_ptr<std::ifstream> inputFile = std::make_unique<std::ifstream>("example.txt");

    // 检查文件是否成功打开
    if (!(*inputFile)) {
        std::cerr << "无法打开文件!" << std::endl;
        return 1; // 返回错误代码
    }

    // 处理文件内容

    // inputFile 会在超出作用域时自动关闭
    return 0; // 正常结束程序
}
```

这样就不用再去手动`close`了。

## 为什么资源需要手动回收?

但为什么？

为什么资源需要手动回收呢？

首先要明确的是，这里说的资源通常是和外部系统有交互的，所以对资源的使用很多都是有限制的，比如系统会限制一个文件被多个进程同时打开，如果不**及时释放**，可能会导致其他进程无法使用这个资源。

到这里又要分两块说：无GC的语言和有GC的语言。

对于无GC的语言，也就只能手动回收了，那有GC的语言比如PHP、Java为什么也需要呢？这是因为垃圾回收也不是时刻在进行的，手动回收是为了**及时释放**，避免对有限资源的长期占用。

### 普通的资源回收(自己指定在何时close)

上面讲的都是要手动释放资源，即通过一个指令告知程序何时要释放资源，但大多数时候都是在方法结束时释放，而且有时打开资源的过程可能会有异常，这时最下面的资源回收的语句还没来得及执行就已经退出了，资源就泄漏了。

### 改进后的资源回收(Golang的 defer Close)

为了解决上面提到的异常退出时资源无法成功回收的问题，Java做了一个`try-with-resource`，可以自动关闭`Closable`类型的资源。而Golang的方案要更灵活，只需要在打开资源之后立即写一条`defer`就可以了，当资源使用完毕后就会自动触发defer中的语句，而且和打开过程中是否出现异常无关。相比Java，这个通用型强了很多，而且defer的语句也不限于资源，其他的也都可以，比如退出前记录一条日志之类。

但即便这样，还是要手动管理，这顶多算个半自动挡。

## RAII的资源回收

回到最初的问题，**吹**Rust的人总说它有RAII，然后C++这边就说“不就是RAII吗？搞得好像谁没有似的”，到这里就要体现出区别了。

从上面的例子来看，C++还需要**显式**使用智能指针来利用RAII自动回收资源，但Rust的RAII机制是根植在语法中的。Rust的所有权系统是实现RAII的基础，**每个对象都有一个所有者，并且只能被一个所有者管理**，当超出所有者的作用域时，Rust就会自动调用该对象的析构函数，释放资源。而析构函数是通过实现`Drop`trait来定义的，当一个对象超出其作用域时，Rust会自动调用它的`drop`方法，从而释放关联的资源。对于文件、网络连接等资源，Rust会在对象析构时自动关闭它们。

```rust
struct MyFile {
    file: File,
}

impl Drop for MyFile {
    fn drop(&mut self) {
        // 在此处释放资源，例如关闭文件
    }
}
```

### 最简单的例子

看一个最简单的例子，打开文件，读取文件，剩下的事交给Rust就好了。

```rust
use std::fs::File;
use std::io::{self, Read};

fn main() -> io::Result<()> {
    let mut file = File::open("file.txt")?; // 打开文件
    let mut contents = String::new();
    file.read_to_string(&mut contents)?; // 读取文件内容

    println!("{}", contents); // 打印文件内容

    // 当 `file` 超出作用域时，文件会自动关闭
    Ok(())
} // `file` 变量在这里超出作用域，资源会被自动释放
```

### 稍稍复杂一点的例子

上面这个和Golang的`defer`相比看不出明显的优势，但如果再加一个额外的**使用**这个`file`的方法呢？

```rust
use std::fs::File;
use std::io::{self, Read};

fn process_file(file: File) {
    // 在这里处理文件
}

fn main() -> io::Result<()> {
    let mut file = File::open("file.txt")?; // 打开文件
    let mut contents = String::new();
    file.read_to_string(&mut contents)?; // 读取文件内容

    println!("{}", contents); // 打印文件内容

    process_file(file);
    // 当 `file` 超出作用域时，文件会自动关闭
    Ok(())
} // `file` 变量在这里超出作用域，资源会被自动释放
```

把`file`句柄传递到别的方法里去了，还怎么在`main`里`defer`呢？这就是Golang的半自动化处理留下的问题，而Rust由于存在所有权系统，当把`file`作为参数传递给`process_file`方法之后，它的所有权就发生了转移，就只能在`process_file`方法里去释放它了。

## 总结

本文通过一个典型的例子解释了什么是RAII，以及在不同语言中实现RAII的区别，总的来说Rust的RAII机制更加**原生**，当然这也是有代价的，比如上面的例子，`file`的所有权转移给`process_file`之后，`main`方法的下半部分就无法使用`file`变量了，这又涉及`Clone`、`Copy`等一堆概念了。所以给我的感觉是为了避免所有权系统带来的麻烦，用Rust可能会写出更加长的方法——既然所有权会被方法调用转移，那么就不调用其他方法了。
