# -*- coding: utf-8 -*-
# Author：邹钰莹
# Start：2024-6-1  21:15
# Finished：
# Description：一个话题下的微博及博主相关信息爬取

# 导入库
import requests
from bs4 import BeautifulSoup as bs
import time
import datetime
import csv
from pathlib import Path
import pandas
import re
import pymysql
import json
from fake_useragent import UserAgent
# from requests import HTTPError
# from selenium import webdriver


# 请求URL
# url = '<https://weibo.com/>'
# 请求头部
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
# }

# 解析页面函数
# def parse_html(html):
#     print(html)

# 保存数据函数
# def save_data():
#     f = open('weibo.txt', 'w', encoding='utf-8')
#     browser = webdriver.Chrome()
#     browser.get(url)
#     time.sleep(10)
#     browser.find_element_by_name('username').send_keys('username')
#     browser.find_element_by_name('password').send_keys('password')
#     browser.find_element_by_class_name('W_btn_a').click()
#     time.sleep(10)
#     response = requests.get(url, headers=headers, cookies=browser.get_cookies())
#     parse_html(response.text)
#     browser.close()
#     f.close()
#
# if __name__ == '__main__':
#     save_data()

# 建csv文件
csv_file = 'topic-blog.csv'
csv_file_path = Path(csv_file)
column_names = ["话题", "用户链接", "用户名", "博文链接", "发博时间", "发博内容", "点赞数", "评论数", "转发数",
                "用户性别", "用户IP", "用户粉丝数", "用户转评赞总数"]
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

ua = UserAgent()
headers = {
    'Cookie':
        'SINAGLOBAL=9357181710317.033.1695259812572; SCF=AkqLyi9i9y85vGtbFIphVfEBYPit8obQec9bKd3o39ePZINFCW3_xTpRp9SRP8GTyO8G5FBw35XCA4WWgYedb58.; UOR=,,cn.bing.com; SUB=_2A25LWppFDeRhGeFH6VYW-S3EwziIHXVoGZONrDV8PUNbmtAbLU_RkW9Ne7a6Yizsa3sLTDetu5JCN9PMvqiAsUKi; ALF=02_1720088341; PC_TOKEN=b53de0406b; _s_tentry=weibo.com; Apache=6185690656414.809.1717496937027; ULV=1717496937124:19:6:5:6185690656414.809.1717496937027:1717458883060',
    'User-Agent':
        ua.random,
        # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    # 'Connection': 'keep-alive',
    # 'Host': 's.weibo.com',
    # 'Referer': 'https://www.weibo.com/'
}

page = 1
# pageCount = 1
weibo_count = 0

baseUrl = 'https://s.weibo.com/weibo?q={}'
topic = '#阳光信用#'
fileName = topic.replace('#', '')
url = baseUrl.format(requests.utils.quote(topic))
# print(url)

def get_userInfo(uid):
    url = f"https://weibo.com/ajax/profile/info?custom={uid}"
    # IP在detail
    detail_url = f"https://weibo.com/ajax/profile/detail?uid={uid}"
    res = requests.get(url, headers=headers)
    detail_res = requests.get(detail_url, headers=headers)
    # soup = bs(res.text, 'html.parser')
    data = res.json()['data']
    user = data['user']
    ip = detail_res.json()['data']['ip_location'].split('：')[1]
    gender = '女' if user['gender'] == 'f' else '男'
    return {
        # 性别
        '用户性别': gender,
        # ip属地。这里有问题！！！！！！
        '用户IP': ip,
        # 粉丝数
        '用户粉丝数': user['followers_count'],
        # 转评赞（注意这是字符串）
        # '用户转评赞总数': user['status_total_counter']['total_cnt']
        '用户转评赞总数': '',
        # 身份认证
        '用户身份认证': '',
    }

data_list = []
while page <= 1:
    # time.sleep(1)
    print('正在爬取第' + str(page) + '页')
    tempUrl = url + '&page=' + str(page)
    # print(tempUrl)
    try:
        res = requests.get(tempUrl, headers=headers)
        print('请求成功')
    except:
        continue
    soup = bs(res.text, 'html.parser')
    # mid = soup.select('#pl_feedlist_index > div:nth-child(4) .card-wrap')
    articals = soup.select('#pl_feedlist_index > div:nth-child(4) .card-wrap')[1:]
    for artical in articals:
        # mid
        mid = artical['mid']
        print(mid)
        # print(artical)
        # 博文链接
        blog_url = artical.select_one('div.card div.content div.from a')
        if blog_url is None:
            continue
        else:
            blog_url = 'https:' + blog_url['href']
            # blog_id = blog_url.split('/')[-2]
        # print("博文id：", blog_id)
        # print("博文链接：", blog_url)

        # 用户链接
        user_url = artical.select_one('div.card div.content div.info a.name')
        uid = ''
        if user_url is None:
            pass
        else:
            user_url = user_url['href']
            user_url = 'https:' + user_url
            uid = user_url.split('?')[0].split('/')[-1]
        # print("用户id：", uid)
        # print("用户链接：", user_url)

        # 用户名
        userName = artical.select_one('div.card div.content div.info a.name').text
        # print("用户名：", userName)

        # 发博时间
        # blog_time = artical.select_one('div.content div.from a').text.strip()
        # print("发博时间：", blog_time)

        # 发博内容
        blog_content = artical.select_one('div.card div.content p.txt').text
        blog_content = ''.join(blog_content).replace(' ', '').replace('\n', '').strip()
        # print("发博内容：", blog_content)

        # 点赞数
        blog_like = artical.select_one('div.card span.woo-like-count').text.strip()
        if blog_like == '赞':
            blog_like = 0
        # print("点赞数：", blog_like)

        # 评论数
        blog_comment = artical.select('div.card div.card-act ul li a')[1].text.strip()
        if blog_comment == '评论':
            blog_comment = 0
        # print("评论数：", blog_comment)

        # 转发数
        blog_forward = artical.select('div.card div.card-act ul li a')[0].text.strip()
        if blog_forward == '转发':
            blog_forward = 0
        # print("转发数：", blog_forward)

        # data_list = [topic, userName, blog_time, blog_content, 0, 0, 0]
        data_dict = {
            '话题': topic,
            '用户链接': user_url,
            '用户名': userName,
            '博文链接': blog_url,
            # '发博时间': blog_time,
            '发博时间': '',
            '发博内容': blog_content,
            '点赞数': blog_like,
            '评论数': blog_comment,
            '转发数': blog_forward,
            '用户性别': '',
            '用户IP': '',
            '用户粉丝数': '',
            '用户转评赞总数': '',
            '用户身份认证': '',
        }
        user_dict = get_userInfo(uid)
        for k in user_dict:
            data_dict[k] = user_dict[k]
        for k, v in data_dict.items():
            print(k, '：', v, sep='')
        # save_to_csv(data_dict)
        weibo_count += 1
        print('第' + str(weibo_count) + '条微博\n------------------------------------------')
    page = page + 1