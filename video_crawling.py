import json
import logging
import os
import re
import threading
import time
from queue import Queue

import requests
from lxml import etree
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoDownloader:
    def __init__(self):
        self.q = Queue(2000)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        }

    def get_ts_url(self, url):
        try:
            response = requests.get(url=url, headers=self.headers)
            response.raise_for_status()
            if response.status_code == 200:
                html = response.content.decode()  # 从网页中找到m3u8文件链接和视频的title
                pattern = re.compile(
                    r'<script\s+type="text/javascript">\s*var\s+player_aaaa\s*=\s*({[\s\S]*?})\s*<\/script>'
                )
                el = etree.HTML(html)
                title = el.xpath(
                    '//div[@class="stui-pannel__head clearfix"]/h3[@class="title"]/text()'
                )[1]
                print(f"将要下载的视频名称: {title}")
                # 使用正则表达式进行匹配
                match = pattern.search(html)
                # 判断是否匹配成功
                if match:
                    # 获取匹配的内容
                    matched_script = match.group(1)
                    # 解析为字典对象
                    data_dict = json.loads(matched_script)
                    m3u8_url = data_dict["url"]
                    # print(m3u8_url)
                    m3u8_text = requests.get(url=m3u8_url, headers=self.headers).text
                    # 得到所有的ts文件名list
                    ts_file: list = re.findall(r"\b(\d+\.ts)\b", m3u8_text)
                    # print(ts_file)
                    for ts_index, ts_name in enumerate(ts_file):
                        ts_url = m3u8_url.replace("index.m3u8", "") + ts_name
                        # print(ts_url)
                        self.q.put([ts_index, ts_url])  # 加入队列
                    return title, len(ts_file)  # return title, len(ts_file)
            else:
                print("get_m3u8_url 未找到匹配的内容")

        except requests.RequestException as e:
            logger.error(f"请求失败: {e}")
            return None

    def download_ts(self, file_path, title, progress_bar):
        """
        下载ts文件
        :param file_path: 保存路径
        :param title: 视频标题
        :param progress_bar: 进度条
        :return: None
        """
        while not self.q.empty():
            ts_index, ts_url = self.q.get()
            ts_file_name = os.path.join(file_path, title)
            while True:
                try:
                    response = requests.get(
                        url=ts_url, headers=self.headers, stream=True, timeout=500
                    )
                    response.raise_for_status()
                    ts_content = response.content
                    file_size = response.headers["Content-Length"]
                    if not str(len(ts_content)) == file_size:
                        print(
                            f"下载的文件{ts_content}:{str(len(ts_content))} 和请求到的文件{file_size}:{str(len(file_size))}大小不相同"
                        )
                        continue

                except requests.RequestException as e:
                    logger.error(f"请求失败: {e}")
                    time.sleep(0.5)

                else:
                    print(f"{ts_file_name}_{ts_index}.ts 请求正常，开始下载----------->")
                    with open(f"{ts_file_name}_{ts_index}.ts", "wb") as f:
                        f.write(ts_content)
                        progress_bar.update(1)  # Update the progress bar
                        print(f"{threading.current_thread().name}:  已下载完成----->:{ts_file_name}_{ts_index}.ts")
                        break

    @staticmethod
    def combine_ts(file_path, title, length, progress_bar):
        try:
            # 合并文件
            print(f"开始合并文件:{title}")
            mp4_file_name = os.path.join(file_path, title)
            with open(f"{mp4_file_name}.mp4", "ab") as f:
                for i in range(length):
                    ts_filename = f"{file_path}/{title}_{i}.ts"
                    if os.path.exists(ts_filename):
                        with open(ts_filename, "rb") as fb:
                            content = fb.read()
                            f.write(content)
                        os.remove(ts_filename)
                        progress_bar.update(1)  # 更新进度条
                print(f"{mp4_file_name}下载完成")
        except Exception as e:
            logger.error(f"合并时出错: {e}")

    def main(self):
        try:
            print("网站:http://hsck824.cc")
            user_input = input(
                "请输入视频播放页链接，例如 <http://hsck824.cc/vodplay/37106-1-1/> ,开始下载---------->\n"
            )
        except KeyboardInterrupt:
            logger.error("已取消")
        else:
            url = user_input
            file_path = r"d:/photo/5"  # 文件保存路径
            print(f"文件保存路径:{file_path}")
            os.makedirs(file_path, exist_ok=True)
            result = self.get_ts_url(url)
            if result:
                title, length = result
                download_progress_bar = tqdm(
                    total=length, unit="ts", unit_scale=True, desc=f"下载中 {title}"
                )

                threads = []
                for i in range(32):  # 线程数
                    thread = threading.Thread(
                        target=self.download_ts,
                        args=(file_path, title, download_progress_bar),
                        name=f"线程{i}",
                    )
                    thread.start()
                    threads.append(thread)

                for th in threads:
                    th.join()
                download_progress_bar.close()
                combine_progress_bar = tqdm(
                    total=length, unit="ts", unit_scale=True, desc=f"合并中 {title}.ts"
                )
                self.combine_ts(file_path, title, length, combine_progress_bar)
                combine_progress_bar.close()


if __name__ == "__main__":
    downloader = VideoDownloader()
    downloader.main()
