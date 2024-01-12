import os.path
import threading

import requests
from lxml import etree


def request_get(url):
    """
    GET请求
    return content
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content.decode()
    except requests.RequestException:
        return None


def get_page_urls():
    """
    获取所有主题的url
    return urls
    """
    pages_url = "https://mztmzt.com/photo/"
    html = request_get(pages_url)
    el = etree.HTML(html)
    page_num = \
        el.xpath('//ul[@class="uk-pagination uk-flex-center uk-margin-remove uk-hidden@s"]/li/span/text()')[
            0].split()[
            -2]  # 得到总页数
    for url in range(int(page_num)):
        page_url = "https://mztmzt.com/photo/page/{}".format(url)
        element = etree.HTML(request_get(page_url))
        pic_urls = element.xpath('//h2[@class="uk-card-title uk-margin-small-top uk-margin-remove-bottom"]/a/@href')
        # sleep(random.choice([0.4, 0.5]))
        yield pic_urls


def save_images(url, title):
    file_path = r"d:/photo/1/"
    file_name = os.path.join(file_path, title)
    print(file_name)
    headers = {
        "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Pragma": "no-cache",
        "Referer": "https://mztmzt.com/",
        "Host": "p.meizitu.net",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0"
    }
    pic_res = requests.get(url, headers=headers)
    if pic_res.status_code == 200:
        with open(file_name, "wb") as f:
            try:
                f.write(pic_res.content)
                f.close()
            except OSError:
                print("os error")

    else:
        print(pic_res.status_code)


def download_pic():
    urls = get_page_urls()
    for url in urls:
        for i in url:
            print(i)
            element = etree.HTML(request_get(i))
            image_url = element.xpath('//figure[@class="uk-inline"]/img/@src')[0]
            title = element.xpath('//h1[@class="uk-article-title uk-text-truncate"]/text()')[0].replace('"',
                                                                                                        '').replace('|',
                                                                                                                    '') + '.jpg'
            threads = []
            thread = threading.Thread(target=save_images, args=(image_url, title))
            threads.append(thread)
            thread.start()

            for thread in threads:
                thread.join()
            # sleep(random.choice([0.4, 0.5]))


if __name__ == '__main__':
    download_pic()
