# -*- coding: utf-8 -*-

import cookielib
import urllib2
import yaml
import re
from bs4 import BeautifulSoup as BS

LOGIN_URL = 'https://secure.nicovideo.jp/secure/login'
MAIL_ADDRESS = 'MAIL'
PASSWORD = 'PASS'
COMMUNITY_BBS_URL = 'http://com.nicovideo.jp/bbs/co2078137'
URL = 'http://dic.nicovideo.jp/b/c/co2078137/'


class NicoBBS:
    def __init__(self, min_num=1, max_num=31):
        self.min_num = min_num
        self.max_num = max_num
        self.opener = self.create_opener()
        self.hash_key = re.search(
            "(hash_key.*?)\"",
            self.opener.open(COMMUNITY_BBS_URL).read()
        ).group(1)

    def create_opener(self):
        # cookie
        cookiejar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

        # login
        opener.open(LOGIN_URL, "mail=%s&password=%s" % (MAIL_ADDRESS, PASSWORD))
        return opener

    def get_page(self, num):
        html = self.opener.open(URL + str(num) + '-?' + self.hash_key).read()
        f = open('./raw/' + str(num).zfill(7) + '.html', 'w')
        f.write(html)
        f.close()
        soup = BS(html, 'html5lib')
        resheads = soup.findAll("dt", {"class": "reshead"})
        resbodies = soup.findAll("dd", {"class": "resbody"})
        responses = []
        index = 0

        for reshead in resheads:
            # extract
            number = reshead.find("a", {"class": "resnumhead"})["name"]
            name = reshead.find("span", {"class": "name"}).text.strip()
            date = "n/a"
            se = re.search('.*(20../.+/.+\(.+\) .+:.+:.+).*', reshead.text.strip())
            if se:
                date = se.group(1)
            hash_id = re.search('ID: (.+)', reshead.text.strip()).group(1)
            body = "".join([unicode(x) for x in resbodies[index]]).strip()
            body = self.filter_message(body)
            index += 1

            # append
            response = {
                "number": number,
                "name": name,
                "date": date,
                "hash": hash_id,
                "body": body
            }
            responses.append(response)
        return responses

    def filter_message(self, message):
        message = re.sub("<br/>", "\n", message)
        message = re.sub(
            " +<img.*?src=\"(http:\/\/dic\.nicovideo\.jp\/.*?.png).*?>", r"\1",
            message)
        message = re.sub("\n<iframe.*?/iframe>", "", message)
        message = re.sub("<.*?>", "", message)
        message = re.sub("&gt;", ">", message)
        message = re.sub("&lt;", "<", message)
        message = re.sub("&amp;", "&", message)
        message = re.sub(u"\(省略しています。全て読むにはこのリンクをクリック！\)",
                         u"(省略)", message)
        message = re.sub(u"画像をクリックして再生!!",
                         u"", message)
        message = re.sub(u"この絵を基にしています！",
                         u"", message)
        return message

    def run(self):
        for num in range(self.min_num, self.max_num, 30):
            print 'loading ' + str(num) + '\'s page now...'
            responses = self.get_page(num)
            for response in responses:
                response_body = response["body"]
                murl = re.search(".*?(http:\/\/dic\.nicovideo\.jp\/.*?.png).*?",
                                 response_body)
                if murl:
                    image_url = murl.group(1)
                    reader = self.opener.open(image_url + "?" + self.hash_key)
                    local = open("./img/" + response["number"] + ".png", 'wb')
                    local.write(reader.read())
                    local.close()
            name = str(num).zfill(7)
            f = open('./out/' + name + '.yaml', 'w')
            f.write(yaml.dump(responses))
            f.close()
            print ' done!'


if __name__ == "__main__":
    nico_bbs = NicoBBS(min_num=154501, max_num=154561)
    nico_bbs.run()
    pass
