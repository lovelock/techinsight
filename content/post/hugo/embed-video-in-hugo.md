---
title: "在Hugo中嵌入视频"
date: 2024-04-16T21:50:49+08:00
image: /images/covers/embed-video-in-hugo.png
math: 
license: 
hidden: false
comments: true
tags:
    - hugo
---

仅半年在B站也发了不少视频，想着在博客上也能引用一下，但国内的视频网站嘛，海外的产品支持可能没有那么好，加上也想看看[Hugo的shortcode](https://gohugo.io/content-management/shortcodes/)到底是怎么工作的，所以就有了这篇文章。


## 找到要引用的视频地址

这并不是直接点开视频的播放地址，而是要使用嵌入地址，俗称落地页。在B站是这样的

![B站嵌入代码](/images/B站嵌入代码.png)

具体的内容是这样

```html
<iframe src="//player.bilibili.com/player.html?aid=1302993488&bvid=BV1DM4m1Q71a&cid=1499653065&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>
```

就是一段HTML片段。


## 优化引用地址

无意间搜到这篇文章[Embed Bilibili Video To HTML](https://leimao.github.io/blog/Embed-Bilibili-Video/)，博主指出B站的这个片段不是响应式的，对移动端的支持不好，提供了一种新的方式

```html
<div style="position: relative; padding: 30% 45%;">
<iframe style="position: absolute; width: 100%; height: 100%; left: 0; top: 0;" src="//player.bilibili.com/player.html?aid=1302993488&bvid=BV1DM4m1Q71a&cid=1499653065&p=1" frameborder="no" scrolling="no" allowfullscreen="true"></iframe>
</div>
```

简单对比一下就能发现其实是在外层嵌套了一些支持Responsive的样式，妙！

## Hugo的shortcode

没有仔细研读，看了一个例子基本就理解了，几个基本的规则

1. 基于新版本的目录结构，应该放在`layouts/shortcodes/name-of-short-code.html`中，其中`name-of-short-code`就是在文章中插入的名字，比如这里新建的文件名叫`bilibili`，那么就应该放在`layouts/shortcodes/bilibili.html`，而且具体的shortcode应该这么写`{{</* bilibili */>}}`
2. shortcode中除了写名字之外还有一些其他东西，这里就涉及到模板引擎了，写在shortcode名字后面的东西，可以通过`{{ .Get 0 }}`这种语法来获取，比如这个例子就是获取第一个参数

根据上面的例子，具体的shortcode内容是这样的

```html
<div style="position: relative; padding: 30% 45%;">
<iframe style="position: absolute; width: 100%; height: 100%; left: 0; top: 0;" src="{{ .Get 0 }}" frameborder="no" scrolling="no" allowfullscreen="true"></iframe>
</div>
```

在需要引用它的地方这么写

```markdown
{{</* bilibili "//player.bilibili.com/player.html?aid=1302993488&bvid=BV1DM4m1Q71a&cid=1499653065&p=1" */>}}
```

搞定收工！如果要引用别的视频网站，可以根据需求写相应的shortcode。
