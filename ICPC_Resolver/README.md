1. 下载 [ICPC Resolver](https://tools.icpc.global/resolver/)，解压
2. `./awards.sh` 打开图形界面，进入 REST 界面，输入 `URL: https://your.domjudge.domain/api/v4/contests/{cid}/`，admin 的账号密码，点击 connect
3. 将默认奖项删除，之后依次添加 Rank（前三）奖项，First to Solve 奖项，并将 Rank 奖项的名称修改为中文，保存为 `award.json`
4. 将 `event_feed.py` 移动到当前目录并运行，目的是主要是删除非参赛队伍和 TOO-LATE 的提交
   ```
   usage: event_feed.py [-h] [--award-path AWARD_PATH] [--ignore-submission-after IGNORE_SUBMISSION_AFTER] [--save-path SAVE_PATH] available_groups

   Fix event feed of domjudge.
   
   positional arguments:
     available_groups      Available groups, split with comma(,). Example: Participants,Observers
   
   optional arguments:
     -h, --help            show this help message and exit
     --award-path AWARD_PATH
                           Award file path. Default: award.json.
     --ignore-submission-after IGNORE_SUBMISSION_AFTER
                           Ignore submission after contest passed this time. Mainly used to ignore too late submissions. Format: %H:%M:%S.%f. Example: 336:00:00.000. Default: contest length.
     --save-path SAVE_PATH
                           Path to save modified event feed. Default: award-fixed.json.
   ```
5. 运行下面命令，其中 `lastGold`，`lastSilver` 和 `lastBronze` 指金银铜奖的数量。
   ```shell
   ./awards.sh award-fixed.json --medals <lastGold> <lastSilver> <lastBronze>
   ```
6. 查看生成的 `award-fixed-awards.json` 文件，将 `Gold Medalist` 修改为一等奖 `\u4e00\u7b49\u5956`，`Silver Medalist` 修改为二等奖 `\u4e8c\u7b49\u5956`，`Bronze Medalist` 修改为三等奖 `\u4e09\u7b49\u5956`
7. 设置字体文件，其中 `YOUR/FONT` 是你电脑自带的某个支持中文的字体文件的绝对路径
   ```shell
   export ICPC_FONT=/YOUR/FONT
   ```
8. 运行滚榜命令，其中`place` 指从`place`后单步运行
   ```shell
   ./resolver.sh award-fixed-awards.json --fast 0.2 --test --singleStep <place>
   ```
9.  务必大致核对一遍奖项和榜单（时间允许的情况下）