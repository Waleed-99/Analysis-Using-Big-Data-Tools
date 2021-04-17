#imports
from keybert import KeyBERT
from googleResults import googleResult
import pandas as pd 
import sys



# Only need to run this once, the rest of requests will use the same session.
pytrend = googleResult()

keyword = sys.argv[1]

keyword_list  = []
keyword_list.append(keyword)
# Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
pytrend.build_payload(kw_list=keyword_list)


# Get Google Keyword Suggestions
suggestions_dict = pytrend.related_queries()


list_value = []


for _, search_query in suggestions_dict.items():
    list_value.append(search_query['top'])

k = []

listToStr = ' '.join([str(elem) for elem in list_value]) 
result = ''.join([i for i in listToStr if not i.isdigit()])
suggestions=result.split()[2:]
doc = '\n'.join(map(str, suggestions))

model = KeyBERT('distilbert-base-nli-mean-tokens')
keywords = model.extract_keywords(doc)
model_solution = model.extract_keywords(doc, keyphrase_ngram_range=(1, 1), stop_words='english', top_n=51)


suggested_keywords = []
relevancy = []

for i in model_solution:
    suggested_keywords.append(i[0])
    relevancy.append(i[1])
    print(i[0])
  
 

dict = {'Suggested Keywords': suggested_keywords, 'Relevancy': relevancy}   
       
df = pd.DataFrame(dict)  



#saving the dataframe  
df.to_csv('SEO_SUGGESTIONS.csv') 