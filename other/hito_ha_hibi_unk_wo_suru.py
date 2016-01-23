# -*- coding: utf-8 -*-

'''
うんこちゃんの過去ブログの記事HTMLをパースするプログラムです。
'''

import re

from bs4 import BeautifulSoup


def main():
    '''
    メイン関数
    '''

    html = read_file()
    soup = BeautifulSoup(html, 'lxml')
    to_wiki = ToWiki()

    area = soup.findAll(class_='entry_area')
    if len(area) > 1:
        status, entry = parse_contents(area[0])
        comment_list, name_list, date_list = parse_comments(area[1])
        write_file(to_wiki.status(status))
        write_file(to_wiki.entry(entry))
        write_file(to_wiki.comment(comment_list, name_list, date_list))
    else:
        status, entry = parse_contents(area[0])
        write_file(to_wiki.status(status))
        write_file(to_wiki.entry(entry))
    return


class ToWiki:
    def status(self, status):
        text = '#nowiki{| ' + \
            status['date'] + ' | ' + \
            status['days_of_week'] + ' | ' + \
            status['category'] + ' | ' + \
            status['time'] + ' | ' + \
            status['comment_num'] + ' | ' + \
            u'by 平成のタネマシンガン |}&br()'
        return text + u'\n'

    def entry(self, entry):
        entry = re.sub(r'<del>', '&s(){', entry)
        entry = re.sub(r'</del>', '}', entry)
        entry = re.sub(r'<span style="color:(.*?)">', r'&color(\1){', entry)
        entry = re.sub(
            r'<span style="font-size:(.*?);">', r'&sizex(\1){', entry
        )
        entry = re.sub(r'\n*</span>', '}', entry)
        entry = re.sub(
            r'<font color="(.*?)" size="(.*?)">(.*?)<\/font>',
            r'&color(\1){&sizex(\2){\3}}', entry
        )
        entry = re.sub(r'<font color="(.*?)">', r'&color(\1){', entry)
        entry = re.sub(r'\n*</font>', '}', entry)
        entry = re.sub(r'</p>', '', entry)
        entry = re.sub(r' *<p> *', u'\n', entry)
        entry = re.sub(u'申し訳ございませんが、お使いの環境ではご利用になれません。', u'', entry)
        entry = re.sub(u'リファラの送信を許可するか、ニコニコ動画上でご覧ください。', u'', entry)
        entry = re.sub(
            r'<a.*?watch\/(sm\d+?)".*?<\/a>',
            r'&nicovideo(\1)', entry
        )
        entry = re.sub(
            r'<a href="\/web\/\d+?\/(http.+?)".*?>(.*?)<\/a>',
            r'[[\2>\1]]', entry
        )
        entry = re.sub(r'<script.*?<\/script>', u'', entry)
        entry = re.sub(r'<div.*?EntryAdContainer.*?<\/div>', u'', entry)
        entry = re.sub(
            r'<embed.*?;v=([sn]m\d+?)&.*?">',
            r'&nicovideo(\1)', entry
        )
        entry = re.sub(r'<\/embed>', u'', entry)
        entry = re.sub(r'<a name="sequel">.*?<\/a>', u'\n\n', entry)

        return self.all(entry + u'\n')

    def comment(self, comments, names, dates):
        text = u'*コメント\n'
        for i in range(0, len(comments)):
            text += comments[i] + u'\n'
            text += '#right(){'
            if names[i] == '-':
                text += u'－ '
            elif names[i]:
                text += names[i] + ' '
            text += dates[i] + '}'
            text += u'\n\n'
        return self.all(text)

    def all(self, text):
        text = re.sub(r'^([>＞].*?)$', r'&nowiki(){\1}', text, flags=re.M)
        text = re.sub(r'^([・].*?)$', r'&nowiki(){\1}', text, flags=re.M)
        return text


def parse_contents(contents):
    '''
    メインコンテンツ(本文と記事情報)をパースする
    '''
    statuses = contents.find(class_='state').findAll('li')
    date_days_of_week = statuses[0].get_text().split(' ')

    status = {
        'date': date_days_of_week[0],
        'days_of_week': date_days_of_week[1],
        'category': statuses[1].get_text(),
        'time': statuses[2].get_text(),
        'comment_num': statuses[3].get_text()
    }

    entries = contents.find_all(class_='entry')
    inner = ''

    entry = entries[0].div
    if entry.img:
        entry.find('img', src=re.compile('pc.gif$')).extract()

    for content in entry.contents:
        if isinstance(entry, type(content)):
            inner += content.prettify()
        else:
            inner += content

    if len(entries) == 2:
        entry = entries[1]
        if entry.img:
            entry.find('img', src=re.compile('pc.gif$')).extract()
        for content in entry.contents:
            if isinstance(entry, type(content)):
                inner += content.prettify()
            else:
                inner += content

    inner = re.sub(u'\xa0', u'', inner)
    inner = re.sub(r'\n', u'', inner)
    inner = re.sub(r'<\/br>', u'\n', inner)
    inner = re.sub(r'<br\/>', u'\n', inner)
    inner = re.sub(r'<br>', u'\n', inner)
    inner = re.sub(r'\n +', u'\n', inner)
    inner = re.sub(r'<a name="sequel"><\/a>', u'', inner)

    return status, inner


def parse_comments(comments):
    '''
    コメントををパースする
    '''
    c_inner = comments.findAll(class_='com_desc')
    c_state = comments.findAll('dd')

    comment_list = []
    name_list = []
    date_list = []
    for i in range(0, len(c_inner)):
        comment_list.append(c_inner[i].get_text())
        state = re.sub(r'\n\n', r'', c_state[i].get_text()).split('\n')
        name_list.append(state[0])
        date_list.append(state[1])

    return comment_list, name_list, date_list


def read_file():
    '''
    ファイル読み込み
    main.txtはid=main以下のノードをそのままコピーしたテキストを想定しています。
    記事のページがない場合、月別など本文は見られる状態での
    class=entry_area以下のノードをそのままコピーしたテキストを想定しています。
    '''
    main_file = open("main.txt", "r")
    html = ''
    for row in main_file:
        html += row

    html = html.decode('utf-8')
    html = re.sub(u'\xa0', u'', html)
    html = html.encode('utf-8')
    main_file.close()
    return html


def write_file(text):
    '''
    ファイル書き込み
    面倒なところは手動で
    '''
    main_file = open("wiki.txt", "a")
    main_file.write(text.encode('utf-8'))
    main_file.close()


if __name__ == '__main__':
    main()
