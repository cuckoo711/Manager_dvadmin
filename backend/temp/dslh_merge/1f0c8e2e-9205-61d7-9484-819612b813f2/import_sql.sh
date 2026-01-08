#!/bin/bash

DB_NAME="mjmmx01zssgsjs1"
DB_USER=root
DB_IP=127.0.0.1
DB_PASS="fb6eTkWhpQkcJzaE"
DB_PORT=33008
SQL_FILE="/home/merge/merge4/mjmmx01zssgsjs1.sql"

export MYSQL_PWD=$DB_PASS

echo "正在删除数据库 ${DB_NAME}..."
mysql -u$DB_USER -h$DB_IP -P$DB_PORT -e "DROP DATABASE IF EXISTS ${DB_NAME};"
if [ $? -ne 0 ]; then
    echo "删除数据库失败！"
    exit 1
fi

echo "正在创建数据库 ${DB_NAME}..."
mysql -u$DB_USER -h$DB_IP -P$DB_PORT -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;"
if [ $? -ne 0 ]; then
    echo "创建数据库失败！"
    exit 1
fi

echo "正在导入数据到数据库 ${DB_NAME}..."
mysql -u$DB_USER -h$DB_IP -P$DB_PORT ${DB_NAME} < ${SQL_FILE}
if [ $? -ne 0 ]; then
    echo "数据导入失败！"
    exit 1
fi

echo "操作完成！"