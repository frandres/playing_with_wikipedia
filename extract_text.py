import re
from nltk.tokenize import sent_tokenize
import itertools
'''
    Given a list [(text,[id0,id1])] returns a ranking of the words
'''
def get_ranking(pairs, minimum_freq = 2):
    frequency = {}
    for (text,ids0,ids1) in pairs:
        for t in extract_all_contexts(ids0,ids1,text,both_ways=True):
            if t in frequency:
                frequency[t]+=1
            else:
                frequency[t] = 1.0

    sorted_text = []
    print 'Freqs'
    for (text,freq) in frequency.items():
        if freq>=minimum_freq:
            sorted_text.append((freq,text))

    sorted_text.sort(reverse= True)

    print '-------------- RANKING ----------------'
    for i in range(0,min(10,len(sorted_text))):
        print str(i) + ' |' + str(sorted_text[i][1]) + '| with freq: '+ str(sorted_text[i][0])
        print ' '

def reg_exps(ids0,ids1,both_ways):
    if both_ways:
        return itertools.chain(reg_exps_iter(ids0,ids1),reg_exps_iter(ids1,ids0))
    else:
        return reg_exps_iter(ids0,ids1)

def reg_exps_iter(ids0,ids1):
    regexps = []
    for id0 in ids0:
        for id1 in ids1:
            yield (re.compile(id0+'.*?'+id1),re.compile('.*'+id0+'(.*)'+id1))

def extract_closest_context(regexp,string):
    match = re.search(regexp,string)
    if match:
        return match.group(1)
    else:
        raise('Closest context not found')

def extract_context(id0,id1,text,both_ways=False):
    # Let's find all occurrences of pairs (id0<WHATEVER>id1)
    f_regexp = re.compile(id0+'.*?'+id1)
    new_c = re.findall(f_regexp, text, flags=0)

    # And make sure we use the smallest one
    c_regexp = re.compile('.*'+id0+'(.*)'+id1)
    if both_ways:
        return [extract_closest_context(c_regexp,p) for p in new_c] +  extract_context(id1,id0,text)
    else:
        return [extract_closest_context(c_regexp,p) for p in new_c]

def extract_all_contexts(ids0, ids1, text, both_ways = False):

    # Initialize the answer

    contexts = []

    # Segment the text into sentences:
    sentences = sent_tokenize(text)

    # Let's compile all the regexps we need:

    for sentence in sentences:
        for id0 in ids0:
            for id1 in ids1:
                for x in extract_context(id0,id1,text,both_ways):
                    yield x

#print (extract_text(['a','c'],['b','d'],'a lalala c b d c a lalalala b a a b b. ', both_ways = True))
for x in extract_all_contexts(['a','c'],['b','d'],'ac tttttt d ac tttt b', both_ways = True):
    print x










