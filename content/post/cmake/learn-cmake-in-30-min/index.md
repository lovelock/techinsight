---
title: "Learn Cmake in 30 Min"
date: 2023-01-06T22:17:27+08:00
tags: ["linux", "cmake", "c", "cxx"]
categories: ["in-action"]
image: cover.png
---

## 什么是 CMake？它能干什么？

CMake 是一个开源的跨平台自动化构建系统，它使用平台和编译器独立的配置文件来生成标准的构建文件，这使得开发者可以使用统一的方法来管理项目的构建过程。CMake的配置文件通常命名为 `CMakeLists.txt`，在这个文件中，开发者可以定义项目的源码文件、依赖关系、目标（如可执行文件和库）、编译选项以及其他构建参数。

<!--more-->

CMake的主要优势在于它的跨平台能力：它可以生成适用于多种平台和IDE的构建配置，包括Unix的Makefiles、Microsoft Visual Studio的解决方案文件、Apple的Xcode项目等。这样，使用CMake的项目可以轻松地在不同的开发环境中编译和运行，无需修改构建配置。

简单来说，CMake让复杂的构建过程变得简单化，提供一种高效、可扩展的方式来自动化构建过程，支持大型项目和多平台编译。

## 一个最简单的 CMake 项目

### 只包含必要元素的 `CMakeLists.txt`

一个最简单的`CMakeLists.txt`文件通常包含以下几个基本元素：

1. **cmake_minimum_required**: 指定运行此项目所需的最低版本的CMake。
2. **project**: 定义了项目的名称和可选的版本号。
3. **add_executable** 或 **add_library**: 添加一个可执行文件或者库到项目中，并指定它的源文件。

下面是一个最简单的示例：

```c
cmake_minimum_required(VERSION 3.0)  # 设置CMake的最低版本要求
project(HelloWorld)                   # 定义项目名称

add_executable(HelloWorld main.c)     # 添加一个可执行文件 "HelloWorld"，源文件是 "main.c"
```

这个 `CMakeLists.txt` 文件定义了一个简单的项目，其中包含一个可执行文件 `HelloWorld`，它是由单个源文件 `main.c` 编译而成的。当你运行CMake时，它会根据这个配置文件生成适合你系统的构建文件（比如Unix的Makefile或者Visual Studio的项目文件）。然后你可以使用相应的构建系统来编译和链接你的程序。

### 最简单的 HelloWorld

```c
#include <stdio.h>

int main() {
  printf("hello world!\n");
  return 0;
}
```

### 构建这个项目

#### 创建 build 目录

在 `CMakeLists.txt` 所在的目录下，创建一个 `build` 目录。

```bash
mkdir build && cd build
```

#### 生成对应当前系统的构建文件

```bash
cmake ..
```

{{<callout "info" "为什么要费这劲呢？">}}
{{</callout>}}
你可能已经看到了，我们先创建了 `build` 目录，然后在它里面执行的是 `cmake ..`，也就是说 `cmake` 需要的文件在 `build` 的上层目录，那是不是直接在它的上层目录执行 `cmake .` 也是可以的呢？
是的，但是这样做其实是个最佳实践，好处在于在必要时可以直接删除 `build` 目录，而不会对项目产生影响，否则 CMake 生成的文件散落在你的代码中，一定不是你想看到的结果。

这个命令通常在一个空的构建目录（通常是项目根目录的子目录，如 `build`）中执行。这是一种被推荐的外部构建方法，可以避免在源代码目录中生成构建文件。`.` 表示当前目录，而 `..` 表示当前目录的父目录，通常这个父目录包含顶层的 `CMakeLists.txt` 文件。

执行 `cmake ..` 会：

- 检查系统环境。
- 根据顶层 `CMakeLists.txt` 文件来确定如何编译项目的源代码。
- 生成对应于当前系统的构建文件（如Makefiles或者Visual Studio解决方案等）。

{{<callout "info" "CMake 怎么知道要生成什么平台的文件呢？">}}
{{</callout>}}

CMake 确定使用哪种具体构建工具（如 Make 或 Visual Studio）的过程是在初次配置构建系统时发生的，也就是在你运行 `cmake` 命令来生成构建文件时。这个决定基于两个主要因素：

1. **可用的构建工具**：CMake 会检测你的系统上安装了哪些构建工具。例如，如果你在 Windows 上且安装了 Visual Studio，CMake 默认会生成 Visual Studio 解决方案文件。如果你在 Linux 或 macOS 上，通常默认生成 Makefile。
2. **用户指定的生成器**：用户可以通过 `-G` 选项显式指定使用哪个生成器，也就是构建系统类型。例如，即使在 Windows 上，你也可以通过 `-G "Unix Makefiles"` 选项告诉 CMake 生成 Makefile，使用 Make 工具进行构建，而不是使用 Visual Studio。类似地，如果你想要使用其他类型的构建系统，如 Ninja，你也可以通过 `-G "Ninja"` 来指定。

当运行 `cmake` 命令没有指定 `-G` 选项时，CMake 会根据它检测到的环境和默认优先顺序选择一个生成器。一旦构建文件被生成，运行 `cmake --build .` 命令时，CMake 会使用相应的构建工具来编译项目，而不需要用户关心具体是使用 Make、Visual Studio 还是其他工具。这种抽象化的好处是，你可以用相同的命令在不同的平台和环境下构建你的项目。
#### 生成最终的可执行文件或库文件

```bash
cmake --build .
```

这个命令是用来实际编译和链接程序的。在你已经生成了构建系统文件后（例如，使用 `cmake ..`），可以使用此命令来启动构建过程。

执行 `cmake --build .` 会：

- 根据当前目录中的构建系统文件（Makefile、Visual Studio解决方案文件等）来编译源代码。
- 生成最终的可执行文件或库文件。

`.` 在这里也表示当前目录，它应该是包含了构建系统文件的目录。这条命令的优点是它抽象了具体的构建工具（make、ninja、msbuild等），使得构建过程与构建系统无关。

执行完这一步，就生成了最终的可执行文件（或库文件，如果你写的是一个库的话）。在这个例子里可执行文件的文件名是 `HelloWorld`，因为 `CMakeLists.txt` 文件的第二行 `project(HelloWorld)` 里已经定义了。

如果只是这么简单，就没必要使用 CMake 了，直接 `gcc` 都能满足了，所以下面我们来看如何用 CMake 来管理依赖。

## 管理一个库项目

有时候我们需要写的项目是一个让其他项目依赖的库，就不能像上面生成一个可执行文件，而是生成一个 `.a` 或 `.so` 文件，下面是一个最简单的例子。完成这个例子之后我们会对两种情况做一个简单的对比。

### 只包含必要元素的 `CMakeLists.txt`

```
cmake_minimum_required(VERSION 3.27)
project(my_math)

# 创建一个明为my_math的静态库
add_library(my_math include/my_math/my_math.h src/my_math.c)

# 指定库的头文件搜索路径
target_include_directories(my_math PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
```

> [!QUESTION] 什么是静态库？是不是还有动态库？
> 在CMake中，当你使用 `add_library` 命令创建一个库时，`SHARED` 和 `STATIC` 关键字用来指定库是动态链接的还是静态链接的：
>
> `STATIC`：创建一个静态库。静态库通常是一个包含多个对象文件的单一归档文件（在Windows上通常是 `.lib` 文件，在Unix-like系统上是 `.a` 文件）。当静态库被链接到一个可执行文件时，库中的代码会被复制到最终的可执行文件中。静态链接发生在编译时，一旦完成，可执行文件不再需要静态库文件。静态库的优点是最终的可执行文件是自包含的，不依赖外部的动态库。缺点是如果多个程序都使用同一个静态库，它们各自都会包含一份库代码的副本，这会导致冗余和更大的程序体积。
>
> `SHARED`：创建一个动态链接库（在Windows上是 `.dll` 文件，在Unix-like系统上是 `.so` 文件）。当动态库被链接到一个可执行文件时，并不是将代码复制到可执行文件中，而是在程序运行时由操作系统动态地加载和链接。这意味着程序在运行时需要能够找到这个动态库文件。动态库的优点是多个程序可以共享同一份库代码，节省空间，并可以在不重新编译程序的情况下更新库代码（只要接口没有改变）。缺点是可能会遇到库版本不匹配或找不到库文件的运行时错误。
>
> 在实际应用中，这两种类型的库各有用处：
>
> - 如果你希望你的程序易于部署，不想处理动态库可能带来的复杂性，你可能会选择静态链接。这样你的程序可以在没有额外依赖的情况下运行。
> - 如果你希望你的应用程序能够共享公共代码并且轻量级，或者希望能够独立于应用程序更新你的库，那么你可能会选择动态链接。
>
> 在 CMake 中，你可以根据需要选择使用 `STATIC` 或 `SHARED` 关键字来构建你的库，或者使用 `add_library` 命令不带任何关键字来创建类型取决于构建类型的库（默认情况下可能是静态的，但可以通过 CMake 变量来控制）。

#### 一个简单的库的实现

`include/my_math/my_math.h`

```c
#ifndef MY_MATH_HEADER
#define MY_MATH_HEADER

int max(int, int);

#endif // !MY_MATH_HEADER

```

{{<callout "info" "为什么要有 `#ifndef`、`#define`、`#endif` 这些？">}}
{{</callout>}}
简单讲就是为了避免重复引用。
先判断 `#ifndef` 也就是如果没有定义过这个 HEADER，那反过来讲如果定义过这个 HEADER 呢？是不是就执行后面所有的语句了？
然后如果进入了，说明就是还没有引入过这个文件，就定义这个常量，这也帮助了第一步的判断
最后是 `#endif`，说明整个 `#ifndef` 结束了

```c
#include "my_math/my_math.h"

int max(int a, int b) {
  if (a > b) {
    return a;
  }

  return b;
}
```

这是整个项目的所有文件，读者可以对照一下

```
├── CMakeLists.txt
├── include
│   └── my_math
│       └── my_math.h
└── src
    └── my_math.c

4 directories, 3 files
```

#### 构建这个项目

```
mkdir build && cd build && cmake .. && cmake --build .
```

执行上述命令之后会生成很多文件，但目前我们需要关注的只有 `libmy_math.a`，这就是其他项目需要依赖的**库**了。

## 管理依赖

下面看如何让 HelloWorld 项目依赖 my_math 项目。

首先要明确的是，CMake 并不能像 Maven/Cargo 那样直接从互联网下载你需要的包，而是需要你自己下载了包之后放在项目依赖的目录下，然后编辑 `CMakeLists.txt`，让你的项目能够识别到这个依赖。这更像早期使用 Ant 编译 Java 的时代吧。

### 最简单的依赖

HelloWorld 的结构暂时不变，但需要创建一个 include 目录来存放依赖，先把 lib-demo 的所有代码放在 HelloWorld 的 include 目录下。

```c
cmake_minimum_required(VERSION 3.27)
project(HelloWorld)

add_executable(HelloWorld src/main.c)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/include/my_math)

target_link_libraries(HelloWorld my_math)
target_include_directories(HelloWorld PRIVATE include/my_math/include)
```

{{<callout "info" "`target_include_directories` 的第二个参数 `PRIVATE` 是什么意思？">}}
{{</callout>}}
这个命令为目标（可执行文件或库）指定包含目录，第二个参数可选值有 3 个：`PUBLIC`、`PRIVATE` 和 `INTERFACE`，这决定了包含目录的范围和传播行为：

`PRIVATE`：指定的包含目录仅用于这个目标的构建，并且不会传递给依赖这个目标的其他目标。如果你有一个目标（如一个库或可执行文件），而这个目标的头文件仅在源文件中内部使用，没有在任何对外的头文件中使用，则应该将这些内部使用的头文件目录标记为 `PRIVATE`。

`PUBLIC`：指定的包含目录既用于这个目标的构建，也会传递给依赖这个目标的其他目标。使用 `PUBLIC` 意味着连接到这个库的任何目标也将自动添加这些包含目录到它们的包含目录列表中。如果你的库的公共头文件需要某些路径才能被找到，那么这些路径应该被标记为 `PUBLIC`。

`INTERFACE`：指定的包含目录不用于这个目标的构建，但会传递给依赖这个目标的其他目标。这通常用在只包含头文件的接口库上，这种情况下构建目标本身并不需要这些包含目录，但是使用该目标的其他目标需要。

简而言之，`PRIVATE` 意味着仅用于构建当前目标，`PUBLIC` 意味着既用于构建当前目标也用于依赖它的目标，而 `INTERFACE` 意味着仅用于依赖当前目标的其他目标。

```c
#include "my_math/my_math.h"
#include <stdio.h>

int main() {
  int a = 10, b = 5;
  int c = max(a, b);
  if (c != 10) {
    printf("max is not correct\n");
  } else {
    printf("c is %d, and max is included\n", c);
  }

  printf("hello world!\n");
  return 0;
}
```

接下来怎么让这个代码运行起来，这里就不再赘述了。

### 嵌套的依赖

前面其实已经完整讲述了一个项目和它的依赖应该如何组织了，其实更深层的依赖管理和上面描述的也没有什么区别，比如上面的 `my_math` 库又依赖了别的库比如 `his_math`，这时你有两个选择：

1. 如果 `HelloWorld` 也使用到了 `his_math`，那你应该把它放在 `HelloWorld` 项目的 `include` 里，这样两个项目都可以使用它。
2. 如果只有 `my_math` 用它，那就可以把它放在 `my_math` 的 `include` 里，具体的做法和上面的并无其他不同。

## 单元测试

没错，CMake 还能做单元测试。

在 my_math 项目里添加一个 `tests` 目录，把 `CMakeLists.txt` 改一下，判断是否存在 `tests` 目录，如下

```c
cmake_minimum_required(VERSION 3.27)
project(my_math)

# 设置C标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED True)

# 创建一个明为my_math的静态库
add_library(${PROJECT_NAME} include/my_math/my_math.h src/my_math.c)
add_subdirectory(third_party/his_math)
target_link_libraries(${PROJECT_NAME} his_math)

if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/tests/CMakeLists.txt)
  enable_testing()
  add_subdirectory(tests)
  include(CTest)
endif()

# 指定库的头文件搜索路径
target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
```

这里我把检测到 `tests/CMakeLists.txt` 之后的操作全部写在一个 `if` 里了。

然后 `tests` 目录本身也需要一个 `CMakeLists.txt`，如下

```c
cmake_minimum_required(VERSION 3.27)
project(my_math_tests)

# 设置C标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED True)

enable_testing()

add_executable(${PROJECT_NAME} test_my_math.c)
# 指定库的头文件搜索路径
target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_SOURCE_DIR}/include)

target_link_libraries(${PROJECT_NAME} his_math my_math)

add_test(NAME my_math_tests COMMAND ${PROJECT_NAME})
```

这里要注意的点还是挺多的，比如前面写的都是 `${CMAKE_CURRENT_SOURCE_DIR}/include`，这里却是 `${CMAKE_SOURCE_DIR}/include`。

其实这个单元测试就是一个的 executable，加了一个通过 `ctest` 命令启动的入口。

然后写一个 `test_my_math.c`，如下

```c
#include "my_math/my_math.h"
#include <stdio.h>

void test_max() {
  int result = max(1, 2);
  if (result == 2) {
    printf("test_max passed.\n");
  } else {
    printf("test_max failed. Expected 2 but got %d.\n", result);
  }
}

int main() {
  test_max();
  // 这里可以添加更多的测试
  return 0; // 如果有测试失败，你可能想要返回非零值
}
```

这时候去 `my_math` 的 `build` 目录里执行 ` cmake .. && cmake --build . && ctest` ，就会发现单元测试已经可以执行了。

```
❯ ctest
Test project /Users/frost/workspace/private/cmake-tutorial/simple-demo/third_party/my_math/build
    Start 1: my_math_tests
1/1 Test #1: my_math_tests ....................   Passed    0.39 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   0.39 sec
```
