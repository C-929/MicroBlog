# -*- coding: utf-8 -*-
# Author：邹钰莹
# Start：2024-6-1  15:23
# Finished：
# Description：

import time
import threading
# 任意准备一个函数
def my_func(a):
    print(a)

# # threading.Thread()创建一个线程对象。target：传入函数名；args：传入函数的参数
# t = threading.Thread(target=my_func, args=(1,))
#
# # 启动线程
# t.start()
#
# # 等待结束。想知道线程什么时候结束，可以使用join()方法
# t.join()

# # 单线程
# def single_thread():
#     print('single thread')
#     for i in range(100):
#         my_func(i)
#     print('single end')
#
# # 多线程
# def multi_thread():
#     print('multi thread')
#     threads = []
#     for i in range(100):
#         threads.append(threading.Thread(target=my_func, args=(i,)))
#
#     for thread in threads:
#         thread.start()
#
#     for thread in threads:
#         thread.join()
#     print('multi end')
#
# if __name__ == '__main__':
#     start = time.time()
#     single_thread()
#     end = time.time()
#     print('single time:', end - start)
#
#     start = time.time()
#     multi_thread()
#     end = time.time()
#     print('multi time:', end - start)

import requests
headers = {
    'Cookie':
        'SINAGLOBAL=9357181710317.033.1695259812572; SCF=AkqLyi9i9y85vGtbFIphVfEBYPit8obQec9bKd3o39ePZINFCW3_xTpRp9SRP8GTyO8G5FBw35XCA4WWgYedb58.; UOR=,,cn.bing.com; SUB=_2A25LWppFDeRhGeFH6VYW-S3EwziIHXVoGZONrDV8PUNbmtAbLU_RkW9Ne7a6Yizsa3sLTDetu5JCN9PMvqiAsUKi; ALF=02_1720088341; PC_TOKEN=b53de0406b; _s_tentry=weibo.com; Apache=6185690656414.809.1717496937027; ULV=1717496937124:19:6:5:6185690656414.809.1717496937027:1717458883060',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
url = "https://weibo.com/ajax/statuses/checkReward?mid=5042170862764048&uid=1893761531&reward_scheme=%7B%22bid%22:%221000293251%22%7D&type=pc"
res = requests.get(url, headers=headers)
# soup = bs(res.text, 'html.parser')
# print(res.text)
user = res.json()['data']['user']
# 粉丝数
fans = user['followers_count']
# 性别
gender = user['gender']
# 身份认证
identify = user['verified_reason']
# 身份认证，没有则是空字串
print(fans, gender, identify, sep='\n')


url = "https://weibo.com/ajax/statuses/show?id=OhH3wbB3q&locale=zh-CN"
res = requests.get(url, headers=headers)
# 发博时间
date = res.json()['created_at']
# 发博IP
try:
    ip = res.json()['region_name']
except:
    ip = '无'
print(date, ip, sep='\n')