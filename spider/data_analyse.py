# -*- coding: utf-8 -*-
# Author：邹钰莹
# Start：2024-6-4  19:54
# Finished：
# Description：

import re
import pandas
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import emoji

# plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']

# 加载停用词表
stopwords_file = 'baidu_stopwords.txt'
with open(stopwords_file, 'r', encoding='utf-8') as words:
    stopwords = [i.strip() for i in words.readlines()]

# 分词函数
def segment(texts):
    segmented_texts = []
    for text in texts:
        if len(text) == 0:
            continue
        seg_list = ' '.join(jieba.lcut(text, cut_all=True))
        segmented_texts.append(seg_list)
    return segmented_texts

# 绘制词云图函数
def generate_wordcloud(text):
    wordcloud = WordCloud(font_path="simhei.ttf", background_color="white", width=800, height=600, margin=2).generate(text)
    plt.figure(figsize=(8, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.show()

# 数据清洗函数
def clean_text(text):
    text = str(text)
    # # 去除话题
    # text = re.sub(r"#\w+#", " ", text)
    # 去除零宽空格（在字体报错中发现的）
    text = text.replace('\u200b', '')
    # 去除ue627
    text = text.replace('\ue627', '')
    # 去除表情符号
    text = emoji.replace_emoji(text, replace=" ")
    # 去除网址
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    text = url_pattern.sub(r" ", text)
    # # 去除停用词。好像会把“用”去掉
    # for word in stopwords:
    #     text = text.replace(word, "")
    # 合并多余的空格
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# 绘制词频图函数
def plot_word_frequency(text):
    word_list = jieba.lcut(text)
    word_counts = Counter(word_list)
    word_freq = word_counts.most_common(20)
    words, freqs = zip(*word_freq)

    # plt.rcParams['font.family'] = 'SimHei'  # 使用SimHei作为默认字体
    # 绘制词频图
    plt.figure(figsize=(10, 6))
    plt.bar(words, freqs)
    plt.xticks(rotation=90)
    plt.xlabel("词")
    plt.ylabel("词频")
    plt.title("博文词频图")
    plt.show()

csv_file = 'topic-blog.csv'
data = pandas.read_csv(csv_file)
weibo_content = data['发博内容']
weibo_content = weibo_content.drop_duplicates()
print(weibo_content.head())

# 数据清洗
weibo_content = weibo_content.apply(clean_text)
print(weibo_content.head())

# # 分词
# segmented_texts = segment(weibo_content)
#
# # 绘制词云图
# text = ' '.join(segmented_texts)
# generate_wordcloud(text)
#
# 绘制词频图
# total_text = ' '.join(weibo_content)
# plot_word_frequency(total_text)
#
# # 绘制饼状图
# gender = data['用户性别']
# pie_labels = gender.value_counts()[:10].index
# plt.pie(gender.value_counts()[:10], labels=pie_labels, autopct='%1.1f%%')
# plt.title('博主性别分布')
# plt.show()
#
# # count = data[["点赞数", "评论数", "转发数", "用户粉丝数", "用户转评赞总数"]]
# # print(count.describe().astype(int))
#
# # 绘制柱状图
# count = data[["点赞数", "评论数", "转发数"]]
# count.plot(kind="bar", stacked=True)
# plt.xlabel("博文", rotation = 0)
# plt.title("博文互动量统计")
# plt.show()
#
# # 绘制点状图：粉丝数与点赞数的关系
# plt.scatter(data["用户粉丝数"], data["点赞数"])
# plt.xlabel("粉丝数")
# plt.ylabel("点赞数")
# plt.title("粉丝数与点赞数的关系")
# plt.show()

# 情感分析
# def analyse_sentiment(text):
#     if len(text) == 0:
#         return 0
#     s = SnowNLP(text)
#     return s.sentiments