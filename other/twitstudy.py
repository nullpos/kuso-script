# -*- coding: utf-8 -*-

import re
import os.path
from bs4 import BeautifulSoup as BS


class TwitStudy:
    def __init__(self, html):
        self.full_soup = BS(html, 'lxml')

    def get_list(self):
        timeline = self.full_soup.find(id='timeline')
        lists = timeline.find_all('li')
        strs = []
        for l in lists:
            l.span.img.extract()
            ss = l.span.get_text()
            ss = re.sub('\n', '', ss, re.MULTILINE)
            ss = re.sub('^. ', '', ss)
            ss = re.sub('.$', '', ss)
            strs.append(ss)
        return strs



def write(src, name='out.txt'):
    f = open(name, 'aw')
    f.write(src.encode('utf-8') + '\n')
    f.close()

if __name__ == "__main__":
    files = os.listdir('./html/')
    for fi in files:
        print 'process %s....' % fi
        f = open('./html/' + fi)
        ts = TwitStudy(f.read())
        f.close()

        a = ts.get_list()
        for l in a:
            write(l)
        print 'done!'

