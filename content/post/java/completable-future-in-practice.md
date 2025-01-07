---
title: "CompletableFuture实例讲解"
description: 
date: 2024-08-16T16:22:17+08:00
image: 
math: 
license: 
hidden: false
comments: true
categories: ["java"]
tags: ["future", "ForkJoinPool"]
---

这是为搞定Flink AsyncIO做的准备工作，要搞清楚CompletableFuture。基本都是[Guide To CompletableFuture](https://www.baeldung.com/java-completablefuture)这篇文章中的例子，在此基础上扩展了一些，最主要的就是在`Async`结尾的方法指定自定义线程池时，用默认的例子直接改成`Async`发现使用的仍然是`ForkJoinPool.commonPool`，但看前面人家的解释，说的是当并行度大于1时，所以就给这个例子加了一些并行度，也就是让这个Future内的任务本身又有一些并行，这时就符合文章的描述了。

```java
package fun.happyhacker;

import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ThreadFactory;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class CompletableFutureDemo {
    public static void main(String[] args) {
        System.out.println("Hello world!");
    }

    /**
     * .complete()直接接收一个字面量，使用场景应该比较有限
     * 
     * @return
     * @throws InterruptedException
     */
    public Future<String> simpleComplete() throws InterruptedException {
        CompletableFuture<String> completableFuture = new CompletableFuture<>();

        Executors.newCachedThreadPool().submit(() -> {
            Thread.sleep(500);
            completableFuture.complete("Hello");
            return null;
        });

        return completableFuture;
    }

    /**
     * .supplyAsync() 接收一个 Supplier 函数，应用场景就可以比较广泛了
     * 
     * @return
     * @throws InterruptedException
     */
    public Future<String> supplyAsync() throws InterruptedException {
        return CompletableFuture.supplyAsync(() -> "Hello");
    }

    /**
     * 把两个Future组装成一个Future，这才是使用Future的普通场景，但实际情况可能会更复杂
     * 
     * @return
     */
    public Future<String> thenApply() {
        CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> "Hello");
        CompletableFuture<String> future = completableFuture.thenApply(s -> s + " World");

        return future;
    }

    /**
     * 把两个Future组装成一个Future，但最后不需要返回结果，而是直接在回调中使用结果了
     * 
     * @return
     */
    public Future<Void> thenAccept() {
        CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> "Hello");
        CompletableFuture<Void> future = completableFuture
                .thenAccept(s -> System.out.println("Computation returned: " + s));

        return future;
    }

    /**
     * 比thenAccept更进一步，不光最后不需要返回结果，甚至在thenRun这一步也不需要知道结果，只是知道结果计算完成了就可以了，具体结果是什么，不关心
     * 
     * @return
     */
    public Future<Void> thenRun() {
        CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> "Hello");
        CompletableFuture<Void> future = completableFuture.thenRun(() -> System.out.println("Computation finished"));

        return future;
    }

    /**
     * thenCompose中传入的又是一个新的Future，也就是把第一个future的结果传递给下一个future，这样就可以串起来多个future了
     * 
     * @return
     */
    public Future<String> thenCompose() {
        CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> "Hello")
                .thenCompose(s -> CompletableFuture.supplyAsync(() -> s + " Future"))
                .thenCompose(s -> CompletableFuture.supplyAsync(() -> s + " World"));

        return completableFuture;
    }

    private CompletableFuture<String> composeHelper(String s) {
        return CompletableFuture.supplyAsync(() -> s + " World");
    }

    public Future<String> thenCompose2() {
        CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> "Hello")
                .thenCompose(this::composeHelper);

        return completableFuture;
    }

    /**
     * 也是联合两个Future，但是它的回调函数是把前后两个Future的结果同时作为参数
     * 
     * @return
     */
    public Future<String> thenCombine() {
        CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> "Hello")
                .thenCombine(CompletableFuture.supplyAsync(() -> " Future"), (s1, s2) -> s1 + s2)
                .thenCombine(CompletableFuture.supplyAsync(() -> " World"), (s1, s2) -> s1 + s2);

        return completableFuture;
    }

    /**
     * 可以直接连接多个Future，但最大的问题是无法返回结果
     * 
     * @return
     */
    public Future<Void> allOf() {
        CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> "Hello");
        CompletableFuture<String> future2 = CompletableFuture.supplyAsync(() -> "Beautiful");
        CompletableFuture<String> future3 = CompletableFuture.supplyAsync(() -> "World");

        return CompletableFuture.allOf(future1, future2, future3);
    }

    /**
     * 这等于是用CompletableFuture::join方法把所有的Future都join起来，然后再把结果拼接起来
     * join方法没有参数，它的作用就是等待所有的Future执行完成
     * 
     * @return
     */
    public String join() {
        CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> "Hello");
        CompletableFuture<String> future2 = CompletableFuture.supplyAsync(() -> "Beautiful");
        CompletableFuture<String> future3 = CompletableFuture.supplyAsync(() -> "World");

        String combined = Stream.of(future1, future2, future3)
                .map(CompletableFuture::join)
                .collect(Collectors.joining(" "));

        return combined;
    }

    /**
     * 每个Future都有一个handle方法，它的作用是把Future的结果或者异常转换成另外一个Future
     * handle的第一个参数是前面Future的结果，第二个参数是前面Future的异常
     * 
     * @param name
     * @return
     */
    public Future<String> handleError(String name) {
        CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
            if (name == null) {
                throw new RuntimeException("Computation Error");
            }

            return "Hello " + name;
        }).handle((s, t) -> s != null ? s : "Hello Stranger");

        return future;
    }

    public Future<String> handleError2(String name) {
        CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
            if (name == null) {
                throw new RuntimeException("Computation Error");
            }

            return "Hello " + name;
        }).handle((s, t) -> t != null ? "抛异常了 " + t.getMessage() + " Hello Stranger" : s);

        return future;
    }

    public Future<String> handleError3(String name) {
        CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
            if (name == null) {
                throw new RuntimeException("Computation Error");
            }

            return "Hello " + name;
        });
        future.completeExceptionally(new RuntimeException("Computation Error Outer"));

        return future;
    }

    /**
     * 带Async后缀的then方法默认在ForkJoinPool.commonPool()中执行，而不是与前面的Future在同一个线程中执行
     * 这可以更好地利用CPU资源，避免由于前面的线程阻塞而导致的资源浪费
     * 
     * @return
     */
    public Future<String> composeAsync() {
        CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> {
            System.out.println("First Task: " + Thread.currentThread().getName());
            return "Hello";
        })
                .thenComposeAsync(s -> CompletableFuture.supplyAsync(() -> {
                    System.out.println("Second Task: " + Thread.currentThread().getName());
                    return s + " Future";
                }))
                .thenComposeAsync(s -> CompletableFuture.supplyAsync(() -> {
                    System.out.println("Third Task: " + Thread.currentThread().getName());
                    return s + " World";
                }));

        return completableFuture;
    }

    /**
     * 相应的，不带Async后缀的就是在同一个线程内执行的
     * 
     * @return
     */
    public Future<String> composeAsync2() {
        CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> {
            System.out.println("First Task: " + Thread.currentThread().getName());
            return "Hello";
        })
                .thenCompose(s -> CompletableFuture.supplyAsync(() -> {
                    System.out.println("Second Task: " + Thread.currentThread().getName());
                    return s + " Future";
                }))
                .thenCompose(s -> CompletableFuture.supplyAsync(() -> {
                    System.out.println("Third Task: " + Thread.currentThread().getName());
                    return s + " World";
                }));

        return completableFuture;
    }

    /**
     * 带Async后缀的then方法会默认在ForkJoinPool.commonPool()中执行，而不是与前面的Future在同一个线程中执行
     * 也可以指定自己的线程池来执行，但一定要注意，如果任务太过简单，也就是thenComposeAsync中的逻辑太简单，它并不会按预期的在自定义的线程池中执行，而要让并行度达到某个水平才可以
     * 
     * @return
     */
    public Future<String> composeAsync3() {
        ExecutorService service1 = Executors.newFixedThreadPool(3, threadFactory("MyFirstPool", true));
        ExecutorService service2 = Executors.newFixedThreadPool(3, threadFactory("MySecondPool", true));
        ExecutorService service3 = Executors.newFixedThreadPool(3, threadFactory("MyThirdPool", true));
        CompletableFuture<String> completableFuture = CompletableFuture.supplyAsync(() -> {
            System.out.println("First Task: " + Thread.currentThread().getName());
            try {
                Thread.sleep(500);
            } catch (InterruptedException ex) {
            }
            return "Hello";
        }, service1)
                .thenComposeAsync(s -> {
                    List<CompletableFuture<String>> futures = IntStream.range(0, 10)
                            .mapToObj(i -> CompletableFuture.supplyAsync(() -> {
                                simulateWork(500);
                                System.out.println("Second Task " + i + ": " + Thread.currentThread().getName());
                                return s + " Future" + i;
                            }, service2))
                            .collect(Collectors.toList());
                    return CompletableFuture.allOf(futures.toArray(CompletableFuture[]::new))
                            .thenApply(v -> futures.stream()
                                    .map(CompletableFuture::join)
                                    .collect(Collectors.joining(", ")));
                }, service2)
                .thenComposeAsync(s -> {
                    List<CompletableFuture<String>> futures = IntStream.range(0, 10)
                            .mapToObj(i -> CompletableFuture.supplyAsync(() -> {
                                simulateWork(500);
                                System.out.println("Thrird Task " + i + ": " + Thread.currentThread().getName());
                                return s + " Future" + i;
                            }, service3))
                            .collect(Collectors.toList());
                    return CompletableFuture.allOf(futures.toArray(CompletableFuture[]::new))
                            .thenApply(v -> futures.stream()
                                    .map(CompletableFuture::join)
                                    .collect(Collectors.joining(", ")));
                }, service3);

        // service1.shutdown();
        // service2.shutdown();
        // service3.shutdown();
        return completableFuture;
    }

    private static void simulateWork(int milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public static ThreadFactory threadFactory(String name, boolean daemon) {
        return runnable -> {
            Thread result = new Thread(runnable, name);
            result.setDaemon(daemon);
            return result;
        };
    }

}
```

```java
package fun.happyhacker;

import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;

import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;

public class CompletableFutureDemoTest {
    @Test
    void testSimpleComplete() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().simpleComplete();
        assertEquals("Hello", future.get());
    }

    @Test
    void testSupplyAsync() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().supplyAsync();
        assertEquals("Hello", future.get());
    }

    @Test
    void testThenApply() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().thenApply();
        assertEquals("Hello World", future.get());
    }

    @Test
    void testThenAccept() throws InterruptedException, ExecutionException {
        Future<Void> future = new CompletableFutureDemo().thenAccept();
        assertEquals(null, future.get());
    }

    @Test
    void testThenRun() throws InterruptedException, ExecutionException {
        Future<Void> future = new CompletableFutureDemo().thenRun();
        assertEquals(null, future.get());
    }

    @Test
    void testThenCompose() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().thenCompose();
        assertEquals("Hello Future World", future.get());
    }

    @Test
    void testThenCompose2() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().thenCompose2();
        assertEquals("Hello World", future.get());
    }

    @Test
    void testThenCombine() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().thenCombine();
        assertEquals("Hello Future World", future.get());
    }

    @Test
    void testAllOf() throws InterruptedException, ExecutionException {
        Future<Void> future = new CompletableFutureDemo().allOf();
        future.get();
    }

    @Test
    void testJoin() throws InterruptedException, ExecutionException {
        String str = new CompletableFutureDemo().join();
        assertEquals("Hello Beautiful World", str);
    }

    @Test
    void testHandleError() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().handleError("World");
        assertEquals("Hello World", future.get());

        Future<String> future2 = new CompletableFutureDemo().handleError(null);
        assertEquals("Hello Stranger", future2.get());

        Future<String> future3 = new CompletableFutureDemo().handleError2(null);
        assertEquals("抛异常了 java.lang.RuntimeException: Computation Error Hello Stranger", future3.get());

        // Future<String> future4 = new CompletableFutureDemo().handleError3(null);
        // try {
        // future4.get();
        // } catch (InterruptedException | ExecutionException e) {
        // assertEquals("java.lang.RuntimeException: Computation Error",
        // e.getMessage());
        // }
    }

    @Test
    void testThenComposeAsync() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().composeAsync();
        assertEquals("Hello Future World", future.get());
    }

    @Test
    void testThenComposeAsync2() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().composeAsync2();
        assertEquals("Hello Future World", future.get());
    }

    @Test
    void testThenComposeAsync3() throws InterruptedException, ExecutionException {
        Future<String> future = new CompletableFutureDemo().composeAsync3();
        future.get();
    }
}
```
