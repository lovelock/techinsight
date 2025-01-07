---
title: "ForkJoinPool RecursiveAction/RecursiveTask实例解析"
description: 
date: 2024-08-16T16:37:37+08:00
image: 
math: 
license: 
hidden: false
comments: true
categories: ["java"]
tags: ["ForkJoinPool"]
---

我觉得直接从完整的源码来解释这个过程比干巴巴的文字描述可能更有说服力。两个的区别就和`Runnable`跟`Callable`的关系一毛一样，一个没有返回值，一个有返回值。
这例子就是完全从[Guide to the Fork/Join Framework in Java](https://www.baeldung.com/java-fork-join)借来的，在注释里加上了自己的一些尝试和理解。

## `RecursiveAction`没有返回值

```java
package fun.happyhacker;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ForkJoinTask;
import java.util.concurrent.RecursiveAction;
import java.util.logging.Level;
import java.util.logging.Logger;

public class CustomRecursiveAction extends RecursiveAction {
    private String workload = "";
    private static final int THRESHOLD = 4;

    private static final Logger logger = Logger.getAnonymousLogger();

    public CustomRecursiveAction(String workload) {
        this.workload = workload;
    }

    public static void main(String[] args) {
        CustomRecursiveAction task = new CustomRecursiveAction("Hello World");
        // task.compute();

        // 除了手动触发compute()方法，还可以使用ForkJoinPool.commonPool()方法来执行
        // ForkJoinPool.commonPool().execute(task);
        // task.join();

        // 可能最简单的方式就是直接invoke了
        // task.invoke();

        // 还有不太常用的方法，手动指定哪个fork哪个join
        // List<CustomRecursiveAction> subActions = task.createSubtasks();
        // subActions.get(0).fork();
        // subActions.get(1).join();

        // 最好的方式还是用ForkJoinTask.invokeAll来提交所有的task，而不是手动执行fork和join
    }

    @Override
    protected void compute() {
        if (workload.length() > THRESHOLD) {
            ForkJoinTask.invokeAll(createSubtasks());
        } else {
            processing(workload);
        }
    }

    /**
     * 这里使用创建两个子任务，然后放在一个列表里，等待invokeAll方法执行
     * 
     * @return
     */
    private List<CustomRecursiveAction> createSubtasks() {
        List<CustomRecursiveAction> subtasks = new ArrayList<>();

        String partOne = workload.substring(0, workload.length() / 2);
        String partTwo = workload.substring(workload.length() / 2, workload.length());

        subtasks.add(new CustomRecursiveAction(partOne));
        subtasks.add(new CustomRecursiveAction(partTwo));

        return subtasks;
    }

    private void processing(String work) {
        String result = work.toUpperCase();

        logger.log(Level.INFO, "This result - ({0}) was processed by {1} ( {2})",
                new Object[] { result, Thread.currentThread().getName(), Thread.currentThread().getId() });

    }

}
```

## `RecusiveTask` 有返回值


```java
package fun.happyhacker;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.ForkJoinTask;
import java.util.concurrent.RecursiveTask;
import java.util.logging.Level;
import java.util.logging.Logger;

public class CustomRecursiveTask extends RecursiveTask<Integer> {
    private final int[] arr;

    private static final int THRESHOLD = 20;
    private static final Logger logger = Logger.getAnonymousLogger();

    public static void main(String[] args) {
        int[] arr = new int[1000000];
        for (int i = 0; i < arr.length; i++) {
            arr[i] = (int) (Math.random() * 100);
        }
        CustomRecursiveTask customRecursiveTask = new CustomRecursiveTask(arr);
        Integer result = customRecursiveTask.compute();
        logger.log(Level.INFO, "sum of ints between 10 and 27 and multiply by 10 is: {0}", result);
    }

    public CustomRecursiveTask(int[] arr) {
        this.arr = arr;
    }

    @Override
    protected Integer compute() {
        if (arr.length > THRESHOLD) {
            return ForkJoinTask.invokeAll(createSubtasks())
                    .stream()
                    .mapToInt(ForkJoinTask::join)
                    .sum();
        } else {
            return processing(arr);
        }
    }

    private Collection<CustomRecursiveTask> createSubtasks() {
        List<CustomRecursiveTask> dividedTasks = new ArrayList<>();
        dividedTasks.add(new CustomRecursiveTask(Arrays.copyOfRange(arr, 0, arr.length / 2)));
        dividedTasks.add(new CustomRecursiveTask(Arrays.copyOfRange(arr, arr.length / 2, arr.length)));

        return dividedTasks;
    }

    private Integer processing(int[] arr) {
        return Arrays.stream(arr)
                .filter(a -> a > 10 && a < 27)
                .map(a -> a * 10)
                .sum();
    }

}
```
