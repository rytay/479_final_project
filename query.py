import json
from sortedcontainers import sorteddict,sortedlist
import sys
import os
import math
from token_handler import tokenize
import ast
import calculations
from datetime import datetime


def do_query(user, index, ai_df, doc_lengths , url_dict , top:int ,ranker='tf_idf', k=1.5, b=0.5,augment=None,result_dir=os.getcwd()+'/results/',query_string='',use_ai_terms=False):
    #Checking if results directory exists, otherwise create it
    if 'results' not in os.listdir(os.getcwd()):
        os.mkdir('results')
    prefix = ''
    if use_ai_terms:
        prefix = 'AI_'

    q = []
    if user:
        query_string = ''
        prompt = input('Enter "no" to stop query, otherwise enter any string to continue: ')
        if prompt == 'no':
            print('Querying terminated. System exiting...')
            sys.exit()
        else:
            query_string = input("Enter query (spaces between terms) : ")
    q = tokenize(query_string)
    if augment is not None:
        q.extend(augment)
    print(q)
    #Process only documents that have at least one query term in them
    to_process = set()
    for term in q:
        if term in index:
            to_process = to_process.union(set(index[term]))
            
    if len(to_process) != 0:
        ranked = []
        if ranker == 'tf_idf':
            k = 'none'
            b = 'none'
            for doc_id in url_dict:
                if use_ai_terms:
                    ranked.append(calculations.tf_idf_overlap_ai(q,doc_id, url_dict,index,doc_lengths, ai_df))
                else:
                    ranked.append(calculations.tf_idf_overlap(q,doc_id,url_dict,index,doc_lengths))
        else:
            for doc_id in url_dict:
                if use_ai_terms:
                    ranked.append(calculations.bm25_ai(q,doc_id,index,ai_df,url_dict,doc_lengths,k,b))
                else:
                    ranked.append(calculations.bm25(q,doc_id,index,url_dict,doc_lengths,k,b))

        #Create final result list, sort in decreasing order and display/log result
        ranked.sort(key=lambda x: x[0],reverse=True)
        log = 'Results for Query: \'' + query_string +'\'\n'
        log += 'Using ai_df : '+str(use_ai_terms)+'\n'
        log +='('+ranker+', url)\n'
        log += ('==================\n')
        if top > len(ranked) - 1:
            top = len(ranked)

        for result in ranked[0:top]:
            log+=str(result)+'\n'
    else:
        log = 'No results for query: \''+ query_string + '\''

    with open(result_dir+prefix+'top_'+str(top)+'_ranker_'+ranker+'_k='+str(k)+'_b='+'_'+str(b)+'_'+str(datetime.now())+'.txt','w+') as f:
        f.write(log)
    print(log)