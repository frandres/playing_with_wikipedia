from extract_text import extract_all_contexts
from longest_subsequence import  get_longest_subsequence
from preprocess import preprocess_ids, preprocess_context,strip_html
def process_contexts(contexts):
    for i in range(0,len(contexts)):
        for j in range(i,len(contexts)):
            t = get_longest_subsequence(contexts[i],contexts[j])
            yield t

def build_frequency_table(contexts,minimum_freq):
    frequency = {}

    for t in process_contexts(contexts): 
        if t in frequency:
            frequency[t]+=1
        else:
            frequency[t] = 1.0

    sorted_text = []
    for (text,freq) in frequency.items():
        if freq>=minimum_freq:
            sorted_text.append((freq,text))

    sorted_text.sort(reverse= True)

    return sorted_text

'''
    Given a list [(text,[id0,id1])] returns a ranking of the words
'''
def get_ranking(triplets, minimum_freq = 1):
    contexts = []
    i = 0
    for (text,ids0,ids1) in triplets:
        i+=1
        print 'Analyzing: ' + str(i)+ ', ' +ids0[0].encode('utf8')
    
        # Let's get rid of HTML:

        text = strip_html(text)

        # Let's now get all contexts and building a list with it.
        for t in extract_all_contexts(preprocess_ids(ids0),preprocess_ids(ids1),text,both_ways=True):
            t = preprocess_context(t)
            contexts.append(t)

    print 'Found: ' + str(len(contexts)) + ' contexts.'

    sorted_text = build_frequency_table(contexts,minimum_freq)

    print '-------------- RANKING ----------------'
    for i in range(0,min(50000,len(sorted_text))):
        print str(i) + ' |' + sorted_text[i][1].encode('utf8') + '| with freq: '+ str(sorted_text[i][0])
        print ' '
