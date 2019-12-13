import math

def df(term,index):
    if term in index:
        return len(set(index[term]))
    else:
        return 0

def df_ai(term, ai_df):
    return ai_df[term]

def cf(term,index):
    if term in index:
        return len(index[term])
    else:
        return 0

#term fequency of term in document
def tf(term, doc_id, index):
    if term in index:
        postings = index[term]
        frequency = 0
        for d in postings:
            if d == doc_id:
                frequency+=1

        return frequency
    else:
        return 0

def tf_weighting(term,doc_id,index):
    term_freq =tf(term,doc_id,index)
    if term_freq != 0:
        return 1 + math.log10(term_freq)
    else:
        return 0
    
def idf_weighting(term,index,doc_lengths):
    if term in index:
        docs_containing = df(term,index)
        total_docs = len(doc_lengths) - 1
        
        return math.log10(total_docs/(docs_containing + 1))
    else:
        return 0

def idf_weighting_ai(term,index,ai_df,doc_lengths):
    
    if term in ai_df:
        docs_containing = df_ai(term,ai_df)
        total_docs = 1237372
    elif term in index:
        docs_containing = df(term,ai_df)
        total_docs = len(doc_lengths) - 1
    else:
        return 0

    
    return math.log10(total_docs/(docs_containing + 1))

def tf_idf_overlap(query,doc_id, url_dict,index,doc_lengths):
    url = url_dict[doc_id]
    
    dl = doc_lengths[doc_id]
    result = 0
    for term in query:
        tf_weight= tf_weighting(term, doc_id, index)
        idf_weight = idf_weighting(term, index, doc_lengths)
        result += tf_weight*idf_weight

    return (float(result),url)

def tf_idf_overlap_ai(query,doc_id, url_dict,index,doc_lengths, ai_df):
    url = url_dict[doc_id]
    
    dl = doc_lengths[doc_id]
    result = 0
    for term in query:
        tf_weight= tf_weighting(term,doc_id,index)
        idf_weight = idf_weighting_ai(term,index, ai_df,doc_lengths)
        result += tf_weight * idf_weight

    return (float(result), url)


def bm25(query:list,doc_id, index, url_dict, doc_lengths,k=1.5,b=0.75):
    avg_dl = doc_lengths['avg_dl']
    dl = doc_lengths[doc_id]
    url = url_dict[doc_id]
    score = 0
    for term in query:
        
        idf_term = float(idf_weighting(term, index, doc_lengths))
      
        
        doc_freq = float(tf(term,doc_id,index))

        score+= float(idf_term * ((doc_freq * (k + 1)))) / (doc_freq + k * (1 - b + (b * (dl / float(avg_dl) ))))
    return (score ,url)

def bm25_ai(query:list, doc_id, index, ai_df, url_dict, doc_lengths,k=1.5,b=0.75):
    avg_dl = doc_lengths['avg_dl']
    dl = doc_lengths[doc_id]
    url = url_dict[doc_id]
    score = 0
    for term in query:

        idf_term = float(idf_weighting_ai(term, index, ai_df, doc_lengths))
        doc_freq = float(tf(term,doc_id,index))
        score += float(idf_term * ((doc_freq * (k + 1)))) / (doc_freq + k * (1 - b + (b * (dl / float(avg_dl)) )))
    return (score,url)