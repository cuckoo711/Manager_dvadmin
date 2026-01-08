#!/bin/bash

# 文件复制模板
# 定义变量
SRC_FILE=/home/merge/merge2/hcz01zssjzys1.sql
DEST_DIR=/home/merge/merge3

# 检查源文件是否存在
if [ ! -f "$SRC_FILE" ]; then
    echo "源文件不存在: $SRC_FILE"
    exit 1
fi

# 确保目标目录存在
if [ ! -d "$DEST_DIR" ]; then
    mkdir -p "$DEST_DIR"
    echo "目标目录不存在，已创建: $DEST_DIR"
fi

# 复制文件
cp "$SRC_FILE" "$DEST_DIR"

# 检查复制是否成功
if [ $? -eq 0 ]; then
    echo "文件已成功复制到: $DEST_DIR"
else
    echo "文件复制失败"
    exit 1
fi