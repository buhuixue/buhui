import json
import os
import re
import threading
from queue import Queue
import time
import requests
from lxml import etree

q = Queue(2000)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
}


def get_ts_url(url):
    """
    获取m3u8链接，得到m3u8文件，在文件中得到ts的链接
    """
    response = requests.get(url=url, headers=headers)
    try:
        if response.status_code == 200:
            # print(response.content.decode())
            html = response.content.decode()
            pattern = re.compile(
                r'<script\s+type="text/javascript">\s*var\s+player_aaaa\s*=\s*({[\s\S]*?})\s*<\/script>')
            el = etree.HTML(html)
            title = el.xpath('//div[@class="stui-pannel__head clearfix"]/h3[@class="title"]/text()')[1]
            print(f"将要下载的视频名称: {title}")
            # 使用正则表达式进行匹配
            match = pattern.search(html)
            # 判断是否匹配成功
            if match:
                # 获取匹配的内容
                matched_script = match.group(1)
                # 解析为字典对象
                data_dict = json.loads(matched_script)
                m3u8_url = data_dict['url']
                # print(m3u8_url)
                m3u8_text = requests.get(url=m3u8_url, headers=headers).text
                # 得到所有的ts文件名list
                ts_file: list = re.findall(r'\b(\d+\.ts)\b', m3u8_text)
                # print(ts_file)
                for ts_index, ts_name in enumerate(ts_file):
                    ts_url = m3u8_url.replace("index.m3u8", "") + ts_name
                    # print(ts_url)
                    q.put([ts_index, ts_url])  # 加入队列
                return title, len(ts_file)
            else:
                print("get_m3u8_url 未找到匹配的内容")
    except requests.RequestException:
        print("request请求失败")


def download_ts(file_path, title):
    while not q.empty():
        ts_index, ts_url = q.get()
        ts_file_name = os.path.join(file_path, title)  # 拼接得到带路径的文件名称'
        while True:
            try:
                response = requests.get(url=ts_url, headers=headers, stream=True, timeout=500)
                ts_content = response.content
                file_size = response.headers['Content-Length']
                if not str(len(ts_content)) == file_size:
                    print(f'下载的文件{ts_content}:{str(len(ts_content))} 和请求到的文件{file_size}:{str(len(file_size))}大小不相同')
                    continue
            except Exception as e:
                print(f"抛出的异常:{e}")
                print(f"{ts_file_name}_{ts_index}.ts :请求失败，正在重试")
                time.sleep(1)
            else:
                print(f"{ts_file_name}_{ts_index}.ts 请求正常，开始下载----------->")
                with open(f'{ts_file_name}_{ts_index}.ts', 'wb') as f:
                    f.write(ts_content)
                    print(f"{threading.current_thread().name}:  已下载完成----->:{ts_file_name}_{ts_index}.ts")
                    break


def combine_ts(file_path, title, length):
    # 合并文件
    mp4_file_name = os.path.join(file_path, title)
    with open(f'{mp4_file_name}.mp4', 'ab') as f:
        for i in range(length):
            if os.path.exists(f'{file_path}/{title}_{i}.ts'):
                with open(f'{file_path}/{title}_{i}.ts', 'rb') as fb:
                    content = fb.read()
                    f.write(content)
                os.remove(f'{file_path}/{title}_{i}.ts')
        print(f"{mp4_file_name}下载完成")


def main():
    print("网站:http://hs.cc")
    user_input = input("请输入视频播放页链接，例如 <http://hs.cc/vodplay/37106-1-1/> ,开始下载---------->\n")
    url = user_input
    file_path = r'/mnt/media/other'
    print(f"文件保存路径:{file_path}")
    os.makedirs(file_path, exist_ok=True)
    title, length = get_ts_url(url)
    # 多线程下载全部ts文件
    threads = []
    for i in range(32):
        thread = threading.Thread(target=download_ts, args=(file_path, title), name=f"线程{i}")
        thread.start()
        threads.append(thread)

    for th in threads:
        th.join()

    combine_ts(file_path, title, length)


if __name__ == '__main__':
    main()
