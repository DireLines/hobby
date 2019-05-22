
import sys
import requests
from bs4 import BeautifulSoup as bs
from html.parser import HTMLParser

tags = {}
alldata = []
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        # print(tag.strip())
        if tag not in tags:
            tags[tag] = 1
        else:
            tags[tag] += 1

    # def handle_endtag(self, tag):
    #     # print("/", tag.strip(),sep='')

    def handle_data(self, data):
        alldata.append(data)

parser = MyHTMLParser()

def findSubList(sl,l):
    results=[]
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            results.append((ind,ind+sll-1))
    return results

def getHTML(url):
    return requests.get(url).text

def getHrefs(url):
    html = getHTML(url)
    parser.feed(html)
    for tag in sorted(tags):
        print('\t',tags[tag],tag,"tags")
    tags.clear()
    alldata.clear()
    # print('\t',len(html),'characters')
    hrefSpots = findSubList("href=\"",html)
    hrefs = []
    for spot in hrefSpots:
        begin_quote_index = spot[1]
        end_quote_index = html.index("\"",begin_quote_index+1)
        hrefText = html[begin_quote_index+1:end_quote_index]
        hrefs.append(hrefText)
    # print('\t',len(hrefs),'hrefs')
    return hrefs

def getLinks(url):
    hrefs = getHrefs(url)
    thirdslash = url.find('/',url.find('/',url.find('/')+1)+1)
    url_base = url
    if(thirdslash != -1):
        url_base = url[0:thirdslash]
    links = []
    for hrefText in hrefs:
        linkText = hrefText
        if(len(hrefText) == 0):
            continue
        if(hrefText[0] == '/'):
            if(len(hrefText) > 1 and hrefText[1]=='/'):
                linkText = "https:" + hrefText
            else:
                linkText = url_base + hrefText
        if(linkText[0:4] == "http"):
            if(linkText in links):
                continue
            links.append(linkText)
        # else:
            # print('\t\t',hrefText,"rejected")
    return links


url = sys.argv[1]
links = getLinks(url)
for i in range(len(links)):
    link = links[i]
    print(i+1,'/',len(links),':',link)
    print('\t',len(getLinks(link)),'links')
print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")