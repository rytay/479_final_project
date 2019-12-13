import sys
import os
import time
import json
import requests
from sortedcontainers import sorteddict,sortedlist
from collections import OrderedDict
import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.http import HtmlResponse
from scrapy.exceptions import CloseSpider
import re
#Beautiful soup
from bs4 import BeautifulSoup

#Boilerpipe imports
from boilerpipe.extract import Extractor

from token_handler import tokenize


class DocItem(scrapy.Item):
    doc_id = scrapy.Field()
    tokens = scrapy.Field()
    url = scrapy.Field()
    doc_length = scrapy.Field()

#Crawler class using disk
class ResearchCrawlerDisk(CrawlSpider):
    #for doc ids and counters documents crawled
    count = 1
    #Maximum documents to parse -1 for all
    doc_limit = -1

    #Set to make sure there are no duplicate urls
    checked = set()
    rec = re.compile(r"https?://(www\.)?")
    
    custom_settings = {
        'LOG_LEVEL' : 'INFO',
        'ROBOTSTXT_OBEY': "True",
        'USER_AGENT' :'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'CONCURRENT_REQUESTS_PER_DOMAIN' : str(50),
        'RETRY_ENABLED': 'False',
        'FEED_FORMAT' : 'json',
        'FEED_URI' : 'items.json'
    }
    
    name = "research_crawler_disk"
    allowed_domains = ['concordia.ca']
    start_urls = ["http://www.concordia.ca/research"]
    #restricting some pages that link repeatedly to themselves or constantly take more than 2 minutes to parse
    rules = [Rule(LinkExtractor(allow= '/research/', deny = ["news",'scientific-monitoring.html\?','actualites.html\?','/research/polanyi/about/karl-polanyi.html','/fr/'],unique=True),callback='parse_item',follow=True)]
    
    def parse_item(self, response: HtmlResponse):
        #If document limit reached
        if self.doc_limit != -1 and self.count == self.doc_limit:
            raise Exception(CloseSpider(reason='Max pages crawled. Shutting down crawler'))
        else:
            #removes duplicate urls when two urls are replicated with https and http
            striped = self.rec.sub('',response.url)
            if striped not in self.checked:
                self.checked.add(striped)
                print('['+str(self.count)+']' "Parsing: "+response.url)
                #Boilerpipe extaction
                text = Extractor(html=response.text).getText()
                token_stream = tokenize(text)
                item = DocItem()
                item['doc_id'] = str(self.count)
                item['tokens'] = token_stream
                item['url'] = response.url
                item['doc_length'] = len(token_stream)
                self.count += 1
                yield item
            

def updateIndex(token_doc, inverted_index: sorteddict.SortedDict):
    for token in token_doc:
            term = token[0]
            docId = token[1]
            if term not in inverted_index:
                inverted_index[term] = [docId]
            else:
                temp = inverted_index[term]
                temp.append(docId)
                inverted_index[term] = temp

#extracts the concept tags and their frequencies from aitopics.org/search, can specify non ai-related terms such as 'university' or 'student' split with a space

def get_ai_df(toRemove=None):
    ai_html = requests.get('https://aitopics.org/search').text
    soup = BeautifulSoup(ai_html,'html.parser')
    concepts = soup.findAll('a',{'class':'dfilt'})
    ai_df = dict()
    for a in concepts:
        if 'concept-tagsRaw' in str(a):
            if '\xa0' in a.text:
                pair = a.text.split('\xa0')
                #get concept frequency
                freq = int(pair[1][1:-1])
                terms = tokenize(pair[0])
                for t in terms:
                    if t in ai_df:
                        t_freq = ai_df[t]
                        #keep largest frequency per term
                        if t_freq > freq:
                            ai_df[t] = t_freq
                    else:
                        ai_df[t] = freq
    #if toRemove is specified remove the terms
    if toRemove is not None and isinstance(toRemove,str):
        toRemove = set(tokenize(toRemove))
        for term in ai_df:
            if term in toRemove:
                del ai_df[term]
    #Adding 'ai' with the same term frequency as artificial intelligence
    ai_df['ai'] = ai_df['artifici']
    #Store it on disk
    with open('ai_df.json','w+') as f:
        f.write(json.dumps(ai_df,indent=4))
    return ai_df
    
def store_dicts(prefix, inverted_index,url_dict,doc_lengths):
    with open(prefix+'inverted.json',"w+") as f:
        f.write(json.dumps(inverted_index, indent=4))

    with open(prefix+'url_dict.json',"w+") as f:
        f.write(json.dumps(url_dict,indent=4))

    with open(prefix+'doc_lengths.json','w+') as f:
        f.write(json.dumps(doc_lengths,indent=4))

def items_to_dicts(items_file):
    inverted_index = sorteddict.SortedDict()
    url_dict = dict()
    doc_lengths = dict()
    with open('items.json') as data:
        items = json.load(data)
    for item in items:
        doc_id = item['doc_id']
        tokens = item['tokens']
        doc_lengths[doc_id] = len(tokens)
        #update url_dict
        url_dict[doc_id] = item['url']
        #update inverted_index
        token_doc = list(map((lambda x: (x,doc_id)), tokens))
        updateIndex(token_doc, inverted_index)
    for key in inverted_index:
        inverted_index[key] =  sorted(inverted_index[key])
    #add average_doc length
    n = 0
    for doc_id in doc_lengths:
        n += doc_lengths[doc_id]
    doc_lengths['avg_dl'] = n / len(doc_lengths)
    return inverted_index, doc_lengths, url_dict

def runSpiderDisk():
    open('items.json','w+').close()
    process = CrawlerProcess()
    process.crawl(ResearchCrawlerDisk)
    process.start()
    inverted_index, doc_lengths, url_dict = items_to_dicts('items.json')
    store_dicts('', inverted_index,url_dict,doc_lengths)
    return inverted_index, doc_lengths, url_dict
    
def load_dict(filename):
    if os.path.isfile(filename):
        with open(filename) as f:
            return json.load(f,object_pairs_hook=OrderedDict)
    else:
        return None