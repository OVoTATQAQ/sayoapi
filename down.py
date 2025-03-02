import requests
import os
import time
from tqdm import tqdm

import re

import multitasking
import signal

import glob

signal.signal(signal.SIGINT, multitasking.killall)

class download:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) OsuCrawler/1.0',
            'Referer': ''
        }
        self.todown = set()

    def getsid(self, db, offset):

        # 初始化变量
        times = 1  # 循环次数，表示将进行10次请求
        limit = 1000  # 每次请求返回的数据量限制，每次请求返回25条数据
        print(offset) # 数据偏移量，初始为0，每次请求后增加limit的值
        mode = 8    # 游戏模式，8表示osu!模式
        sid = set()  # 用于存储所有获取到的beatmap的id，使用集合避免重复
        # 循环进行请求，直到times为0
        while times > 0:
            # 构建请求URL，包含搜索关键词、游戏模式、排序方式、数据限制和偏移量
            url = f'https://api.sayobot.cn/beatmaplist?L={limit}&O={offset}&M={mode}'
            # print(url)
            # 发送GET请求，使用self.headers作为请求头
            response = requests.get(url, headers=self.headers)
            # 检查响应状态码，如果是200表示请求成功
            if response.status_code == 200:
                # 解析响应内容为JSON格式
                data = response.json()['data']
                # 遍历每个beatmapset
                for map in data:
                    if  (map['sid'] not in db):
                        # filename[map['sid']] = str(map['sid']) + ' ' + map['artist'] + ' - ' + map['title'] + '.osz'
                        sid.add(map['sid'])
                # 更新偏移量，准备下一次请求
                offset += limit
                # 减少剩余请求次数
                times -= 1
        return sid

    @multitasking.task
    def download_beatmap(self, id, filename):
        
        url = f'https://dl.sayobot.cn/beatmaps/download/full/{id}'
        
        response = requests.get(url, headers = self.headers, stream = True)

        save_path = 'beatmaps/' + filename + '.osz'

        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

    def getmaphaved(self):  
    
        db = set()

        for f_name in os.listdir('D:\\Program Files (x86)\\osu\\Songs'):
            match = re.match(r'^\d+', f_name)
            if match:
               db.add(match.group())

        return db
        
    def run(self):
        db = self.getmaphaved()
        print("已拥有的地图数量：", db.__len__())

        if not os.path.exists('beatmaps'):
            os.makedirs('beatmaps')
        
        
        tot = 0

        while True:
            multitasking.wait_for_tasks()
            sid = self.getsid(db, tot * 1000)
            sum = 0
            for id in sid:
                self.download_beatmap(id, str(id))
                print(id)
                sum += 1
                tot += 1
                if (sum == 20):
                    multitasking.wait_for_tasks()
                    sum = 0
                if (tot % 100) == 0:
                  print(tot)


if __name__ == '__main__':

    

    download().run()