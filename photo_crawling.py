import json
import os
import threading
import requests


def pic_get(url):
    """
    图片请求
    """
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Host": "more.yesky.com",
        "Origin": "https://wap.yesky.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # print(response.text)
        return response.text
    else:
        print("网络错误,状态码:", response.status_code)


def format_data():
    """
    格式数据
    {(title,url),(....,...)}
    """
    pic_titles = []
    pic_urls = []
    raw_data = json.loads(pic_get(url))['list']
    # print(raw_data)
    for i in raw_data:
        pic_title = i["title"].replace("《", "[").replace("》", "]") + '.png'
        pic_url = i["lead9x16Meidum"]
        pic_titles.append(pic_title)
        pic_urls.append(pic_url)
    return zip(pic_titles, pic_urls)


def download_pic(pic_title, pic_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
    }
    file_path = r'd:\photo'
    filename = os.path.join(file_path, pic_title)
    pic_res = requests.get(pic_url, headers=headers)
    if pic_res.status_code == 200:
        with open(filename, "wb") as f:
            f.write(pic_res.content)
            print(f"===下载 {pic_title} 完成====")
            f.close()
    else:
        print(pic_res.status_code)


def download_all_pic():
    threads = []
    data = format_data()
    for pic_title, pic_url in data:
        thread = threading.Thread(target=download_pic, args=(pic_title, pic_url))
        threads.append(thread)
        thread.start()

        for thread in threads:
            thread.join()


if __name__ == '__main__':
    for i in range(20):
        url = f"https://more.yesky.com/c/shtml/592939_25152_display_time_{i}.json?_=1701932316169"
        download_all_pic()
