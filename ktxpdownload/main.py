#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import urllib2, re, sys, os

BACKWORD = "\r" if sys.platform.startswith('win') else chr(27)+'[A'

"""
A tool for download comic.
"""

class TableParser(HTMLParser):
    "Handler all tags in table."
    def __init__(self):
        HTMLParser.__init__(self)
        self._inTable = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self._inTable = True
        if self._inTable:
            self.start_tag(tag, attrs)

    def start_tag(self, tag, attrs): pass

    def handle_data(self, data):
        if self._inTable:
            self.data(data)
    
    def data(self, data): pass

    def handle_endtag(self, tag):
        if tag == 'table':
            self._inTable = False

        if self._inTable:
            self.end_tag(tag)

    def end_tag(self, tag): pass

class KtxpParser(TableParser):
    """
    A parser for parse ktxp.com html.
    """
    def __init__(self):
        TableParser.__init__(self)
        self._isATag = False
        self._downloadTd = False
        self._aText = ''
        self._links = []
        self._texts = []

    def start_tag(self, tag, attrs):
        if tag == 'td' and \
                [k for (k,v) in attrs if k == 'class' and v == 'ltext ttitle']:
            self._downloadTd = True

        if tag == 'a' and self._downloadTd:
            href = [v for (k, v) in attrs if k == 'href']
            if href:
                href = href[0]
            if re.match('^/down.+torrent$', href):
                self._links.append(href)

            if re.match('^/html.+html$', href):
                self._isATag = True
        
    def end_tag(self, tag):
        if tag == 'td':
            self._downloadTd = False
            

        if tag == 'a' and self._isATag:
            self._texts.append(self._aText)
            self._isATag = False
            self._aText = ''
            

    def data(self, data):
        text = data.strip()
        if(self._isATag and len(text) > 0):
            text = re.sub('[ \t\r\n]+', ' ', text)
            self._aText += text

    def get_result(self):
        return (self._links, self._texts)

class Result():
    def __init__(self, link, text):
        self.link = 'http://bt.ktxp.com'+link
        texts = [ t.strip() for t in re.split(u'[\[\]\u3010\u3011\u2605\u25c6]', text) if len(t.strip()) > 0 ]

        self.group = ''
        self.number = None
        for t in texts:
            if re.search(u'字幕', t):
                self.group = t
            number = re.findall(u'第?(\d+)(?:话|話|集)', t)
            if number:
                self.number = number[0]
            if self.number == None and re.match('^\d+$', t):
                self.number = t

if __name__ == '__main__':
    if(len(sys.argv) < 2):
        print """
USAGE: COMMAND KEYWORD
"""
        exit(1)
    keyword = sys.argv[1]
    url = 'http://bt.ktxp.com/search.php?keyword=%s&order=seeders' % (keyword)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    html = response.read()
    response.close()
    ktxpParser = KtxpParser()
    ktxpParser.feed(html)
    (links, texts) = ktxpParser.get_result()
    results = []
    for i in range(0, len(links)):
        r = Result(links[i], unicode(texts[i], 'utf-8'))
        if r.number != None:
            results.append(r)

    for i in range(0, 10):
        r = results[i]

        filename = "%s-%04d.torrent" % (keyword, int(r.number))
        if os.path.exists(filename):
            continue
        u = urllib2.urlopen(r.link)
        f = open(filename, 'wb')
        meta = u.info()
        fileSize = int(meta.getheaders('Content-Length')[0])

        print ''
        fileSizeDl = 0
        blockSz = 8192
        while True:
            buffer = u.read(blockSz)
            if not buffer:
                break
            
            fileSizeDl += len(buffer)
            f.write(buffer)
            print '%sDownloading: %s Bytes: %10d/%s [%3.2f%%]' % (BACKWORD, filename, fileSizeDl, fileSize, fileSizeDl * 100. / fileSize)


        f.close()
