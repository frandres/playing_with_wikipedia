from extract_text import extract_all_contexts
from longest_subsequence import  get_longest_subsequence
from preprocess import preprocess_ids, preprocess_context,strip_html
from nltk import pos_tag

def is_valid_context(text):
    text = text.split(' ')
    poss = pos_tag(text)
    has_verb = False
    has_noun = False
    valid = True
    for i in range(0,len(poss)):
        pos = poss[i][1]
        if i+1< len(poss):
            next_pos = poss[i+1][1]
            valid = valid and (pos!='DT' or next_pos[0:2]=='NN')
            valid = valid and (pos[0]!='V' or next_pos[0:2]!='IN')
            valid = valid and (pos!='IN' or next_pos[0]!='V')
        has_verb = has_verb or pos[0] == 'V'
        has_noun = has_noun or pos[0:2] == 'NN'

    return has_verb and has_noun and valid
def process_contexts(contexts):
    for i in range(0,len(contexts)):
        for j in range(i,len(contexts)):
            t = get_longest_subsequence(contexts[i],contexts[j])
            words = t.split(' ')
            if len(words)>3:
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
        if freq>=minimum_freq and is_valid_context(text):
            sorted_text.append((freq,text))

    sorted_text.sort(reverse= True)

    return sorted_text

'''
    Given a list [(text,[id0,id1])] returns a ranking of the words
'''
def get_ranking(triplets, minimum_freq = 1,contexts=None):
    if contexts == None:
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
    else:
        for i in range(0,len(contexts)):
            contexts[i] = preprocess_context(contexts[i])

    sorted_text = build_frequency_table(contexts,minimum_freq)

    print '-------------- RANKING ----------------'
    for i in range(0,min(50000,len(sorted_text))):
        print str(i) + ' |' + sorted_text[i][1].encode('utf8') + '| with freq: '+ str(sorted_text[i][0])
        print ' '
