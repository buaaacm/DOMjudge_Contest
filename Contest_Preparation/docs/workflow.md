## Polygon2DOMjudge

将 Polygon 上下载的 package 转换为 DOMjudge 需要的形式。

### Requirements

`Linux` 系统（或低版本的 `OS X`），`wine`，`texlive-full`。

`Windows` 系统可类似操作。

### 从 Polygon 下载题目文件并 build

1. 用 `polygon_files` 目录中的 `olymp.sty`，`statements.ftl`，`tutorials.ftl` 文件替换 Polygon 的 contest 中的相应文件（在 Properties/Files 中修改）。
2. 在 Polygon 上以 Build full packages (+verify) 的形式 build package，随后下载 package。
3. ```sh
   unzip contest-*****.zip -d contest-*****
   cd contest-*****
   # MACOS version
   sed -i '' 's/latex/xelatex/g' statements/chinese/doall.sh
   # Linux version
   sed -i 's/latex/xelatex/g' statements/chinese/doall.sh
   find ./ -name '*.sh' -exec chmod +x {} \;
   ./doall.sh
   ```

本地 build 出的题面 pdf 很可能不尽如人意，有的地方有一些小 bug，甚至可能 build 失败。这里只需要在 `statements/chinese/` 目录下重新 `./doall.sh` 即可单独 build 题面。

接下来需要在 Polygon 上运行脚本以打包成 DOMjudge 格式的题目包。

1. 参考 `config.sample.yaml` 文件，在 `config.yaml` 文件中修改相关配置
2. （可选）准备好气球颜色 `balloon.yaml`：
   ```
   problem-name1: '#FF7109'
   problem-name2: '#008100'
   ```
   若不准备好该文件，会随机生成气球颜色。
3. 运行 `python3 polygon2domjudge.py`：
   ```
   usage: polygon2domjudge.py [-h] [--origin-ml] [--balloon BALLOON] [--language LANGUAGE] contest_path

   Parse Polygon package to DOMjudge format.
   
   positional arguments:
     contest_path         Contest directory (polygon package) path.
   
   optional arguments:
     -h, --help           show this help message and exit
     --origin-ml          If set, use the original memory limit of Polygon. Otherwise, set memory limit to 2GB.
     --balloon BALLOON    Balloon color config path. Default: Generate random colors
     --language LANGUAGE  Language used in statements Default: chinese
   ```

## Setup Contest

在 DOMjudge 上新建比赛！

步骤如下：

1. 在 `contest.yaml` 中填写比赛信息，例如：
   ```
   name:                     DOMjudge open practice session
   short-name:               practice
   start-time:               '2020-04-30T10:00:00+01:00'
   duration:                 '2:00:00'
   scoreboard-freeze-length: '0:30:00'
   penalty-time:             20
   ```
2. 给 `admin` 创建一个 team，否则添加 submission 时会报 `No jury solutions added: must associate team with your user first.` 错误 
3. 查看题目包的大小，需要修改 `nginx` 中的 `client_max_body_size` 以及 `timeout` 相关参数，而对于单个测试点特别大的情况，还需要修改 `domserver` 的 `docker-compose` 文件中的 `--max_allowed_packet`
4. 运行 `python3 create_contest.py`：
   ```
   usage: create_contest.py [-h] [--contest CONTEST] [--contest-id CONTEST_ID] contest_path

   Add a contest to DOMjudge.
   
   positional arguments:
     contest_path          Contest directory (polygon package) path.
   
   optional arguments:
     -h, --help            show this help message and exit
     --contest CONTEST     Contest config path. Default: ../input/contest.yaml
     --contest-id CONTEST_ID
                           Contest id if the contest exists.
   ```
5. 进入 DOMjudge 的比赛界面，手动修改题目的 shortname

## Config TL and ML

根据评测机的速度，可能需要调整时间限制或空间限制。这时，题面也需要做同步修改。

步骤如下：

1. 运行 `python3 config_tl_ml.py`
2. `get` 可获取当前题面中的限制和 `DOMjudge` 的限制，`set` 可以将题面中的限制修改为 `DOMjudge` 的限制，具体用法参考 `help`
   ```
   usage: config_tl_ml.py [-h] {get,set} contest_path contest_id

   Compare the time limit and the memory limit of the statement and the domjudge setting.
   
   positional arguments:
     {get,set}     Get or set.
     contest_path  Contest directory (polygon package) path.
     contest_id    DOMjudge contest id.
   
   optional arguments:
     -h, --help    show this help message and exit
   ```
3. 别忘了重新 `build` 题面并上传到 `DOMjudge`

## Generate teams and users

1. 运行 `python3 gen_teams.py`：
   ```
   usage: gen_teams.py [-h] [--team-csv TEAM_CSV] [--seats SEATS] [--pwd-len PWD_LEN] group_id max_team_id

   Generate teams, users, and add them to DOMjudge.
   
   positional arguments:
     group_id             Group id to register teams.
     max_team_id          Maximum team id that currently exists. You should manually check it from DOMjudge/database to
                          avoid duplication.
   
   optional arguments:
     -h, --help           show this help message and exit
     --team-csv TEAM_CSV  Team csv file path. Default: ../input/team_info.csv. Refer to the sample file to check its
                          format.
     --seats SEATS        Location file path. Default: ../input/seats.txt. File that lists all available seats.
     --pwd-len PWD_LEN    Password length. Default: 12.
   ```
   选手信息保存于 `output/participant_info.csv` 中

## 压力测试

使用 locust 进行压力测试。测试代码位于 `locustfile.py` 中。

1. 再次确认 `config.yaml` 中的压力测试部分，按实际情况修改参数。
2. 在 `code/` 目录下运行 `locust` 命令。
3. 本地浏览器开启 `http://localhost:8089/` 页面，查看测试情况。