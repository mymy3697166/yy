@echo off
cd C:\Program Files\MySQL\MySQL Server 5.7\bin\
set "Ymd=%date:~,4%%date:~5,2%%date:~8,2%"
mysqldump -uroot -proot ordersync > D:\bk_%Ymd%.sql
@echo on