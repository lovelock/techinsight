---
title: "使用Lima管理macOS上的Linux虚拟机"
date: 2024-04-05T23:11:59+08:00
image: /images/covers/Lima-for-linux-virtual-machine-on-macOS.png
hidden: false
comments: true
---

## 背景

一直以来，尤其是自从使用Apple Silicon的芯片的MacBook Pro以来，在macOS上使用Linux虚拟机就变得很困难了，加上我家里用的是Ryzentosh，两台电脑都很难使用虚拟机，就搞得很头疼。尤其最近需要调试那个C语言的程序，依赖一些libevent、inotify这类东西，不想把宿主机搞得太乱，所以选择一个虚拟机管理器的事情又得重新考虑了。

Intel芯片的macOS还是有很多选择的，Parallels Desktop就不说了，唯一的缺点就是贵，只说免费的方案。

VirtualBox肯定是首选，但在Apple Silicon芯片发布后5年后的今天（2024年4月），支持苹果M系列芯片的版本仍然没有发布，甚至早前公布的虽然不可用的预览版也早已下架了，搞不好Oracle内部早已经放弃了。

废话不多说，直接介绍今天的主角吧，Lima——Linux Machine，名字简单直接，其实我第一次看到类似的名字是Colima，是在apppleboy64大佬的博客上看到的，是一个本地管理K3s的工具，后来顺着了解到了Lima，可以理解为为了在macOS上运行Containerd而需要先启动一个Linux虚拟机，那么这个Lima就是为了运行这个虚拟机的。但我们现在要的就是这个虚拟机，至于后面是否要用K3s/K8s，不是现在考虑的事情。

其实所有这些东西背后都是[QEMU](https://www.qemu.org/docs/master/system/introduction.html)，无非是使用哪个前端了。我知道的还有一个[libvirt](https://libvirt.org/)，但配置相对很复杂，而我只需要一个能简单run起来的虚拟机而已，所以使用如此简单的Lima几乎是一个完美的选择。

## 快速入门

### 安装

前面说了，我们是要在macOS平台上使用，那么肯定优先选择用homebrew安装了。

```bash
brew install lima
```

可以看到，会自动安装`QEMU`依赖。

### 配置虚拟机

```bash
limactl start
```

这时会弹出几个选项，不要着急选，先看下自己的需求

```
$ limactl start
? Creating an instance "default"  [Use arrows to move, type to filter]
> Proceed with the current configuration
  Open an editor to review or modify the current configuration
  Choose another template (docker, podman, archlinux, fedora, ...)
  Exit
...
INFO[0029] READY. Run `lima` to open the shell.
```

默认用的是Ubuntu 23.10，我不喜欢用Ubuntu，所以会先选择` Choose another template (docker, podman, archlinux, fedora, ...)`来重新配置，比如我选择了Debian 12，配置如下

```
# This template requires Lima v0.7.0 or later
images:
  # Try to use release-yyyyMMdd image if available. Note that release-yyyyMMdd will be removed after several months.
  - location: "https://cloud.debian.org/images/cloud/bookworm/20240211-1654/debian-12-genericcloud-amd64-20240211-1654.qcow2"
    arch: "x86_64"
    digest: "sha512:6856277491c234fa1bc6f250cbd9f0d44f77524479536ecbc0ac536bc07e76322ebb4d42e09605056d6d3879c8eb87db40690a2b5dfe57cb19b0c673fc4c58ca"
  - location: "https://cloud.debian.org/images/cloud/bookworm/20240211-1654/debian-12-genericcloud-arm64-20240211-1654.qcow2"
    arch: "aarch64"
    digest: "sha512:c8f3746aa979cdc95c13cd4b8cc032151f1e5685525a85c2b3b2e30defa02dacb1058b68f955ac16f3f2dbd473d13dfef15d2a22f348bcc4abb427e0713fa9a4"
  # Fallback to the latest release image.
  # Hint: run `limactl prune` to invalidate the cache
  - location: "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2"
    arch: "x86_64"
  - location: "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-arm64.qcow2"
    arch: "aarch64"
mounts:
  - location: "~"
  - location: "/tmp/lima"
    writable: true
```

绝大多数情况下，前面`images`相关的配置我们完全不用关心，只需要知道它能虚拟出来一个完整的虚拟机就行了，最重要的是`mounts`选项，不得不说，`yaml`配置真是很难读

```
mounts:
  - location: "~"
  - location: "/tmp/lima"
    writable: true
```

这个配置的意思是它会把`~`也就是宿主机的家目录挂载到虚拟机，让我们可以在虚拟机内访问到宿主机家目录中的问题，但默认是只读的，不要以为这里有`writable: true`就不用管了，其实这个`writable`是给`/tmp/lima`用的，所以需要简单修改一下，改成

```
mounts:
  - location: "~"
    writable: true
  - location: "/tmp/lima"
    writable: true
```

就可以保存了，一直下一步就可以了。这里如果不用魔法可能会非常慢，具体这里就不说了，自己想办法解决。

### 访问虚拟机

这就是为什么我说Lima几乎完美的原因了，它是真的知道开发人员需要什么，跟我大声说——SSH！所以默认启动之后就配置好了ssh访问，可以执行`lima`命令进入虚拟机。

> 注意：这是因为前面我们没有指定虚拟机的名字，所以默认是`default`，所以执行`lima`也就不需要指定名字了。如果你想启动多个虚拟机，相应的命令可以替换成`limactl start debian`、`lima debian`这样。

这时候更有意思的来了，进虚拟机之后它会把你当前在宿主机的位置带进虚拟机，如果你不小心去了别的目录，还想回到宿主机的家目录，只需要`cd /Users/your_name/path/to/your/location/`就行了，别提多贴心了。

现在你可以开心地使用虚拟机了，是不是很有WSL的味道？

## One More Thing

考虑以下两种情况

1. 在Apple Silicon的芯片上运行X86_64的Linux虚拟机
2. 在Ryzontosh上运行虚拟机

QEMU表示：我太难了！！！

但还是可以的，第一种情况你在前面编辑配置的时候可能已经看到了，配置文件中有几项带默认值的，这里简单列一下

| key      | value                      |
| -------- | -------------------------- |
| `vmType` | 默认QEMU就行了，vz性能更差 |

|`
os` | 也不用动，你既然找它肯定是要用Linux |
|`
arch` |关键就是这里了，Apple Silicon的机器默认肯定都选的是`aarch64`，但如果确实需要X86的虚拟机，可以改成
`x86_64`

第二种情况，需要手动给QEMU[指定运行参数](https://www.reddit.com/r/Ryzentosh/comments/g8pl8p/any_virtualization_support/)，把加上`
QEMU_SYSTEM_X86_64="QEMU-system-x86_64 -cpu max -machine q35"`环境变量再执行`limactl start`就可以了，但运行速度会比较慢就是了。

那么好奇的小朋友就会问了，这是为什么呢？

先看下GPT对于QEMU和KVM的区别的说明

> QEMU（Quick Emulator）和 KVM（Kernel-based Virtual Machine）之间的关系是相互补充的，它们一起在Linux上提供了一种高效的虚拟化解决方案。
> QEMU是一个通用的开源机器模拟器和虚拟器。它可以执行硬件虚拟化，使您能够运行一个操作系统的完整副本（称为客户机或虚拟机）在另一个操作系统上。QEMU可以在用户模式下运行，提供软件仿真虚拟化，但这通常会导致较慢的性能。
> KVM是Linux内核的一部分，它允许Linux将自身转换为一个类型1（裸金属）的虚拟机监控器。KVM需要处理器支持硬件虚拟化扩展（Intel的VT-x或AMD的AMD-V）。当KVM用于QEMU时，它提供硬件辅助虚拟化，显著提高虚拟机的性能，特别是对于CPU密集型应用程序。
> KVM本身不执行任何模拟，它依赖于用户空间程序（如QEMU）来设置虚拟机的环境、虚拟硬件等。QEMU在使用KVM时，负责设备模拟，而CPU密集型任务则由KVM在硬件虚拟化扩展的帮助下运行，这样可以近乎本地速度执行虚拟机。
>
> 简单来说，QEMU用于模拟硬件，而KVM让QEMU利用CPU扩展来提供更快的虚拟化性能。如果无法使用KVM（例如在不支持硬件虚拟化的平台上），QEMU仍然可以独立工作，只是性能会有所下降。

可以理解为Hypervisor.Framework就是macOS平台上的KVM，而在Ryzentosh上，无法访问Hypervisor.Framework，所以就只能完全依赖QEMU自己模拟和计算了，经过一层转化自然就慢了。
