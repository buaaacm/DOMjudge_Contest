## 查看数据库占用空间

```sql
USE domjudge;
SELECT CONCAT(table_schema,'.',table_name) AS 'Table Name', CONCAT(ROUND(table_rows/1000000,4),'M') AS 'Number of Rows', CONCAT(ROUND(data_length/(1024*1024*1024),4),'G') AS 'Data Size', CONCAT(ROUND(index_length/(1024*1024*1024),4),'G') AS 'Index Size', CONCAT(ROUND((data_length+index_length)/(1024*1024*1024),4),'G') AS'Total'FROM information_schema.TABLES WHERE table_schema LIKE 'domjudge';
```

## 清理 judging_run_output 表

DOMjudge 居然会保存整个输出！！！一个解决思路是手动改数据库，把输出截断。

```sql
UPDATE domjudge.judging_run_output AS jro SET jro.output_run = substr(jro.output_run, 1, LEAST(100000, LENGTH(jro.output_run)));
```

之后可能要手动重建表，否则空间不能得到释放。

## 