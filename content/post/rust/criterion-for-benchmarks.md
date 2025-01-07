---
title: "使用 Rust Criterion 进行性能基准测试"
description:
date: 2024-11-15T09:56:01+08:00
image:
math: true
license:
hidden: false
comments: true
categories: ["rust"]
tags: ["基准测试", "性能测试", "实战"]
---

在 Rust 开发中，性能基准测试是非常重要的一环，能够帮助开发者评估代码的性能并进行优化。`Criterion.rs` 是一个强大的 Rust 基准测试框架，它提供了简单易用的接口和丰富的功能。本文将介绍如何使用 `Criterion` 进行基准测试，以及一些注意事项。

### 1. 什么是 Criterion.rs？

`Criterion.rs` 是一个用于 Rust 的基准测试库，旨在取代 Rust 标准库中的基准测试功能。它提供更精确的测量手段和更好的报告功能，能够帮助开发者深入了解代码的性能表现。

### 2. 安装 Criterion.rs

要在项目中使用 `Criterion.rs`，首先需要在 `Cargo.toml` 文件中添加依赖。你可以使用以下命令来安装：

```toml
[dev-dependencies]
criterion = "0.5.1"
```

注意：这个依赖是添加在`dev-dependencies`中的，所以不能直接用`cargo add criterion`来安装。那么它有两种方式实现

1. 编辑`Cargo.toml`

这是废话

2. 通过`cargo-edit`

```bash
cargo install cargo-edit
cargo add --dev criterion
```

安装`cargo-edit`就是为了能让`cargo add`支持一个`--dev`的选项。

### 3. 创建基准测试

创建一个基准测试非常简单。首先，在项目的 `benches` 目录中创建一个新的基准测试文件，例如 `benches/bench_hash.rs`。以下是一个简单的例子：

```rust
// benches/bench_hash.rs
use criterion::{criterion_group, criterion_main, Criterion};
use deduplicate::file_info;

fn bench_hash() {
    let path = "/path/to/a/file";

    file_info::sha256_hash(path);
}

fn benchmark_hash(c: &mut Criterion) {
    c.bench_function("benchmark_sha256", |b| b.iter(|| bench_hash()));
}

criterion_group!(benches, benchmark_hash);
criterion_main!(benches);
```

在这个例子中，我们定义了一个 `bench_hash()` 方法，用来调用你的`lib.rs`中已经定义过的`file_info::sha256_hash()`方法，这里只是为了给它一个输入参数，并创建了一个基准测试来测量其性能。`c.bench_function` 函数接收一个名称和一个闭包作为参数，闭包中是我们希望基准测试执行的代码。

### 4. 运行基准测试

要运行基准测试，你可以使用以下命令：

```bash
cargo bench
```

这时你会发现基准测试并没有执行，这是因为还需要在`Cargo.toml`中添加下列的内容

```toml
[[bench]
name = "bench_hash"
harness = false
```

这里解释一下这几行的含义
1. `name = "bench_hash"` 告诉criterion去`benches`目录中找`bench_hash.rs`或`bench_hash/main.rs`
2. `harness = false` cargo自带的bench是使用harness，这也是个基准测试框架，但我们现在要用的是一个第三方的框架，所以就要把内置的框架给禁用掉

以此类推，还可以定义更多的`[[bench]]`。

### 5. 输出结果

运行基准测试后，`Criterion.rs` 将会生成详细的输出，显示每个基准测试的平均时间、标准差、样本数量等信息。这些结果可以帮助你了解代码在不同条件下的表现。

### 6. 自定义

#### 迭代次数

对于比较慢的方法，默认会运行100个迭代，如果你的方法非常慢，就会消耗大量时间，比如像上面的给文件计算SHA256散列值的，对于大文件来说就会很慢，这时可能会希望减少执行次数来减少等待时间。通过自定义`criterion_group!(benches, benchmark_hash);`这行来解决

```rust
criterion_group!(
    name = benches;
    config = Criterion::default().sample_size(10).warm_up_time(Duration::from_secs(20));
    targets = benchmark_hash
);
```

其中`sample_size`就是迭代次数，不能低于10，`warm_up_time`是预热用的时间，有兴趣可以再研究其他的选项。

注意：`criterion_group!`是一个宏，里面的三行结尾就是`;`，而不是`,`，我没有写错，`targets`可以有多个，可以自己尝试一下。

#### 日志

一般最简单的日志可以通过`log`接口和`env_logger`来实现，而`env_logger`在使用之前需要执行一次`env_logger::init()`，可以放在这里

```rust
fn benchmark_hash(c: &mut Criterion) {
    env_logger::init();
    c.bench_function("benchmark_sha256", |b| b.iter(|| bench_hash()));
}
```

当然如果要定义多个类似`benchmark_hash`的函数，这也会有一些冲突，就需要`once_cell`或`lazy_static`等其他方案了。

#### 输出结果

安装`criterion`时有一个选项是使用`html_report`，默认会使用gnuplot来画图，但rust里有一个比较好的实现是plotters，所以如果没有安装gnuplot就会默认使用plotters。

```
Gnuplot not found, using plotters backend
```

```toml
[dev-dependencies]
criterion = { version = "0.5.1", features = ["html_reports"] }
```

这样执行完之后会生成`target/criterion`目录，其中有`/report/index.html`文件，用浏览器打开，会看到类似这样的结果

![](../images/rust/criterion_plotters_report.png)

非常美观了，从直线的情况来看，说明并没有随着运行次数的增加性能变差。

#### 调优

运行性能测试肯定是为了调优，当你调整了代码，再次执行时，会得到一个类似这样的报告

```
benchmark_sha256        time:   [40.128 µs 40.160 µs 40.191 µs]
                        change: [-0.5928% -0.3165% -0.0596%] (p = 0.04 < 0.05)
                        Change within noise threshold.
Found 1 outliers among 10 measurements (10.00%)
  1 (10.00%) high mild
```

还是用截图会更直观一些，因为它带颜色

![](../images/rust/comparison.png)

就能看到每次的改动优化了多少，当然我这里没有改代码，所以基本上测试结果也没变化。

而运行第二次测试之后刚才的report也会更新，新增了一部分变成这样

![](../images/rust/bench_comparison.png)

可以说是非常贴心了。

### 7. 注意事项

- **多次运行**：`Criterion.rs` 会自动进行多次运行以提高结果的准确性。默认情况下，它会运行 100 次并根据结果进行统计分析。
- **测量影响**：基准测试可能会受到多种因素的影响，如 CPU 温度、背景进程等。在进行基准测试时，建议尽量减少外部干扰，最好在空闲的机器上运行。
- **避免优化**：在基准测试中，Rust 编译器可能会对未使用的结果进行优化。确保你的基准测试代码中使用了结果，可以通过将结果赋值给 `_` 变量来避免这种情况。例如：
- **清理数据**：`Criterion.rs` 会在每次运行后生成输出数据。可以通过删除 `target/criterion` 目录来清理旧的数据和基准测试结果。
- **使用基准聚合**：你可以将多个基准测试组合在一起以获得更全面的性能评估。使用 `criterion_group!` 和 `criterion_main!` 宏来组织你的基准测试。

### 8. 结论

`Criterion.rs` 是一个强大且灵活的基准测试工具，能够帮助 Rust 开发者获取详细的性能数据。通过遵循本文的步骤和注意事项，你可以有效地使用 Criterion 进行性能基准测试，从而找到代码中的瓶颈并进行优化。希望这篇文章能够帮助你更好地理解和使用 Criterion.rs，提升你的 Rust 编程能力！
