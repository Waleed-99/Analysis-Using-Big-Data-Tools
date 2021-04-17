import pandas as pd
import gensim
import re
from gensim.parsing.preprocessing import preprocess_documents
from nltk.corpus import stopwords  
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import sys


keyword = sys.argv[1]
print(keyword)


df = pd.read_csv('alexa.com_site_info.csv', sep= ',')
df = df[ df['category'] != 'Adult/Arts' ]

text_corpus = df['all_topics_top_keywords_name_parameter_1'].fillna('').astype(str)




processed_corpus = preprocess_documents(text_corpus)
dictionary = gensim.corpora.Dictionary(processed_corpus)
bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]


tfidf = gensim.models.TfidfModel(bow_corpus, smartirs='npu')
corpus_tfidf = tfidf[bow_corpus]
num_topics = 200
lsi = gensim.models.LsiModel(corpus_tfidf, num_topics= num_topics)
index = gensim.similarities.MatrixSimilarity(lsi[corpus_tfidf])

new_doc = gensim.parsing.preprocessing.preprocess_string(keyword)
new_vec = dictionary.doc2bow(new_doc)
vec_bow_tfidf = tfidf[new_vec]
sims = index[vec_bow_tfidf]
recommended_list = []
#keyword_opportunities_breakdown_easy_to_rank_keywords = Popular keywords within this site's competitive power.
#topic buyer keywords = popular keywords in competitor website
for s in sorted(enumerate(sims), key=lambda item: -item[1]):
    temp = []
    temp.append({df['all_topics_top_keywords_name_parameter_1'].iloc[s[0]]})
    recommended_list.append(temp)
        
 

print(recommended_list[:10])



