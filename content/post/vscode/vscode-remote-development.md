---
title: "VSCode远程开发初体验"
description: 
date: 2024-07-17T14:53:16+08:00
image: 
math: 
license: 
hidden: false
comments: true
---

之前体验过一把IDEA的远程开发，只能说能看出来IntelliJ想把功能做到很完善，也确实做到了，但由于占用资源太多，即使远程使用的是配置相对非常高的服务器，占用10G+的内存也不是一个好的选择吧，尝试了几次之后就被惊人的延迟和频繁丢失的输入给劝退了。

听说VSCode的远程开发效果非常不错，所以想尝试一下。只需要给服务器开一个专用的SSH端口，把用密码登录的选项禁用掉，就相对安全了。只要有了SSH通道，整个配置就已经完成了，对，就是这么简单。

以RockyLinux8的容器为例。

## 在容器中安装并启动SSH服务

```sh
dnf install -y ssh-server
/usr/sbin/ssh-server
```

这时不出意外会报错，因为配置文件中指定的key文件不存在，执行以下三条命令之后就好了。

```sh
ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key
ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key
```

## 创建一个开发专用的账号，赋予一个登录的shell，指定Home目录，并赋予相应的权限。

```sh
useradd dev
usermod -s /bin/bash dev
usermod -aG wheel dev
usermod -d /data1/code dev
chown -R dev. /data1/code
```

好了，现在`/data1/code`已经是`dev`账户的家目录了。

现在设置登录相关的信息。随便设置一个密码，其实可以尽量复杂一些。

```sh
passwd dev #接下来要输入密码
```

这时候尝试从远程登录，可能会这个错误

```plaintext
System is booting up. Unprivileged users are not permitted to log in yet. Please come back later. For technical details, see pam_nologin(8).
```

你知道，系统并没有正在启动，这明显是一个误报。针对不同的系统可能不同，对于Rocky Linux 8而言，需要删除`/run/nologin`文件，再尝试登录就可以了。

> 删除的这个文件中的内容恰恰就是上面的报错信息，意外吧。

## 修改sshd配置文件

密码登录既不方便也不安全，需要先用`ssh-copy-id`来实现证书登录，再从服务端关闭密码登录功能。

```sh
ssh-copy-id dev@remote-host -p{newPort}
```

这就可以了。然后在服务端的`/etc/ssh/sshd_config`中找到

```conf
PasswordAuthentication yes
```

把`yes`改成`no`，重启ssh-server，就会发现已经无法用密码登录了，也就安全了。

搞定了。

## 总结

最近使用VSCode比较多，我发现其实绝大多数情况下使用VSCode就已经够了，完全不需要JetBrains家的产品了，甚至JB家引以为傲的Java开发好像也没有那么大的优势了，jdt-lsp的很多提示已经比IDEA更友好了，更容易在代码上线运行之前就发现问题。举一个例子

```java

@Builder
public class Data {
    private Integer age = 0;
}
```

上面的代码非常具有迷惑性，因为实际运行时你会发现，如果没有执行`.age()`方法，这个值将是`null`，而不是0，这在VSCode中就会提示如果不使用`@Builder.Default`，则代码中指定的这个`=0`的值将直接被抛弃。这非常有用。
