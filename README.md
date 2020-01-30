# 479_final_project
Crawl concordia.ca/research using scrapy and query support for crawled documents.
* uses SPIMI algorithm to create inverted indices of terms from concordia.ca and aitopics.org/search
* Provides tf-idf overlap and bm25 ranking for queries
* Augmentation with AI specific terms from aitopics.org/search

* w_news is pre-compiled dictionaries with news articles
* no_news is pre-compiled dictionaries without news articles
* configure and run with runner.py
