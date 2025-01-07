---
title: "PHP解决curl响应过大时爆内存的问题"
date: 2024-04-09T17:46:03+08:00
image: /images/covers/curl-with-large-response-oom-fix.png
hidden: false
comments: true
tags: ["PHP", "curl"]
---

PHP 调用 http 服务此前一直都是封装的 curl，这事儿我也干过不少次了，不过今天碰到了一个新问题。

接口是 clickhouse 服务，查询的响应体比较大，放在内存里要超过 1 G，再继续修改 `max_memory_limit` 意义不大，所以就希望把结果直接放入文件，然后逐行读取处理，以减少整个过程的内存消耗，那么怎么把结果写入文件呢？

相关的选项是这个

```php
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
```

这个选项设置为 `1/true` 时，就会把结果放在 `$response = curl_exec($ch)` 里的这个 `$response` 里，这也是现在这个问题的来源，`$response` 太大了。但如果把它设置为 `0/false`，它会写到标准输出，又没办法用代码处理。

参考了[这个问题](https://stackoverflow.com/questions/7967531/php-curl-read-remote-file-and-write-contents-to-local-file)，给出了两个思路。

{{< bilibili "//player.bilibili.com/player.html?aid=1302993488&bvid=BV1DM4m1Q71a&cid=1499653065&p=1"  >}}

## 直接写入文件

```php
$fh = fopen($file, 'w');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 0);
curl_setopt($ch, CURLOPT_FILE, $fh);
```

一定要注意的是，如果 `$file` 对应的目录不存在，则无法自动创建目录，整个过程会失败。

## 写回调方法

```php
# setup a global file pointer
$GlobalFileHandle = null;

function saveRemoteFile($url, $filename) {
  global $GlobalFileHandle;

  set_time_limit(0);

  # Open the file for writing...
  $GlobalFileHandle = fopen($filename, 'w+');

  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, $url);
  curl_setopt($ch, CURLOPT_FILE, $GlobalFileHandle);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, false);

  # Assign a callback function to the CURL Write-Function
  curl_setopt($ch, CURLOPT_WRITEFUNCTION, 'curlWriteFile');

  # Exceute the download - note we DO NOT put the result into a variable!
  curl_exec($ch);

  # Close CURL
  curl_close($ch);

  # Close the file pointer
  fclose($GlobalFileHandle);
}

function curlWriteFile($cp, $data) {
  global $GlobalFileHandle;
  $len = fwrite($GlobalFileHandle, $data);
  return $len;
}
```

这个看起来有点多此一举了，因为不指定这个回调函数也会写入这个方法，只是无法对写入的方式做一些精细控制，这个回调函数多数时候是不需要的，因为我更倾向于先整体写入文件，上层的方法再根据业务需求去处理，而不是在这里决定。
