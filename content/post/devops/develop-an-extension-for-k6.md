---
title: "为 Grafana k6 编写 YAR 协议扩展：从 Go 到 JavaScript 的无缝集成"
description: 
date: 2025-02-25T19:00:09+08:00
image: 
math: true
license: 
hidden: false
comments: true
categories: ["go"]
tags: ["基准测试", "性能优化", "k6"]
---

最近，我为 Grafana k6 编写了一个支持 YAR 协议的扩展，整个过程非常有趣且充满挑战。在这篇博客中，我将分享如何从零开始实现这个扩展，并解释其中的一些关键细节。特别地，我会详细说明为什么在 Go 中定义的是 `NewClient` 方法，但在 JavaScript 中调用的是 `newClient`，以及这背后的机制。

---

## 1. 背景

### 什么是 Grafana k6？
Grafana k6 是一个开源负载测试工具，专注于性能和可靠性测试。它允许用户使用 JavaScript 编写测试脚本，并通过虚拟用户（VU）模拟高并发场景。

### 什么是 YAR 协议？
YAR（Yet Another RPC）是一个轻量级的 RPC 协议，常用于高性能的远程服务调用。为了更好地测试 YAR 服务，我决定为 k6 编写一个扩展，使其能够直接调用 YAR 协议。

---

## 2. 实现过程

### 2.1 编写 YAR 客户端
首先，我用 Go 编写了一个 YAR 客户端，代码如下：

```go
package client

import (
	"git.happyhacker.fun/frost/yargo/protocol"
)

type YarClient struct {
	hostname   string
	port       int
	persistent bool
	timeout    int
}

func (c *YarClient) Call(request protocol.Request, params ...any) (*protocol.Response, error) {
	// 实现 YAR 调用逻辑
}
```

### 2.2 创建 k6 扩展
接下来，我将这个 YAR 客户端封装为 k6 扩展。k6 允许通过 Go 编写扩展，并将其暴露给 JavaScript 运行时。

```go
package yar

import (
	"go.k6.io/k6/js/modules"
	"git.happyhacker.fun/frost/yargo/protocol"
)

type YarClient struct {
	client *client.YarClient
}

func init() {
	modules.Register("k6/x/yar", new(YarClient))
}

func (y *YarClient) NewClient(hostname string, port int, persistent bool, timeout int) *YarClient {
	y.client = &client.YarClient{
		Hostname:   hostname,
		Port:       port,
		Persistent: persistent,
		Timeout:    timeout,
	}
	return y
}

func (y *YarClient) Call(request protocol.Request, params ...any) (*protocol.Response, error) {
	return y.client.Call(request, params...)
}
```

### 2.3 编译 k6 扩展
使用 `xk6` 工具将扩展编译到 k6 二进制文件中：

```bash
xk6 build --with k6-yar=.
```

### 2.4 编写 k6 测试脚本
最后，我编写了一个 k6 测试脚本来使用这个扩展：

```javascript
import yar from 'k6/x/yar';

let client = yar.newClient("127.0.0.1", 8009, true, 5);

export default function () {
  let request = yar.newRequest("default");
  let response = client.call(request);
  console.log(JSON.stringify(response));
}
```

---

## 3. 关键细节：为什么 `NewClient` 变成了 `newClient`？

在实现过程中，我一度困惑：为什么在 Go 中定义的是 `NewClient` 方法，但在 JavaScript 中调用的是 `newClient`？这是否是一个错误？

### 3.1 Go 的方法命名
在 Go 中，方法名通常采用 **PascalCase**（首字母大写），以表示其公开性。因此，我定义了 `NewClient` 方法：

```go
func (y *YarClient) NewClient(hostname string, port int, persistent bool, timeout int) *YarClient {
	// 初始化 YAR 客户端
}
```

### 3.2 JavaScript 的命名规则
在 JavaScript 中，函数名通常采用 **camelCase**（首字母小写），以符合语言的习惯用法。k6 的模块系统会自动将 Go 方法名转换为 JavaScript 风格的命名。

因此，`NewClient` 在 JavaScript 中变成了 `newClient`。

### 3.3 k6 的模块注册机制
k6 的 `modules.Register` 方法会将 Go 结构体的方法暴露给 JavaScript 运行时，并自动进行命名转换。例如：
- `NewClient` → `newClient`
- `Call` → `call`

这种转换是 k6 设计的一部分，旨在让 JavaScript 代码更加符合语言习惯。

---

## 4. 遇到的问题与解决方案

### 4.1 `replace` 指令未生效
在 `xk6 build` 过程中，我发现 `go mod replace` 指令未生效，导致构建工具仍然尝试从原始路径下载依赖。通过显式指定 `replace` 标志解决了这个问题：

```bash
xk6 build --with k6-yar=. -replace git.happyhacker.fun/frost/yargo=../path/to/your/yar/client
```

### 4.2 VU 配置
在测试过程中，我通过 `options` 灵活配置了虚拟用户（VU）的数量和行为。例如：

```javascript
export const options = {
  vus: 10,
  duration: '30s'
};
```

---

## 5. 总结

通过为 Grafana k6 编写 YAR 协议扩展，我不仅加深了对 k6 和 Go 的理解，还体会到了跨语言开发的乐趣。特别地，`NewClient` 到 `newClient` 的命名转换让我意识到，框架设计中的细节往往是为了让开发者更加专注于业务逻辑，而不是被语言差异所困扰。

如果你也有兴趣为 k6 编写扩展，不妨从一个小功能开始，逐步探索其强大的能力。希望这篇博客能为你的开发之旅提供一些帮助！

---

## 参考链接
- [Grafana k6 官方文档](https://k6.io/docs/)
- [xk6 项目](https://github.com/grafana/xk6)
- [YAR 协议介绍](https://en.wikipedia.org/wiki/YAR)

Happy coding! 🚀