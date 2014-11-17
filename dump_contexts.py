from extract_text import extract_all_contexts
from longest_subsequence import  get_longest_subsequence
from preprocess import preprocess_ids, preprocess_context,strip_html
import cPickle as pickle

'''
    Given a list [(text,[id0,id1])] returns a ranking of the words
'''
def dump_contexts(triplets, dump_name = 'dump.pkl'):
    contexts = []
    i = 0
    for (text,ids0,ids1) in triplets:
        i+=1
        print 'Analyzing: ' + str(i)+ ', ' +ids0[0].encode('utf8')
        # Preprocessing
    
        # Let's get rid of HTML:

        text = strip_html(text)

        # Let's now get all contexts and building a list with it.
        for t in extract_all_contexts(preprocess_ids(ids0),preprocess_ids(ids1),text,both_ways=True):
            t = preprocess_context(t)
            contexts.append(t)

    pickle.dump(contexts, open(dump_name, 'wb'), -1)

        
