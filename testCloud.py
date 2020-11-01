# !/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Author  : Sprite
@File    : testCloud.py
@DATE    : 2020/10/18 0018 16:54
@Program : Pycharm
'''

import jieba  # 分词
from matplotlib import pyplot as plt  # 绘图，数据可视化
from wordcloud import WordCloud       # 词云
from PIL import Image                 # 图片处理
import numpy as np                    # 矩阵运算
import sqlite3


# 准备词云所需文字
con = sqlite3.connect("movie.db")
cur = con.cursor()
sql = "select instroduction from movie250"
data = cur.execute(sql)

text = ''
for item in data:
    text = text + item[0]
cur.close()
con.close()

cut = jieba.cut(text)
string = ' '.join(cut)


img = Image.open(r'.\static\assets\img\tree.jpg')
img_array = np.array(img)
wc = WordCloud(
    background_color = 'white',
    mask = img_array,
    font_path = "HGY2_CNKI.TTF" #字体所在位置 ： C:\Windows\Fonts
)

wc.generate_from_text(string)


# 绘制图片

fig = plt.figure(1)
plt.imshow(wc)
plt.axis('off')#是否显示坐标轴

# plt.show()

plt.savefig(r'.\static\assets\img\word.jpg')

