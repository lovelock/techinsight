---
title: OkHttp同步和异步方式性能比较
description: 
date: 2024-04-22T22:33:43+08:00
image: 
math: 
license: 
hidden: false
comments: true
---
关于同步和异步，我理解是同步是串行执行，可以用多线程的方式来利用多核加快处理速度，而异步则是在遇到耗时操作时直接yield，待耗时操作完成时再提醒主线程执行回调的方式，所以异步能提高的是“吞吐量”而不是并发数。

本文就通过OkHttp的两种执行模式来详细说明。

## 环境准备

1. JDK 17
2. [JMH](https://openjdk.org/projects/code-tools/jmh/) 最著名的benchmark框架是JMH（Java Microbenchmark Harness）。JMH是专门用于代码微性能基准测试的工具，由Oracle的性能团队开发，它是专门为测试Java应用程序中的方法性能而设计的，适合做细粒度的性能测试。
3. 一个肯定不是性能瓶颈的HTTP服务（Rust编写）
4. [K6 压力测试工具](https://k6.io/)

## 实验过程

### 实现一个性能超级强的HTTP服务

#### 创建项目

```bash
cargo new fast-server
cd fast-server
```

#### 编辑`Cargo.toml`

```toml
[package]
name = "fast-server"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
axum = "0.7.5"
```

#### 编写Rust代码

使用最少的依赖，返回一个`Hello, World!`

```rust
use axum::{routing::get, Router};

#[tokio::main]
async fn main() {
    // build our application with a route
    let app = Router::new()
        // `GET /` goes to `root`
        .route("/", get(index));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8888").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

// basic handler that responds with a static string
async fn index() -> &'static str {
    "Hello, World!"
}
```

#### 启动服务

```bash
cargo run --release
```

#### 测试服务

```bash
$ http 127.0.0.1:8888
HTTP/1.1 200 OK
content-length: 13
content-type: text/plain; charset=utf-8
date: Mon, 22 Apr 2024 14:46:47 GMT

Hello, World!
```

至此，一个高性能服务就完成了。

什么，这就高性能了？那么我们来测试一下。

### 压力测试

#### 安装k6

```bash
brew install k6
```

#### 配置测试脚本

```bash
k6 new fast-server.js
```

这个命令会生成一份脚手架代码，具体内容如下（删除了大部分注释）

```javascript
import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  // A number specifying the number of VUs to run concurrently.
  vus: 10,
  // A string specifying the total duration of the test run.
  duration: '30s',
};

export default function() {
  http.get('https://test.k6.io');
  sleep(1);
}
```

根据我们前面配置的端口，稍微修改一下这个脚本

```javascript
import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  // A number specifying the number of VUs to run concurrently.
  vus: 10,
  // A string specifying the total duration of the test run.
  duration: '30s',
};

export default function() {
  http.get('http://127.0.0.1:8888');
}
```

#### 执行压力测试

```bash
k6 run fast-server.js
```

![fast-server压力测试结果](/images/fast-server-performance.png)
可以看到，在AMD R5 3600（6C12T）的macOS系统上，跑出了5万多的QPS，而且最大响应时间是14ms，可能用C可以写出更快的服务，但Rust的方式更加简单、直接。

上面只是为了证明后端服务不是我们整个实验的瓶颈，接下来开始编写OkHttp相关的代码。

### OkHttp测试代码

相关代码见[lovelock/okhttp-performance-comparison](https://github.com/lovelock/okhttp-performance-comparison)

启动服务，并使用VisualVM观察资源占用情况。

#### 对比——后端服务快

![多线程VisualVM监控](/images/okhttp-multi-thread-vvm.png)
![多线程压测结果](/images/okhttp-multi-thread-k6.png)
![异步VisualVM监控](/images/okhttp-async-vvm.png)
![异步压测结果](/images/okhttp-async-k6.png)

可以看到，多线程模式比异步模式使用的占用的内存多了3倍，但多线程模式的QPS要高于异步模式80%。

但是，这其实并没有模拟真实的线上场景，因为线上的场景有以下几个特点

1. 后端服务没有那么快
2. 要放在更长的时间跨度来整体看

但这也可以反过来说明如果后端服务非常快，而且对内存没那么敏感，就可以使用更简单的多线程模式。

接下来我们让后端服务变慢再来看看效果。

#### 对比——后端服务慢

把上面Rust服务的`index`方法改造一个这样（注意`use std::time::Duration;`）

```rust
// basic handler that responds with a static string
async fn index() -> &'static str {
    std::thread::sleep(Duration::from_millis(50));
    "Hello, World!"
}
```

重新运行服务并压测

![fast-server-with-sleep](/images/fast-server-with-sleep.png)
