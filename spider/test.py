# -*- coding: utf-8 -*-
# Author：邹钰莹
# Start：2024-6-6  13:40
# Finished：
# Description：

# 导入库
import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from utils import creat_csv, save_to_csv

# 伪装请求头
ua = UserAgent()
headers = {
    'Cookie':
        'SINAGLOBAL=9357181710317.033.1695259812572; SCF=AkqLyi9i9y85vGtbFIphVfEBYPit8obQec9bKd3o39ePZINFCW3_xTpRp9SRP8GTyO8G5FBw35XCA4WWgYedb58.; UOR=,,cn.bing.com; SUB=_2A25LWppFDeRhGeFH6VYW-S3EwziIHXVoGZONrDV8PUNbmtAbLU_RkW9Ne7a6Yizsa3sLTDetu5JCN9PMvqiAsUKi; ALF=02_1720088341; PC_TOKEN=b53de0406b; _s_tentry=weibo.com; Apache=6185690656414.809.1717496937027; ULV=1717496937124:19:6:5:6185690656414.809.1717496937027:1717458883060',
    'User-Agent': ua.random,
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# 爬取话题页
def get_topic_page(topic, start_page, end_page):
    # 话题页url
    url = f"https://s.weibo.com/weibo?q=%23{topic}%23"
    # 开爬页数
    page = start_page
    # 已爬博文数
    blog_count = 0
    # 按页爬取该话题下的博文
    while page <= end_page:
        # time.sleep(1)
        print('第' + str(page) + '页')
        cur_url = url + '&page=' + str(page)
        # print(cur_url)
        try:
            res = requests.get(cur_url, headers=headers)
            print('请求成功')
        except:
            continue
        soup = bs(res.text, 'html.parser')
        # 第一个div.card-wrap不是
        blogs = soup.select('#pl_feedlist_index > div:nth-child(4) .card-wrap')[1:]
        for blog in blogs:
            # print(blog)
            # mid（广告多一层没mid的同类div，所以遇到没mid的div就跳过）
            try:
                mid = blog['mid']
                # print(mid)
            except:
                continue

            # 博文链接
            blog_url = blog.select_one('div.card div.content .from a')
            if blog_url is None:
                pass
                # continue
            else:
                blog_url = 'https:' + blog_url['href']
                bid = blog_url.split('?')[0].split('/')[-1]
            # print(bid)
            # print("博文链接：", blog_url)

            # 用户链接和uid
            user_url = blog.select_one('div.card div.content div.info a.name')
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
            userName = blog.select_one('div.card div.content div.info a.name').text
            # print("用户名：", userName)

            # 博文内容
            blog_content = blog.select_one('div.card div.content p.txt').text
            blog_content = ''.join(blog_content).replace(' ', '').replace('\n', '').strip()
            # print("博文内容：", blog_content)

            # 点赞数
            blog_like = blog.select_one('div.card span.woo-like-count').text.strip()
            if blog_like == '赞':
                blog_like = 0
            # print("点赞数：", blog_like)

            # 评论数
            blog_comment = blog.select('div.card div.card-act ul li a')[1].text.strip()
            if blog_comment == '评论':
                blog_comment = 0
            # print("评论数：", blog_comment)

            # 转发数
            blog_forward = blog.select('div.card div.card-act ul li a')[0].text.strip()
            if blog_forward == '转发':
                blog_forward = 0
            # print("转发数：", blog_forward)

            # 发博时间，发博IP
            blog_time, blog_ip = get_blogInfo(bid)

            data_dict = {
                '话题': topic,
                '用户链接': user_url,
                '用户名': userName,
                '博文链接': blog_url,
                '发博时间': blog_time,
                '发博IP': blog_ip,
                '博文内容': blog_content,
                '点赞数': blog_like,
                '评论数': blog_comment,
                '转发数': blog_forward,
                '用户性别': '',
                '用户粉丝数': '',
                '用户身份认证': '',
            }
            user_dict = get_userInfo(mid, uid)
            for k in user_dict:
                data_dict[k] = user_dict[k]
            for k, v in data_dict.items():
                print(k, '：', v, sep='')
            save_to_csv(data_dict)
            blog_count += 1
            print('第' + str(blog_count) + '条微博\n------------------------------------------')
        page = page + 1

# 获取博文详情
def get_blogInfo(id):
    url = f"https://weibo.com/ajax/statuses/show?id={id}&locale=zh-CN"
    res = requests.get(url, headers=headers)
    # 发博时间
    blog_time = res.json()['created_at']
    # 发博IP
    try:
        ip = res.json()['region_name']
    except:
        ip = '无'
    return blog_time, ip

# 获取用户信息
def get_userInfo(mid, uid):
    url = f"https://weibo.com/ajax/statuses/checkReward?mid={mid}&uid={uid}&reward_scheme=%7B%22bid%22:%221000293251%22%7D&type=pc"
    res = requests.get(url, headers=headers)
    user = res.json()['data']['user']
    # 粉丝数
    fans = user['followers_count']
    # 性别
    gender = user['gender']
    # 身份认证
    identify = user['verified_reason']
    return {
        '用户性别': gender,
        '用户粉丝数': fans,
        '用户身份认证': identify
    }

if __name__ == '__main__':
    creat_csv()
    get_topic_page("21岁重庆男子跳江", 1, 10)