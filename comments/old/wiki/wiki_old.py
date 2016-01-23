# -*- coding: utf-8 -*-

import re
import urllib2
import validators
import yaml
import os.path
from bs4 import BeautifulSoup as BS
import datetime


class Wiki:
    def __init__(self, src):
        name = re.sub(r'^.*\/(.*?)\/pages\/(.*?)\.html$',
                      r'\1-\2', src)
        name = re.sub('\n', '', name)
        name = './raw/' + name + '.html'
        if validators.url(src):
            if os.path.exists(name):
                f = open(name)
                html = f.read()
                f.close()
            else:
                try:
                    html = urllib2.urlopen(src).read()
                    write(html, name)
                except Exception, e:
                    raise e
        else:
            html = src

        self.full_soup = BS(html, 'html5lib')

    def replace_plugins(self, wikibody):
        pass

    def get_object(self):
        if hasattr(self, 'comments'):
            return self.comments
        if not self.full_soup.id == 'wikibody':
            wikibody = self.full_soup.find(id='wikibody')
        else:
            wikibody = self.full_soup

        comments_ul = wikibody.find_all('ul')
        if len(comments_ul) > 1:
            raise TooManyTagsError('wikibody has too many ul tags.'
                                   'Please use with edited html src.')
        comments_li = comments_ul[0].find_all('li')
        for element in comments_li:
            if not element.name == 'li':
                raise NotOnlyLITagsError('ul tag has "not li" tags.'
                                         'Please use with edited html src.')

        self.comments = []
        for element in comments_li:
            span = element.find_all('span')
            if span:
                tmp_time = span[-1].extract().get_text().encode('utf-8')
                if self.is_valid_time(self.trim_time(tmp_time)):
                    time = self.trim_time(tmp_time)
                else:
                    time = self.add_a_second(time)
            else:
                time = self.add_a_second(time)
            comment = self.trim_comment(
                '\n'.join(element.stripped_strings).encode('utf-8'))
            self.comments.append({'comment': comment, 'time': time})
        return self.comments

    def is_valid_time(self, time):
        try:
            datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        except Exception:
            return False
        else:
            return True

    def trim_comment(self, text):
        return re.sub('[- ]+$', '', text)

    def trim_time(self, text):
        return re.sub('(^[ \n]+)|([ \n]+$)', '', text)

    def add_a_second(self, time):
        new_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        new_time += datetime.timedelta(seconds=1)
        return new_time.strftime('%Y-%m-%d %H:%M:%S')


class TooManyTagsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NotOnlyLITagsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def write(src, name='test.txt'):
    f = open(name, 'w')
    f.write(src)
    f.close()


def read():
    f = open('wiki.html', 'r')
    html = f.read().decode('utf-8')
    f.close()
    return html

if __name__ == "__main__":
    f = open('wiki_url.txt', 'r')
    for line in f:
        print re.sub(r'\n', '', line), '...'
        try:
            wiki = Wiki(line)
            comments = wiki.get_object()
            name = re.sub(r'^.*\/(.*?)\/pages\/(.*?)\.html$',
                          r'\1-\2', line)
            name = re.sub('\n', '', name)
            name = './out/' + name + '.yaml'
            write(yaml.dump(comments), name)
        except Exception, e:
            print '\n\tfailed: ', e
            continue
        print 'complete!'
    f.close()
    '''
    if len(sys.argv) > 1:
        wiki = Wiki(sys.argv[1])
        comments = wiki.get_object()
        name = re.sub(r'^.*\/(.*?)\/pages\/(.*?)\.html$', r'out/\1-\2.yaml',
                      sys.argv[1])
        write(yaml.dump(comments), name)
    else:
        wiki = Wiki(read())
        # wiki = Wiki('http://www9.atwiki.jp/unkochan-comment/pages/51.html')
        comments = wiki.get_object()
        f = open('comment.txt', 'w')
        for comment in comments:
            f.write('comment:' + comment['comment'] + '\n')
            f.write('time:' + comment['time'] + '\n')
        f.close()
    '''
    pass
