---
title: 使用C语言实现一个线程安全的AC自动机
description: 
date: 2024-04-10T23:47:17+08:00
image: /images/covers/a-threadsafe-ac-automaton-with-c.png
math: 
license: 
hidden: false
comments: true
draft: false
tags:
  - c
  - 线程安全
  - 并发
  - 算法
---
## 背景

有一个很优秀的[C语言实现的AC自动机代码](https://multifast.sourceforge.net/)，但它不是线程安全的，为什么这么说呢，我们来看下代码。

```c
typedef struct ac_trie
{
	struct act_node *root; /**< The root node of the trie */

	size_t patterns_count; /**< Total patterns in the trie */

	short trie_open; /**< This flag indicates that if trie is finalized
					  * or not. After finalizing the trie you can not
					  * add pattern to trie anymore. */

	struct mpool *mp; /**< Memory pool */

	/* ******************* Thread specific part ******************** */

	/* It is possible to search a long input chunk by chunk. In order to
	 * connect these chunks and make a continuous view of the input, we need
	 * the following variables.
	 */
	struct act_node *last_node; /**< Last node we stopped at */
	size_t base_position;       /**< Represents the position of the current chunk,
								 * related to whole input text */

	AC_TEXT_t *text; /**< A helper variable to hold the input chunk */
	size_t position; /**< A helper variable to hold the relative current
					  * position in the given text */

	MF_REPLACEMENT_DATA_t repdata; /**< Replacement data structure */

	ACT_WORKING_MODE_t wm; /**< Working mode */

} AC_TRIE_t;
```

这是整个自动机的定义，其实作者也意识到了那几个变量是线程相关的，但他并没有选择实现线程安全，因为这个项目是为一个命令行程序服务的，而这个命令行程序显然是没有机会处理多线程场景的。

那为什么有这几个线程相关的变量就无法实现线程安全呢？再看下面的代码

```c
/**
 * @brief Search in the input text using the given trie.
 * 
 * @param thiz pointer to the trie
 * @param text input text to be searched
 * @param keep indicated that if the input text the successive chunk of the 
 * previous given text or not
 * @param callback when a match occurs this function will be called. The 
 * call-back function in turn after doing its job, will return an integer 
 * value, 0 means continue search, and non-0 value means stop search and return 
 * to the caller.
 * @param user this parameter will be send to the call-back function
 * 
 * @return
 * -1:  failed; trie is not finalized
 *  0:  success; input text was searched to the end
 *  1:  success; input text was searched partially. (callback broke the loop)
 *****************************************************************************/
int ac_trie_search (AC_TRIE_t *thiz, AC_TEXT_t *text, int keep, 
        AC_MATCH_CALBACK_f callback, void *user)
{
    size_t position;
    ACT_NODE_t *current;
    ACT_NODE_t *next;
    AC_MATCH_t match;

    if (thiz->trie_open)
        return -1;  /* Trie must be finalized first. */
    
    if (thiz->wm == AC_WORKING_MODE_FINDNEXT)
        position = thiz->position;
    else
        position = 0;
    
    current = thiz->last_node;
    
    if (!keep)
        ac_trie_reset (thiz);
    
    /* This is the main search loop.
     * It must be kept as lightweight as possible.
     */
    while (position < text->length)
    {
        if (!(next = node_find_next_bs (current, text->astring[position])))
        {
            if(current->failure_node /* We are not in the root node */)
                current = current->failure_node;
            else
                position++;
        }
        else
        {
            current = next;
            position++;
        }
        
        if (current->final && next)
        /* We check 'next' to find out if we have come here after a alphabet
         * transition or due to a fail transition. in second case we should not 
         * report match, because it has already been reported */
        {
            /* Found a match! */
            match.position = position + thiz->base_position;
            match.size = current->matched_size;
            match.patterns = current->matched;
            
            /* Do call-back */
            if (callback(&match, user))
            {
                if (thiz->wm == AC_WORKING_MODE_FINDNEXT) {
                    thiz->position = position;
                    thiz->last_node = current;
                }
                return 1;
            }
        }
    }
    
    /* Save status variables */
    thiz->last_node = current;
    thiz->base_position += position;
    
    return 0;
}

```

可以看到`thiz`就是正在使用的AC自动机的实例，但在查找过程中它改变了它的相关属性，这在多线程环境中肯定是会有冲突的，那么怎么解决呢？

## 方案

设想这样一个简单的场景，我们在处理链表相关的算法题时，最常做的事情是什么呢？对，是建立一个`dummyHead`，仔细想想为什么要这么做。

是的，根本目的是不希望我们遍历完成之后改变原来的链表，其实就是保持链表的不变性。

这里也是一样的道理，既然不能改变Trie里的这些属性，那么就把它提出来，最终让它们成为线程内部的变量，这样就做到了线程之间的隔离，每个线程只处理自己的查找，把Trie变成不可变的。

### 实现一个不可变的Trie

```c
/*
 * The A.C. Trie data structure
 */
typedef struct ac_trie
{
	struct act_node *root; /**< The root node of the trie */

	size_t patterns_count; /**< Total patterns in the trie */

	short trie_open; /**< This flag indicates that if trie is finalized
					  * or not. After finalizing the trie you can not
					  * add pattern to trie anymore. */

	struct mpool *mp; /**< Memory pool */

	MF_REPLACEMENT_DATA_t repdata; /**< Replacement data structure */

	ACT_WORKING_MODE_t wm; /**< Working mode */

} AC_TRIE_t;

```

`MF_REPLACEMENT_DATA_t repdata;` 这个很可疑，但它是用来实现替换功能的，我暂时没有这个需求，所以先不动它。

但整个搜索过程还是需要那些变量的，我们把它放在一个新定义的结构体中。

```c
typedef struct ac_search
{
	/* ******************* Thread specific part ******************** */

	/* It is possible to search a long input chunk by chunk. In order to
	 * connect these chunks and make a continuous view of the input, we need
	 * the following variables.
	 */
	struct act_node *last_node; /**< Last node we stopped at */
	size_t base_position;       /**< Represents the position of the current chunk,
								 * related to whole input text */

	AC_TEXT_t *text; /**< A helper variable to hold the input chunk */
	size_t position; /**< A helper variable to hold the relative current
					  * position in the given text */

} AC_SEARCH_t;
```


相应地，也需要改查找方法的实现

```c
int ac_trie_search(AC_TRIE_t *thiz, AC_SEARCH_t *search, int keep,
                   AC_MATCH_CALBACK_f callback, void *user)
{
    size_t position;
    ACT_NODE_t *current;
    ACT_NODE_t *next;
    AC_MATCH_t match;

    if (thiz->trie_open)
        return -1; /* Trie must be finalized first. */

    if (thiz->wm == AC_WORKING_MODE_FINDNEXT)
        position = search->position;
    else
        position = 0;

    current = search->last_node;

    if (!keep)
        ac_trie_reset(thiz);

    /* This is the main search loop.
     * It must be kept as lightweight as possible.
     */
    while (position < search->text->length)
    {
        if (!(next = node_find_next_bs(current, search->text->astring[position])))
        {
            if (current->failure_node /* We are not in the root node */)
                current = current->failure_node;
            else
                position++;
        }
        else
        {
            current = next;
            position++;
        }

        if (current->final && next)
        /* We check 'next' to find out if we have come here after a alphabet
         * transition or due to a fail transition. in second case we should not
         * report match, because it has already been reported */
        {
            /* Found a match! */
            match.position = position + search->base_position;
            match.size = current->matched_size;
            match.patterns = current->matched;

            /* Do call-back */
            if (callback(&match, user))
            {
                if (thiz->wm == AC_WORKING_MODE_FINDNEXT)
                {
                    search->position = position;
                    search->last_node = current;
                }
                return 1;
            }
        }
    }

    /* Save status variables */
    search->last_node = current;
    search->base_position += position;

    return 0;
}
```

把其中原先是`thiz`的地方改成`search`。
接下来就需要考虑怎么初始化`AC_SEARCH_t`。

```c
AC_SEARCH_t *ac_search_create(void)
{
    AC_SEARCH_t *search = (AC_SEARCH_t *)malloc(sizeof(AC_SEARCH_t));
    search->text = NULL;
    search->position = 0;
    search->last_node = NULL;
    search->base_position = 0;

    return search;
}
```

这是一个完全0值的初始化过程，事实上我们得先考虑把`text`初始化，因为要知道查的文本是什么。

```c
AC_SEARCH_t *search = ac_search_create();
AC_TEXT_t chunk;
chunk.astring = "experience the ease and simplicity of multifast";
chunk.length = strlen(chunk.astring);
search->text = &chunk;
```

这时执行会发现报段错误，具体错误就不展示了，原因是在`node_find_next_bs`方法中，有这样一段代码

```c
max = nod->outgoing_size - 1;
```

而`nod`是在`ac_trie_search`方法中的`current`，如果传入的`search->last_node`是空值，这里就直接一个空指针异常了。

检查Trie的初始化代码发现，每次开始查询之前都需要重置一下状态（其实就是我们这里处理的这些变量）

```c
/**
 * @brief reset the trie and make it ready for doing new search
 *
 * @param thiz pointer to the trie
 *****************************************************************************/
static void ac_trie_reset(AC_TRIE_t *thiz)
{
    thiz->last_node = thiz->root;
    thiz->base_position = 0;
    mf_repdata_reset(&thiz->repdata);
}
```

重点就在这里了，需要先把`search->last_node = trie->root`，这样才能开始。

### 最终效果

```c
AC_SEARCH_t *search = ac_search_create();
AC_TEXT_t chunk;
chunk.astring = chunks[i];
chunk.length = strlen(chunk.astring);
search->text = &chunk;
search->last_node = trie->root;
```
这就是一个完整的`AC_SEARCH_t`的初始化过程了。

### 多线程测试

这里只展示关键部分代码

首先定义一个结构体来向线程传递参数。
```c
typedef struct
{
    AC_TRIE_t *automata;
    AC_SEARCH_t *search;
} ThreadParams;
```


创建多个线程并等待执行结束
```c
pthread_t threads[3];

for (i = 0; i < 3; i++)
{
	ThreadParams *threadParams = (ThreadParams *)malloc(sizeof(ThreadParams));
	threadParams->automata = trie;
	AC_SEARCH_t *search = ac_search_create();
	AC_TEXT_t chunk;
	chunk.astring = chunks[i];
	chunk.length = strlen(chunk.astring);
	search->text = &chunk;
	search->last_node = trie->root;
	threadParams->search = search;
	pthread_create(&threads[i], NULL, chlid_handler, threadParams);
}

for (i = 0; i < 3; i++)
{
	pthread_join(threads[i], NULL);
}
```

定义线程内的回调方法，把传进来的参数解出来，调用查找方法
```c
void *chlid_handler(void *arg)
{
    ThreadParams *params = (ThreadParams *)arg;
    AC_MATCH_t match;
    printf("Searching: \"%s\" in thread: %ld\n", params->search->text->astring, (unsigned long int)pthread_self());

    ac_trie_search(params->automata, params->search, 0, match_handler, 0);
    return NULL;
}
```

大功告成。