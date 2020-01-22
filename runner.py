import crawler
from sortedcontainers import sortedlist
import query
import os

#Parameters for running crawler/loading dictionaries
GENERATE = False

#Initialize from disk or run the crawler again
if GENERATE:
    inverted_index, doc_lengths, url_dict = crawler.runSpiderDisk()
    ai_df = crawler.get_ai_df()

else:
    inverted_index, doc_lengths, url_dict, ai_df = crawler.load_dict('inverted.json'), crawler.load_dict('doc_lengths.json'), crawler.load_dict('url_dict.json'),crawler.load_dict('ai_df.json')
    ai_df = crawler.get_ai_df()


#Example Queries, comment out if not needed

#Which departments have AI research?
q1=[
    'department ai research faculty intelligence',
    'department chair ai research learning faculty ',
    'artificial learning ai research departments faculty intelligence'
]

#Which researchers are working on AI
q2=[
    'ai researchers researching intelligence',
    'studying dr professor phd research chair intelligence ai',
    'phd ai intelligence analysis analyze lab'
]

#what AI research is being conducted at Concordia
q3=[
    'research lab technology machine ai concordia',
    'research lab technician learning ai',
    'results studying type ai concordia'
]

#user query or automated query
USER= False
#How many results to return
TOP = 50
#K and B values for bm25
K = 1.5
B = 0.75
#if Ranker not 'tf-idf' then bm25 is used
RANKER = 'tf_idf'

#Choose whether to use ai_df values
USE_AI_TERMS = False
#Augment the query with terms such as department chairs in list format
AUGMENT = None

if USER:
    while(True):
           query.do_query(USER, index=inverted_index, ai_df=ai_df, doc_lengths=doc_lengths, url_dict=url_dict, top=TOP , ranker=RANKER , k=K , b=B,use_ai_terms=USE_AI_TERMS);
else:
    for info in [q1,q2,q3]:
        for q in info:
            query.do_query(USER,index=inverted_index, ai_df=ai_df, doc_lengths=doc_lengths , url_dict=url_dict , top=TOP ,ranker=RANKER, k=K, b=B,augment=None,result_dir=os.getcwd()+'/results/',query_string=q,use_ai_terms=USE_AI_TERMS)
    
