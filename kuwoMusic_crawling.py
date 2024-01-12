import concurrent.futures
import json
import os
import re

import requests

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "_ga=GA1.2.492061537.1704179089; _gid=GA1.2.692247719.1704179089; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1704179090; _gat=1; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1704179426; Hm_Iuvt_cdb524f42f0cer9b268e4v7y735ewrq2324=TK2HhNJKfpaBrTMCmGePnQNhXFAX2Rpp; _ga_ETPBRPM9ML=GS1.2.1704179090.1.1.1704179426.60.0.0",
    "DNT": "1",
    "Host": "www.kuwo.cn",
    "Pragma": "no-cache",
    "Referer": "https://www.kuwo.cn/rankList",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Secret": "d79fc10c2de29da680fc3dd9a08b6b6ab3e3f982294c84da984e9455961b131f05935afc",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0"
}


def get_music_list():
    """
    yield name,music_id
    """
    url = "https://www.kuwo.cn/api/www/bang/bang/musicList?"

    params = {
        "bangId": "158",  # 抖音热榜158，酷我热榜16
        "pn": "1",
        "rn": "20",
        "httpsStatus": "1",
        "reqId": "d0d19450-a939-11ee-b382-77b914b727dd",
        "plat": "web_www"
    }

    response = requests.get(url=url, params=params, headers=headers)
    try:
        if response.status_code == 200 and response.json()["code"] == 200:
            num = response.json()["data"]["num"]  # 音乐总数
            # print(type(num))
            pn = int(num) // 20  # 总页数
            for i in range(pn):
                music_response = requests.get(url=url, params={  # 重新请求
                    "bangId": "158",
                    "pn": i,
                    "rn": "20",
                    "httpsStatus": "1",
                    "reqId": "d0d19450-a939-11ee-b382-77b914b727dd",
                    "plat": "web_www"
                }, headers=headers)
                music_list = music_response.json()["data"]["musicList"]
                for music in music_list:  # 遍历得到所有的音乐id，名称
                    music_name = music["name"]
                    music_id = music["rid"]
                    yield music_name, music_id

    except requests.RequestException:
        print("请求失败！")
        yield None


def get_music_play_urls():
    """
    传入music_id 得到 音乐播放url
    return music_play_url
    """
    url = "https://bd.kuwo.cn/api/v1/www/music/playUrl?"
    music_list = get_music_list()
    for name, music_id in music_list:
        params = {
            "mid": music_id,  # 歌曲id
            "type": "music",
            "httpsStatus": "1",
            "reqId": "5037f9a0-a944-11ee-9245-2fd97fe4112b",
            "plat": "web_www"
        }
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.json()["code"] == 200:
                music_play_url = response.json()["data"]["url"]  # 播放地址 *.mp3
                yield name, music_play_url  # 返回音乐播放地址
            elif response.json()["code"] == -1:
                print(f"{name} 该歌曲为付费内容")
        except json.JSONDecodeError:
            print("请求错误")


def download_music(args):
    name, music_play_url = args
    # print(f"音乐播放链接:{music_play_url}")
    pattern = re.compile(r'https://(.*?)/')
    match = pattern.search(music_play_url)
    host = match.group(1)  # 得到请求头中的Host
    # print(f"host:{host}")
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "identity;q=1, *;q=0",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Host": host,
        "Pragma": "no-cache",
        "Range": "bytes=0-",
        "Referer": "https://m.kuwo.cn/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0",
    }
    file_path = r'd:/photo/3/'
    os.makedirs(file_path,exist_ok=True)  # 创建文件夹
    file_name = os.path.join(file_path, name + ".mp3")
    music_content = requests.get(url=music_play_url, headers=headers, stream=True, timeout=500).content
    if music_content:
        with open(file_name, "wb") as f:
            f.write(music_content)
            print(name + "下载完成")
            f.close()
    else:
        print(f"{name}音乐内容为空，下载失败")


def download_all_music():
    music_play_urls = get_music_play_urls() # 传入name, music_play_url
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_music, music_play_urls)


if __name__ == '__main__':
    download_all_music()
