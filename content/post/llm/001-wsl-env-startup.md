---
title: "001 Wsl Env Startup"
description: 
date: 2025-10-03T23:23:30+08:00
image: 
math: true
license: 
hidden: false
comments: true
draft: true
categories: []
tags: []
---

## 安装Ubuntu WSL

```bash
PS C:\Users\frost> wsl --install -d Ubuntu
正在下载: Ubuntu
正在安装: Ubuntu
已成功安装分发。可以通过 “wsl.exe -d Ubuntu” 启动它
正在启动 Ubuntu...
Provisioning the new WSL instance Ubuntu
This might take a while...
Create a default Unix user account: frost
New password:
Retype new password:
passwd: password updated successfully
To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.
```

### 1. 安装ROCm

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y wget gpg build-essential libnuma-dev
# 1. 创建密钥存储目录
sudo mkdir --parents --mode=0755 /etc/apt/keyrings

# 2. 下载并导入 AMD 公钥
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/rocm.gpg > /dev/null

# 3. 添加 AMDGPU 驱动源（ROCm 依赖）
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/amdgpu/6.2.4/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/amdgpu.list

# 4. 添加 ROCm 软件源
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/6.2.4 noble main" | sudo tee /etc/apt/sources.list.d/rocm.list

# 5. 设置源优先级（避免与系统包冲突）
echo -e 'Package: *\nPin: release o=repo.radeon.com\nPin-Priority: 600' | sudo tee /etc/apt/preferences.d/rocm-pin-600
# 更新源索引
sudo apt update

# 安装 ROCm 完整套件（含 HIP SDK、运行时等）
sudo apt install -y rocm-hip-sdk rocm-opencl-sdk rocm-core

# 若提示依赖冲突，执行以下命令修复
sudo apt --fix-broken install -y
```