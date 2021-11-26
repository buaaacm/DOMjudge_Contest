## 传题前
1. 是否为数据库设置了强密码？
2. 是否使用了 DOMjudge 自带的 Config checker 检查配置？
3. `C/C++` 标准是否检查过？DOMjudge 的默认行为是使用评测结点 `gcc/g++` 的默认标准。如需修改，可在 DOMjudge 的 Executable 中修改。理论上，若不同评测结点的 `gcc/g++` 版本差异过大，有可能导致它们使用不同的默认标准。 
4. 是否开启了 Py3 提交？是否使用了 `pypy3`？
5. 若比赛有交互题，是否设置了足够长的 timelimit_overshoot？交互题的 wall time 很长，不设置会导致 TLE。当然，这会显著增加评测负担，因为无法对某个题单独设置该属性。如果不需要卡 CPU time（即实际的 TL），那么可以考虑将时限开得很长，将 timelimit_overshoot 配置成若干倍时限。总而言之，这需要根据实际情况加以考虑。一般可以考虑设 `3s|100%`。

## 传题后
1. 如果比赛不允许选手自行注册，是否禁止了注册？
2. 如果比赛不希望公开，是否将比赛设为了非 public？
3. 是否根据评测结点的速度相应调整时间限制？题面是否相应修改？
4. 是否测试了评测结点时间的抖动？是否禁用了地址空间配置随机加载？参考[这里](https://www.domjudge.org/docs/manual/7.3/judging.html#judging-consistency)。
5. 是否在 DOMjudge 的 Judging verifier 中检查过 polygon 上的 verdict 与 DOMjudge 的 verdict 不一致的情况？
6. 比较 DOMjudge 上测试点数量和 Polygon 上测试点数量（以防测试点导入出现问题）。
7. 默认 OL 是 `8MB`，对于超大输出的题目，需要计算选手可能的最大输出，增加 OL。
8. 各种空白符是否有问题？例如 `\r`（目前脚本自动删除），行末空格，文件结尾换行等？