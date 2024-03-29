# Polygon Files

这里保存了 Polygon 中的相关文件，并按我们的需求进行了适应性修改。下面记录了主要的修改内容。

## testlib.h

1. 将返回值修改为 $42,43$，对应 DOMjudge 的接口
2. 修改 `registerTestlibCmd` 函数中命令行参数的顺序，对应 DOMjudge 的接口
3. 修改 `registerInteraction` 函数中命令行参数的顺序，对应 DOMjudge 的接口
4. Polygon 上的 `tout` 用于输出给 `checker` 检查的信息，但是 `DOMjudge` 不能同时支持 `interactor` 和 `checker`。因此在 `DOMjudge` 上将 `tout` 改为向 `judgemessage.txt` 输出信息。

## olymp.sty

1. 增加中文语言选项，并对部分语句本地化
2. 使用 `lastpage` 包，而非将其代码放在 `olymp.sty` 中，以使得 `lastpage` 与 `hyperref` 兼容
3. 增加不可见的 `section` 命令，使得 `subsection` 等能够正确显示
4. 添加中文首行缩进支持

## statements.ftl

1. 使用中文支持的 `olymp.sty`
2. 增加了一些算法竞赛中可能使用的包
3. 全局定义 `\lstset` 的格式

`statements.min.ftl` 则仅在原版的基础上添加了中文。

## tutorials.ftl

1. 使用中文支持的 `olymp.sty`
2. 增加了一些算法竞赛中可能使用的包
3. 全局定义 `\lstset` 的格式

`tutorials.min.ftl` 则仅在原版的基础上添加了中文。
