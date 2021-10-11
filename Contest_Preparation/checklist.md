1. 是否使用了 DOMjudge 自带的 Config checker 检查配置？
2. 如果比赛不允许选手自行注册，是否禁止了注册？
3. 如果比赛不希望公开，是否将比赛设为了非 public？
4. 是否根据评测结点的速度相应调整时间限制？题面是否相应修改？
5. `C/C++` 标准是否检查过？DOMjudge 的默认行为是使用评测结点 `gcc/g++` 的默认标准。如需修改，可在 DOMjudge 的 Executable 中修改。理论上，若不同评测结点的 `gcc/g++` 版本差异过大，有可能导致它们使用不同的默认标准。 
6. 是否测试了评测结点时间的抖动？是否禁用了地址空间配置随机加载？参考[这里](https://www.domjudge.org/docs/manual/7.3/judging.html#judging-consistency)。
7. 是否在 DOMjudge 的 Judging verifier 中检查过 polygon 上的 verdict 与 DOMjudge 的 verdict 不一致的情况？