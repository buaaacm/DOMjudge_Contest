# DOMjudge Contest

在搭建好的 DOMjudge 上举办一场新的比赛！

## Polygon2DOMjudge

将 Polygon 上下载的 package 转换为 DOMjudge 需要的形式。

### Requirements

`Linux` 系统（或低版本的 `OS X`），`wine`，`texlive-full`。

`Windows` 系统可类似操作。

### 从 Polygon 下载题目文件并 build

1. 在 Polygon 上以 Build full packages (+verify) 的形式 build package，随后下载 package。
2. `unzip contest-*****.zip -d contest-*****`
3. `cd contest-*****`
4. ```sh
    vim ./statements/chinese/doall.sh
    :%s/latex/xelatex/g
    vim ./statements/chinese/statements.tex
    # in line 3, insert
    \usepackage[UTF8]{ctex}
    ```
5. `find ./ -name '*.sh' -exec chmod +x {} \;`
6. `./doall.sh`

本地 build 出的题面 pdf 很可能不尽如人意，有的地方有一些小 bug，甚至可能 build 失败。这里只需要在 `statements/chinese/` 目录下重新 `./doall.sh` 即可单独 build 题面。

接下来需要在 Polygon 上运行脚本以打包成 DOMjudge 格式的题目包。

1. 将 `polygon2domjudge.py`、`testlib.h` 移动到 `contest-*****` 目录
1. （可选）准备好气球颜色 `balloon.yaml`：
   ```
   problem-name1: '#FF7109'
   problem-name2: '#008100'
   ```
   若不准备好该文件，会随机生成气球颜色
2. 运行 `python3 polygon2domjudge.py` 即可：
   ```
   usage: polygon2domjudge.py [-h] [--origin-ml] [--balloon BALLOON] [--language LANGUAGE]

   Parse Polygon package to DOMjudge format.
   
   optional arguments:
     -h, --help           show this help message and exit
     --origin-ml          If set, use the original memory limit of Polygon. Otherwise, set memory limit to 2GB.
     --balloon BALLOON    Balloon color config path. Default: Generate random colors
     --language LANGUAGE  Language used in statements Default: chinese
   ```

## Setup Contest

在 DOMjudge 上新建比赛！

步骤如下：

1. 将 `create_contest.py` 移动到 `contest-*****` 目录
2. 在 `contest-*****/contest.yaml` 中填写比赛信息，例如：
   ```
   name:                     DOMjudge open practice session
   short-name:               practice
   start-time:               '2020-04-30T10:00:00+01:00'
   duration:                 '2:00:00'
   scoreboard-freeze-length: '0:30:00'
   penalty-time:             20
   ```
3. 在 `create_contest.py` 文件中修改 admin 用户名和密码
4. 给 `admin` 创建一个 team，否则添加 submission 时会报 `No jury solutions added: must associate team with your user first.` 错误 
5. 运行 `python3 create_contest.py`：
   ```
   usage: create_contest.py [-h] [--contest CONTEST] url
   
   Add a contest to DOMjudge.
   
   positional arguments:
     url                DOMjudge url. Example: https://bcpc.buaaacm.com/domjudge
   
   optional arguments:
     -h, --help         show this help message and exit
     --contest CONTEST  Contest config path. Default: contest.yaml
   ```

## Generate teams and users

1. 填写 `groups.tsv`，即队伍类别，注意该文件不能有空行，下同（这 DOMjudge 实现的真辣鸡）
2. 运行 `python3 gen_teams.py`：
   ```
   usage: gen_teams.py [-h] [--pwd-len PWD_LEN] url team
   
   Generate teams, users, and add them to DOMjudge.
   
   positional arguments:
     url                DOMjudge url. Example: https://bcpc.buaaacm.com/domjudge
     team               Team number
   
   optional arguments:
     -h, --help         show this help message and exit
     --pwd-len PWD_LEN  Password length
   ```

## judgehost 压力测试

1. 将 `random_submission.py`、`accounts.tsv` 复制到 `domjudge/` 目录
2. 运行 `python3 random_submission.py`：
   ```
   usage: random_submission.py [-h] [--submit-interval SUBMIT_INTERVAL] url contest_id

   Randomly submit to DOMjudge.
   
   positional arguments:
     url                   DOMjudge url. Example: https://bcpc.buaaacm.com/domjudge
     contest_id            Contest Id
   
   optional arguments:
     -h, --help            show this help message and exit
     --submit-interval SUBMIT_INTERVAL
                           Interval between submissions
   ```
