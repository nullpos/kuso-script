# -*- coding: utf-8 -*-

import os
import re
import sys
import urllib2
import glob
import cookielib
import time
from bs4 import BeautifulSoup

LOGIN_URL = 'https://secure.nicovideo.jp/secure/login'
MAIL_ADDRESS = 'MAIL'
PASSWORD = 'PASS'


def write(text):
    f = open('a.html', 'w')
    f.write(text)
    f.close()


def get_lv_urls(path):
    if not os.path.isdir(path):
        return []
    # get all filenames
    files = [os.path.relpath(x, path)
             for x in glob.glob(os.path.join(path, '*'))]
    # replace
    for i in range(0, len(files)):
        files[i] = re.sub(r'^.*?(lv\d+?)[^\d].*?$',
                          r'http://live.nicovideo.jp/watch/\1',
                          files[i])
    files = list(set(files))
    files.sort()
    return files


def get_lv_statuses(urls):
    statuses = []
    cookiejar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    opener.open(LOGIN_URL, "mail=%s&password=%s" % (MAIL_ADDRESS, PASSWORD))
    for url in urls:
        lv = re.search(r'(lv\d+)', url).group(1)
        sys.stdout.write('processing ' + str(lv) + '...')
        html = opener.open(url).read()
        soup = BeautifulSoup(html, 'html5lib')
        info = parse_soup(soup)
        info['lv'] = lv
        statuses.append(info)
        sys.stdout.write('done!\n')
        time.sleep(1)
    return statuses


def parse_soup(soup):
    info = {}

    title_el = soup.find(class_='gate_title')
    # alive
    if title_el:
        title = title_el.span.get_text().encode('utf-8')
        main_el = soup.find(class_='textbox')

        kaijo_el = main_el.find(class_='hmf')
        kaijo_all = kaijo_el.get_text()
        start_date = re.search(r'(\d{4}\/\d{2}\/\d{2})', kaijo_all).group(1)
        start_time = re.search(u'開演\:(\d{2}\:\d{2})', kaijo_all).group(1)
        end_time = re.search(u'(\d{2}\:\d{2})に終了', kaijo_all).group(1)
        raijo = re.search(u'来場者数：(\d+)人', kaijo_all).group(1)
        comment = re.search(u'コメント数：(\d+)', kaijo_all).group(1)
        senden = re.search(u'宣伝ポイント：(\d+)', kaijo_all)
        if senden:
            senden = senden.group(1)

        detail_el = main_el.find(id='jsFollowingAdMain')
        detail_el.div.extract()
        detail = []
        for s in detail_el.strings:
            detail.append(s.encode('utf-8'))
        ts = re.search('この放送はタイムシフトに対応しておりません', detail[-2])
        if ts:
            detail.pop(-1)
            detail.pop(-1)
        detail.pop(0)
        for i in range(0, len(detail)):
            detail[i] = re.sub(r'^\n', '', detail[i])
        detail[0] = re.sub(r'^\t{4}', '', detail[0])
        detail[-1] = re.sub(r'\n\t$', '', detail[-1])
        detail = '\n'.join(detail)

        co = re.sub(r'^.*?(c[oh]\d+).*$', r'\1',
                    main_el.find(class_='shosai').a['href'])

        info = {
            'state': 'alive',
            'number': co,
            'title': title,
            'date': start_date,
            'start': start_time,
            'end': end_time,
            'raijo': raijo,
            'comment': comment,
            'detail': detail,
            'ts': True if (not ts) else False
        }
        if senden:
            info['senden'] = senden

        """
        print co, title
        print start_date, start_time, end_time
        print raijo, comment
        if senden:
            print senden
        print detail
        print '---------------'
        """
    # deleted
    else:
        info = {
            'state': 'deleted'
        }

    return info


def test_get_lv_statuses():
    urls = [
        'http://live.nicovideo.jp/watch/lv44066475',
        'http://live.nicovideo.jp/watch/lv243771362',
        'http://live.nicovideo.jp/watch/lv22398191',
        'http://live.nicovideo.jp/watch/lv195635871'
    ]
    return get_lv_statuses(urls)


def obj_to_wiki(statuses):
    wikis = []
    for info in statuses:
        if info['state'] == 'alive':
            text = u'|BGCOLOR(#fffacd):'
            text += info['date']
            text += u'|BGCOLOR(#fffacd):'
            text += info['start'] + u'～' + info['end']
            text += u'|' + info['title'].decode('utf-8')
            text += u'|' + re.sub(r'\n', '&br()', info['detail']).decode('utf-8')
            text += u'|CENTER:[[' + info['lv']
            text += u'>http://live.nicovideo.jp/watch/' + info['lv'] + u']]'
            if not info['ts']:
                text += u' (TS非対応)'
            text += u'|CENTER:|'
            wikis.append(text)
        else:
            print 'cannot get live info:', info['lv']
    return wikis


def main():
    lv_urls = get_lv_urls('Y:\\file\\movie\\broadcast\\niconico\\yocchan')
    lv_statuses = get_lv_statuses(lv_urls)
    # lv_statuses = test_get_lv_statuses()
    statuses = obj_to_wiki(lv_statuses)
    f = open('wiki.txt', 'w')
    for s in statuses:
        f.write(s.encode('utf-8'))
        f.write('\n')
        print s.encode('utf-8')
    f.close()
    # print lv_urls

if __name__ == '__main__':
    main()
