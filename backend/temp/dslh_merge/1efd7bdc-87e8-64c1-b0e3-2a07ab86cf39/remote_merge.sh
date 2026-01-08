#!/bin/bash
DB_PERFIX=ycnrg05xybys
DB_USER=root
DB_IP="127.0.0.1"
DB_PWD="JnC25k4JApFcRyBN"
DB_PORT=33008

export MYSQL_PWD=$DB_PWD

if [ -d "/home/merge/merge" ]; then
    echo "检测到 /home/merge/merge 存在，正在删除..."
    rm -rf "/home/merge/merge"
    echo "删除完成。"
fi
mkdir -p "/home/merge/merge"
BACKUP=/home/merge/merge

startId=1
endId=22

if [ -z "$startId" ]; then
    echo "请输入起始服务器id"
    exit 1
elif [ -z "$endId" ]; then
    echo "请输入结束服务器id"
    exit 1
elif [ "$startId" -gt "$endId" ]; then
    echo "起始服务器id应小于等于结束服务器id"
    exit 1
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # 恢复默认颜色

for ((i = startId; i <= endId; i++)); do
    echo -e "${GREEN}====备份数据库==== ${DB_PERFIX}$i${NC}"
    databse=${DB_PERFIX}$i
    mysqldump -u$DB_USER -h $DB_IP -P$DB_PORT -R --opt $databse > ${BACKUP}\/${databse}.sql
    echo -e "${RED} ====备份数据库结束==== ${DB_PERFIX}$i${NC}\n"
done

echo -e "${GREEN}====备份数据库结束====${NC}\n"