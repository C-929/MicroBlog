# Author: zyy
# Date: 2024-6-1

# 导入库
import requests
# from lxml import etree
from bs4 import BeautifulSoup
import time
import csv
# import os
from pathlib import Path
import pandas as pd
import re
import pymysql
import json

# 解析json
# 将返回值以json的形式展示：
# res.json()
# json.loads(res.text)
# 解析：max_id = res.json()["data"]["max_id"] # 获取maxid给下一页请求用
# 获取二进制数据：
# res.content

class CommentsCrawler():
    # 评论区数据包：buildComments……
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Cookie':
            'SINAGLOBAL=9357181710317.033.1695259812572; SCF=AkqLyi9i9y85vGtbFIphVfEBYPit8obQec9bKd3o39ePZINFCW3_xTpRp9SRP8GTyO8G5FBw35XCA4WWgYedb58.; UOR=,,cn.bing.com; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5lLYzvsLgx.UrORoLlRJh55JpX5KMhUgL.FoMfSozX1K5XSKB2dJLoIf2LxKnLB.qL1KnLxKqL1KnLB-qLxKqLBoBLB.zLxK-L1-eLBKnLxKnLB.qL1hMLxK-L12-LB.zLxKML1-2L1hBLxKBLB.2LB.2LxK-L1K2L1K5t; ALF=1719405652; SUB=_2A25LUA8EDeRhGeFL7VAV-S7IzjiIHXVoLA7MrDV8PUJbkNAbLWKikW1NfciIyUyO5oj7LYJOcroVseE2TPLiRU3_; _s_tentry=www.weibo.com; Apache=5005225609344.11.1717236958103; XSRF-TOKEN=j7ezW2MKsWdxZtisgN4jIdIN; ULV=1717236958207:14:1:3:5005225609344.11.1717236958103:1717027446200; WBPSESS=4lEIDfaqTPvtTnsAyxglp_6Cm0l_nbB4FRBg7GCrmb3HCG8BAMwDiT5Sc1frw8lT36UYTdxssyYN-8x8I5uQ1p0kxjO4JMVYhTjkFZU6Js7GE85AyHbzHgQsgMlm0-8wDr-mjzHaEhIb-X4rTAWRew==',
        # 防盗链
        'Referer':
            'https: // weibo.com / 5032932021 / OgWJNcKlh'
    }
    # max_id, max_id_type = 0, 0
    # params = {
    #     'id': None,
    #     'mid': None,
    #     'max_id': max_id,
    #     'max_id_type': max_id_type
    # }
    table_name = 'comments'
    csv_name = 'comments'
    db = 'weibo'

    # 爬评论。评论动态加载，需用network分析数据来源
    def catch_page(self, page):
        flow = None
        max_id = None
        # id和mid是一样的
        # self.params['id'], self.params['mid'] = id, id
        # 一共爬page页评论，一页最多20条
        for i in range(1, page+1):
            url = f"https://weibo.com/ajax/statuses/buildComments?{flow}is_reload=1&id=5040390393038079&is_show_bulletin=2&is_mix=0{max_id}&count=10&uid=5032932021&fetch_level=0&locale=zh-CN"
            # self.params['max_id'], self.params['max_id_type'] = self.max_id, self.max_id_type
            res = requests.get(url=url, headers=self.headers)
            data_list = res.json()['data']
            flow = 'flow=0&'
            max_id = '&max_id=' + str(res.json()['max_id'])
            print(i, flow, max_id, url)
            # print(res.json())
            for data in data_list:
                text_raw = data['text_raw']
                source = data['source']
                screen_name = data['user']['screen_name']
                print(text_raw, source, screen_name)


    # 执行sql语句
    def query(self, sql, params, type='no_select'):
        params = tuple(params)
        with pymysql.connect(host='localhost', user='root', password='@200429zyy', database=self.db, port=3306,
                             charset='utf8') as con, con.cursor() as cursor:
            # 使用execute()方法执行sql查询
            cursor.execute(sql, params)
            if type != 'no-select':
                data_list = cursor.fetchall()
                con.commit()
                return data_list
            else:
                con.commit()
                return '成功'

    # 保存到数据库
    def save_to_mysql(self):
        with open(self.csv_name, 'r', encoding='utf-8') as r_f:
            reader = csv.reader(r_f)
            for i in reader:
                if i[0] == 'type':
                    continue
                sql = f"insert into '{self.table_name}'(topic,blog_id,comm_id,page,uid,uname,uip,time,gender,comm) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                params = [i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9]]
                self.query(sql, params)

    # 判断数据库某张表是否已存在
    def table_exists(self, cursor, table_name):
        sql = f"show tables like '{self.table_name}';"
        cursor.execute(sql)
        return cursor.fetchone() is not None

    # 建数据库表
    def create_mysql(self):
        try:
            # 使用with语句自动管理连接和游标的关闭
            with pymysql.connect(host='localhost', user='root', password='@200429zyy', database=self.db,
                                 port=3306, charset='utf8') as con, con.cursor() as cursor:
                if self.table_exists(cursor, self.table_name):
                    print(f"Table {self.table_name} exists.")
                else:
                    create_table_sql = '''
                                create table cases(
                                    id int primary key auto_increment,
                                    topic varchar(100),
                                    blog_id varchar(255),
                                    comm_id varchar(255),
                                    page varchar(50),
                                    uid varchar(255),
                                    uname varchar(100),
                                    uip varchar(60),
                                    time varchar(30),
                                    gender varchar(5),
                                    comm varchar(2555)
                                );
                            '''
                    cursor.execute(create_table_sql)
                # 执行DDL语句（CREATE、DROP等）默认自动提交，不需要手动提交
                # conn.commit()
                print('数据库连接成功！')
        except pymysql.Error as e:
            print(f'数据库连接失败！错误信息：{e}')

    # 爬取评论区信息
    # def crawl_data(self):
    #     for i in


if __name__ == '__main__':
    CommentsCrawler().catch_page(50)