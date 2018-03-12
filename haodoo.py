from bs4 import BeautifulSoup
import requests
import os
import re
import sys

baseurl = "http://www.haodoo.net/"

class haodoo:
    
    def __init__(self, url, root):
        self.url = url
        self.root = root

    def gethtml(self, url):
        print("gethtml("+url+")")
        headers = { 'user-agent': 'my-app/0.0.1' }
        r = requests.get(url, headers = headers)
        r.encoding = 'UTF-8'
        page = r.text
        return page
    
    def getfile(self, url, fname):
        print("getfile("+url+")")
        print("file name " + fname)
        if not fname or os.path.exists(fname):
            print("fname error or exists")
            return
        try:
            headers = { 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36' }
            r = requests.get(url, headers = headers, stream = True)
            if r.status_code != 200:
                print("error in get file")
                exit()
            print("file length " + r.headers['content-length'])
            with open(fname, 'wb') as f:
                for chunk in r.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
        except:
            # delete file
            print("unknown exception!")
            if os.path.exists(fname):
                os.remove(fname);
            exit()
        return

    def getsuburl(self):
        page = self.gethtml(self.url)
        p = re.compile("<span( )+class( )*=( )*a92.+</span>", re.DOTALL)
        m = p.search(page)
        suburls = []
        if m:
            text = m.group(0)
            for sm in re.finditer('"(.+)"', text):
                suburls.append(baseurl + sm.group(1))
        return suburls 
    
    def getfiles(self, url):
        print("getfiles("+url+")")
        page = self.gethtml(url)
        p = re.compile('<div[ class="]+a03.*?</div>', re.DOTALL)
        m = p.search(page)
        subitems = []
        if m:
            text = m.group(0)
            for sm in re.finditer('href.+?"(.+?)" *>(.+?)</a>', text):
                subitems.append(baseurl + sm.group(1))
        return subitems

    def downloadmobi(self, url):
        print("downloadmobi("+url+")")
        page = self.gethtml(url)
        m = re.search('SetTitle\(".*[《【](.+?)[》】]"\)', page)
        if not m:
            return
        pagename = m.group(1)
        pagename.strip()
        for m in re.finditer("DownloadMobi\('(.+?)'\)", page):
            furl = "{0}?M=d&P={1}.mobi".format(baseurl, m.group(1))
            fname = m.group(1)
            if fname[-1].isalpha():
                fname = pagename + fname[-1]
            else:
                fname = pagename
            fpath = self.root + fname + ".mobi"
            self.getfile(furl, fpath)


def main(topic, path):
   
    url = "http://www.haodoo.net/?M=hd&P=" + topic
    hd = haodoo(url, path)
    if not os.path.exists(path):
        os.makedirs(path)
    
    urls = hd.getsuburl()
    for url in urls:
        items = hd.getfiles(url)
        for item in items:
            try:
                hd.downloadmobi(item)
            except:
                print("error " + item)

if __name__ == "__main__":
    topic = sys.argv[1]
    path = sys.argv[2]
    topic.strip()
    path.strip()
    if path[-1] != '/' and path[-1] != '\\':
        path = path + '/'
    path = path + topic + '/'
    main(topic, path)
