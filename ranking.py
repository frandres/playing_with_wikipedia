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

    return has_verb or has_noun #and valid

# Given a list of counts of words, computes some relevats statistics and returns this in a string representation
def process_word_counts(word_counts):
#    return [' 'for counts in word_counts]
    return ['(' + str(min(counts))+' '+ str(max(counts))+')' for counts in word_counts]

'''
    Given a list of contexts, processes them by extracting all the pairwise longest subsequences, keeping a count of the words (TODO: Explain this better), and then building a frequency table.
'''
def process_contexts(contexts,minimum_freq):
    lss = {}
    for i in range(0,len(contexts)):
        for j in range(i,len(contexts)):
            glss = get_longest_subsequence(contexts[i],contexts[j])
            if glss is not None:
                t= glss[0]
                word_counts = glss[1]
                words = t.split(' ')
                if len(words)>3:
                    if t in lss.keys():
                       for i in range(0,len(word_counts)):
                            lss[t][i].append(word_counts[i][0])
                            lss[t][i].append(word_counts[i][1])
                    else: 
                        lss[t]= []
                        for i in range(0,len(word_counts)):
                            lss[t].append([word_counts[i][0],word_counts[i][1]])
    i = 0
    processed_contexts = {}
    for (expression,word_counts) in lss.items():
        freq = len(word_counts[0])/2
        if freq>=minimum_freq and is_valid_context(expression):
            words = expression.split(' ')
            context =''
            processed_word_counts = process_word_counts(word_counts)
            for i in range(0,len(words)):
                context+=processed_word_counts[i]+words[i]
            context+=processed_word_counts[len(processed_word_counts)-1]
            processed_contexts[context]=freq

    return processed_contexts

def build_ranking(contexts,minimum_freq):
    frequency = {}

    frequency = process_contexts(contexts,minimum_freq)
    '''
    for t in process_contexts(contexts): 
        if expression in frequency:
            frequency[t]+=1
        else:
            frequency[t] = 1.0
    '''
    sorted_text = []
    for (text,freq) in frequency.items():
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

    sorted_text = build_ranking(contexts,minimum_freq)

    print '-------------- RANKING ----------------'
    for i in range(0,min(100,len(sorted_text))):
        print str(i) + ' |' + sorted_text[i][1].encode('utf8') + '| with freq: '+ str(sorted_text[i][0])
        print ' '
