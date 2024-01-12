import json
from datetime import datetime

import requests


class YouDao:
    def __init__(self, cookie, key):
        self.cookie = cookie
        self.key = key
        self.checkin_url = "https://note.youdao.com/yws/mapi/user?method=checkin"
        self.ad_url = "https://note.youdao.com/yws/mapi/user?method=reward&businessType=ADVERT_VIDEO&businessCode=150&IDFA=00000000-0000-0000-0000-000000000000&_appName=ynote&_appuser=e5840b6621ca4bb4b3f8422e4766d0ea&_cityCode=511500&_cityName=%25E5%25AE%259C%25E5%25AE%25BE&_device=iPhone13%2C3&_firstTime=2023-11-27%252015%3A02%3A57&_idfa=00000000-0000-0000-0000-000000000000&_imei=521729d6b10a1bc0261bef6f2ebe8d64b0bb35cd&_launch=4&_manufacturer=apple&_network=wifi&_operator=M&_platform=ios&_screenHeight=844&_screenWidth=390&_system=iOS&_systemVersion=17.1.1&_vendor=AppStore&_version=7.4.320&client_ver=7.4.320&device_id=iPhone13%2C3-5307F458-E5E0-4551-9151-D2FBE58E12F3&device_model=iPhone&device_name=iPhone&device_type=iPhone&imei=5307F458-E5E0-4551-9151-D2FBE58E12F3&keyfrom=note.7.4.320.iPhone&level=user&login=phone&mid=17.1.1&model=iPhone13%252C3&net=wifi&os=iOS&os_ver=17.1.1&phoneVersion=iPhone&sec=v1&sev=j1&vendor=AppStore"
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-Hans-CN;q=1, en-CN;q=0.9",
            "Cookie": self.cookie,
            "User-Agent": "YNote/7.4.320 (iPhone; iOS 17.1.1; Scale/3.00)",
            "Host": "note.youdao.com",
            "Connection": "keep-alive",
        }

    def send_msg(self,ti, msg):
        """
        server酱推送
        传入title，msg
        """
        url = f'https://sctapi.ftqq.com/{self.key}.send'
        title = ti
        data = {
            'title': title,
            'desp': msg
        }
        req = requests.post(url, data=data)
        print(req.status_code)

    def youdao_post(self, url):
        # 有道的post请求
        return requests.post(url=url, headers=self.headers)

    def watch_ad(self):
        # 看视频得空间
        res = self.youdao_post(self.ad_url)
        return res.text

    def sign(self):
        # 签到
        ad_res = self.watch_ad()
        response = self.youdao_post(self.checkin_url)
        if response.status_code == 200:
            data = json.loads(response.text)
            total = data["total"] / 1048576  # 总空间
            sign_time = data["time"] / 1000  # 签到时间
            space = data["space"] / 1048576  # 获得空间
            format_time = datetime.fromtimestamp(sign_time).strftime('%Y-%m-%d %H:%M:%S')
            print(data,ad_res)
            print("签到成功,这次签到获得:{}M,总空间:{}M，签到时间:{}".format(space, total, format_time))
            self.send_msg(ti="签到成功",msg="这次签到获得:{}M,总空间:{}M，签到时间:{}".format(space, total, format_time))
        else:
            msg = response.status_code, response.json()["message"]
            print("网页状态", msg)
            self.send_msg(ti="签到失败",msg=msg)
        response.close()


if __name__ == '__main__':
    cookie = 'NTES_PASSPORTYNOTE_FORCE=true; YNOTE_SESS=v2|213qbdY3qVOW0fTFPLkG0l5kMwB64PK0Ul64pFOLeu0QZhfO5nMlA0pFnMw4hMQFRlf0Lk5h4OY0k5RLOA6Mgu0kA0MQZ6LOG0; YNOTE_LOGIN=5||1702107554048'  # 填入cookie https://note.youdao.com/
    key = "SCT120690TsKsdjxbUPNEg14IgtvBIPIhw"  # server酱的sendkey
    YouDao(cookie, key).sign()
