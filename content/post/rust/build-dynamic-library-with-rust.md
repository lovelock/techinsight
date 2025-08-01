---
title: "使用 Rust 开发动态链接库（.so）完整指南"
description: 
date: 2025-08-01T16:14:03+08:00
image: 
math: true
license: 
hidden: false
comments: true
categories: ["rust"]
tags: ["clang"]
---

## 目录

[项目创建与配置](#1-项目创建与配置)
[Rust 代码编写规范](#2-rust-代码编写规范)
[头文件生成与管理](#3-头文件生成与管理)
[构建系统实现](#4-构建系统实现)
[安装与分发](#5-安装与分发)
[调用示例](#6-调用示例)
[跨平台注意事项](#7-跨平台注意事项)
[最佳实践](#8-最佳实践)

## 项目创建与配置

### 初始化项目

```bash
cargo new --lib rust_so_lib
cd rust_so_lib
```

### Cargo.toml 配置

```toml
[package]
name = "rust_so_lib"
version = "0.1.0"
edition = "2021"

[lib]
name = "rust_so_lib"
crate-type = ["cdylib"]# 关键配置：生成动态链接库

[dependencies]
libc = "0.2"# 用于C类型兼容
```

> **重要提示**：确保不要同时使用 `[workspace]` 和 `[lib]` 配置，否则会导致编译错误。

## Rust 代码编写规范

### 基础示例 (src/lib.rs)

```rust
use std::os::raw::{c_int, c_char};
use std::ffi::{CString, CStr};

#[unsafe(no_mangle)]
pub extern "C" fn add_numbers(a: c_int, b: c_int) -> c_int {
    a + b
}

#[unsafe(no_mangle)]
pub extern "C" fn string_length(s: *const c_char) -> c_int {
    let c_str = unsafe { CStr::from_ptr(s) };
    c_str.to_bytes().len() as c_int
}

#[unsafe(no_mangle)]
pub extern "C" fn create_greeting(name: *const c_char) -> *mut c_char {
    let name_str = unsafe { CStr::from_ptr(name).to_string_lossy() };
    let greeting = format!("Hello, {}!", name_str);
    CString::new(greeting).unwrap().into_raw()
}

#[unsafe(no_mangle)]
pub extern "C" fn free_string(s: *mut c_char) {
    unsafe { CString::from_raw(s) };
}
```

### 关键编程要点

1. **ABI 兼容性**：
- 使用 `extern "C"` 确保C兼容调用约定
- `#[unsafe(no_mangle)]` 禁止名称修饰
2. **类型映射**：
   
   | Rust 类型       | C 类型        |
   | --------------- | ------------- |
   | `c_int`         | `int`         |
   | `*const c_char` | `const char*` |
   | `*mut c_char`   | `char*`       |

3. **内存安全**：
- Rust分配的内存应由Rust释放
- 提供明确的资源释放函数（如`free_string`）

## 头文件生成与管理

### 手动创建头文件

```c
// rust_so_lib.h
#ifndef RUST_SO_LIB_H
#define RUST_SO_LIB_H

#ifdef __cplusplus
extern "C" {
#endif

int add_numbers(int a, int b);
int string_length(const char* s);
char* create_greeting(const char* name);
void free_string(char* s);

#ifdef __cplusplus
}
#endif

#endif // RUST_SO_LIB_H
```

### 使用 cbindgen 自动生成

1. 安装工具：
   
   ```bash
   cargo install cbindgen
   ```

2. 配置文件 (cbindgen.toml)：
   
   ```toml
   language = "C"
   include_guard = "RUST_SO_LIB_H"
   autogen_warning = "/* AUTO-GENERATED FILE, DO NOT EDIT */"
   ```

3. 生成命令：
   
   ```bash
   cbindgen --config cbindgen.toml --crate rust_so_lib --output rust_so_lib.h
   ```

## 构建系统实现

### 完整 Makefile

```makefile
# 项目配置
TARGET := rust_so_lib
VERSION := 0.1.0
PREFIX ?= /usr/local
LIBDIR := $(PREFIX)/lib
INCLUDEDIR := $(PREFIX)/include

# 构建目标
RUST_TARGET := release
RUST_LIB := target/$(RUST_TARGET)/lib$(TARGET).so
HEADER := $(TARGET).h

.PHONY: all build install uninstall clean test

all: build

build:
cargo build --$(RUST_TARGET)

install: build
install -d $(LIBDIR) $(INCLUDEDIR)
install -m 755 $(RUST_LIB) $(LIBDIR)/lib$(TARGET).so.$(VERSION)
ln -sf lib$(TARGET).so.$(VERSION) $(LIBDIR)/lib$(TARGET).so
install -m 644 $(HEADER) $(INCLUDEDIR)
ldconfig

uninstall:
rm -f $(LIBDIR)/lib$(TARGET).so*
rm -f $(INCLUDEDIR)/$(HEADER)
ldconfig

clean:
cargo clean
rm -f *.o *.a *.so test_$(TARGET)

test: $(RUST_LIB)
$(CC) test.c -o test_$(TARGET) -l$(TARGET) -Ltarget/$(RUST_TARGET) -I.
LD_LIBRARY_PATH=target/$(RUST_TARGET) ./test_$(TARGET)
```

### Makefile 功能说明

| 命令             | 功能描述                |
| ---------------- | ----------------------- |
| `make`           | 构建Release版本的动态库 |
| `make install`   | 安装到系统目录          |
| `make uninstall` | 卸载已安装的库          |
| `make clean`     | 清理所有生成文件        |
| `make test`      | 编译并运行测试程序      |

## 安装与分发

### 标准安装流程

```bash
cargo build --release
sudo make install
```

### 自定义安装路径

```bash
make install PREFIX=/custom/install/path
```

### 分发包内容

建议包含以下文件结构：

```
dist/
├── include/
│└── rust_so_lib.h# 头文件
├── lib/
│└── librust_so_lib.so # 动态库
└── examples/# 调用示例
└── test.c
```

## 调用示例

### C 语言示例 (test.c)

```c
#include <stdio.h>
#include "rust_so_lib.h"

int main() {
   // 数值计算
   printf("3 + 5 = %d\n", add_numbers(3, 5));

   // 字符串处理
   const char* name = "Rust";
   char* greeting = create_greeting(name);
   printf("%s\n", greeting);
   printf("String length: %d\n", string_length(greeting));
   free_string(greeting);

   return 0;
}
```

### 编译与运行

```bash
# 动态链接方式
gcc test.c -o test -lrust_so_lib -Ltarget/release
LD_LIBRARY_PATH=target/release ./test

# 静态链接方式
gcc test.c -o test target/release/librust_so_lib.so
```

## 跨平台注意事项

### 平台差异处理

```makefile
# 在Makefile中添加平台检测
UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
LIB_EXT := dylib
LDLIBS := -Wl,-rpath,@loader_path
else ifeq ($(OS), Windows_NT)
LIB_EXT := dll
LDLIBS := -Wl,-rpath='$$ORIGIN'
else
LIB_EXT := so
LDLIBS := -Wl,-rpath=\$$ORIGIN
endif
```

### Windows 特殊处理

1. 修改 Cargo.toml：
   
```toml
[target.'cfg(windows)'.dependencies]
winapi = { version = "0.3", features = ["winbase"] }
```

2. 添加 DLL 导出属性：
   
```rust
#[cfg_attr(target_os = "windows", link(name = "rust_so_lib"))]
extern "C" {
// 导出函数
}
```

## 最佳实践

### 接口设计原则

1. **保持接口稳定**：
- 使用版本号控制ABI兼容性

- 避免频繁变更函数签名
2. **内存管理规范**：

```rust
// 明确所有权转移
#[unsafe(no_mangle)]
pub extern "C" fn create_buffer(size: usize) -> *mut u8 {
   let mut buf = Vec::with_capacity(size);
   let ptr = buf.as_mut_ptr();
   std::mem::forget(buf); // 明确转移所有权
   ptr
}

#[unsafe(no_mangle)]
pub extern "C" fn free_buffer(ptr: *mut u8, size: usize) {
   unsafe { Vec::from_raw_parts(ptr, 0, size) };
}

```
### 错误处理模式
```rust
#[repr(C)]
pub enum ErrorCode {
   Success = 0,
   InvalidInput = 1,
   MemoryError = 2,
}

#[unsafe(no_mangle)]
pub extern "C" fn safe_operation(input: *const c_char) -> ErrorCode {
   if input.is_null() {
   return ErrorCode::InvalidInput;
}
// ...操作逻辑
ErrorCode::Success
}
```

### 性能优化建议

1. **批量数据处理**：

```rust
#[unsafe(no_mangle)]
pub extern "C" fn process_batch(
   inputs: *const c_int,
   count: usize,
   outputs: *mut c_int
   ) {
   let inputs = unsafe { std::slice::from_raw_parts(inputs, count) };
   let outputs = unsafe { std::slice::from_raw_parts_mut(outputs, count) };
   // 批量处理...
}
```

2. **零拷贝接口**：

```rust
#[unsafe(no_mangle)]
pub extern "C" fn get_data(buffer: *mut u8, max_size: usize) -> usize {
   let data = generate_data(); // Rust端生成数据
   let copy_size = data.len().min(max_size);
   unsafe {
   std::ptr::copy_nonoverlapping(data.as_ptr(), buffer, copy_size);
   }
   copy_size
}
```

通过本指南，您可以系统性地掌握使用 Rust 开发生产级动态库的全流程，从项目创建、代码编写、构建系统到分发部署的完整知识体系。实际开发中应根据具体需求调整接口设计和构建流程。
