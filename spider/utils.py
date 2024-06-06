# -*- coding: utf-8 -*-
# Author：邹钰莹
# Start：2024-6-6  14:15
# Finished：
# Description：

from pathlib import Path
import csv

csv_file = 'MicroBlog.csv'
csv_file_path = Path(csv_file)
column_names = ["话题", "用户链接", "用户名", "博文链接", "发博时间", "发博IP", "博文内容",
                "点赞数", "评论数", "转发数", "用户性别", "用户粉丝数", "用户身份认证"]
# 建csv文件
def creat_csv():
    # csv文件不存在就建
    if not csv_file_path.exists():
        # 定义csv文件表头
        with csv_file_path.open(mode='a', newline='', encoding='utf-8') as file_writer:
            # writer = csv.writer(file_writer)
            # writer.writerow(column_names)
            writer = csv.DictWriter(file_writer, fieldnames=column_names)
            writer.writeheader()

# 保存到csv文件里
def save_to_csv(data_dict):
    with open(csv_file, 'a', newline='', encoding='utf-8-sig') as file:
        # writer = csv.writer(file)
        # writer.writerow(data_list)
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writerow(data_dict)