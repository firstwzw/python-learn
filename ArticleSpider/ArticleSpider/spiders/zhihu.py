# -*- coding: utf-8 -*-
import scrapy
from ArticleSpider import settings
import re
import json
import time
from zheye import zheye
from urllib import parse


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']

    def start_requests(self):
        return [scrapy.Request(
            url="https://www.zhihu.com/#signin",
            callback=self.login,
        )]

    def login(self, response):
        text = response.text
        match_obj = re.match('.*name="_xsrf"\s+value="(.*?)"', text, re.DOTALL)
        xsrf = ""
        if match_obj:
            xsrf = match_obj.group(1)
        if xsrf:
            post_data = {
                "_xsrf": xsrf,
                "email": settings.ZHIHU_USER,
                "password": settings.ZHIHU_PASSWD,
                "captcha_type": "cn",
            }
            t = str(int(time.time() * 1000))
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login&lang=cn".format(t)
            return [scrapy.Request(
                url=captcha_url,
                callback=self.login_after_captcha,
                meta={"post_data": post_data}
            )]

    def login_after_captcha(self, response):
        with open("captcha.jpg", "wb") as f:
            f.write(response.body)
            f.close()
        z = zheye()
        pos = z.Recognize("captcha.jpg")
        tmp = []
        input_points = []
        for poss in pos:
            tmp.append(float(format(poss[1] / 2, '0.2f')))
            tmp.append(float(format(poss[0] / 2, '0.2f')))
            input_points.append(tmp)
            tmp = []
        captcha = '{"img_size": [200, 44], "input_points": %s}' % str(input_points)
        post_data = response.meta.get("post_data", {})
        post_data["captcha"] = captcha
        return [scrapy.FormRequest(
            url="https://www.zhihu.com/login/email",
            formdata=post_data,
            callback=self.check_login
        )]

    def check_login(self, response):
        text_json = json.loads(response.text)
        print(text_json)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            print("登录成功")
            for url in self.start_urls:
                yield scrapy.Request(url=url, dont_filter=True)
        else:
            print("登录失败")

    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        total = 0
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                total = total + 1
                # yield scrapy.Request(
                #     url=request_url,
                #     meta={"question_id": question_id},
                #     callback=self.parse_question
                # )
        print(total)

    def parse_question(self, response):
        pass
