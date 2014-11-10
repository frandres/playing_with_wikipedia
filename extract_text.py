import re

'''
    Given a list [(text,[id0,id1])] returns a ranking of the words
'''
def get_ranking(pairs, minimum_freq = 10):
    frequency = {}
    for (text,(ids0,ids1)) in pairs:
        for id0 in ids0:
            for id1 in ids1:
                l = extract_test(id0,id1,text,both_ways=True)
                for t in l:
                    if l in frequency:
                        frequency[l]+=1
                    else:
                        frequency[l] = 0.0

    sorted_text = []
    for (text,freq) in frequency.items():
        if freq>=minimum_freq:
            sorted_text.append(freq,text)
    sorted_text.sort()
    
    for i in range(0,10):
        print sorted_text[i]

def extract_text(id0, id1, text, window=0, both_ways = False, whole_sentence = False,eliminate_ids = False, threshold = 50):
    id0 = id0.replace('_',' ')
    id1 = id1.replace('_',' ')
    regexp = '(.*)('+id0+'.*?'+id1+').*'
    if whole_sentence:
        # regexp = '(.*)\.(.*?'+id0+'.*?'+id1+'.*?\.).*'
        window = 0
    #regexp = '.*?('+id0+'^((?!'+id0+').)*$'+id1+')(.*)'
    print ('Using a window of size ' + str(window) + ' and the regexp:') 
    print(regexp)
    
    pattern = re.compile(regexp,re.DOTALL)

    keep_looking = True
    matches = []
    text_for_reg_exps = text

    positions = []
    while keep_looking:
        m = pattern.search(text_for_reg_exps)
        if m is None:
            break
        groups = m.groups()
        keep_looking = len(groups) == 2
        match = groups[1]
        text_for_reg_exps = groups[0]
        positions.append(len(text_for_reg_exps))
        matches.append(match)

    ans = []
    for i in range(0,len(matches)):
        
        # Augment the obtained text with a window of size window or with a whole sentence.

        i0 = positions[i]-window
        i1 = positions[i]+len(matches[i])+window

        if whole_sentence:
            while i0>=0 and text[i0-1] != '.':
                i0-= 1
            while i1<len(text) and text[i1] != '.':
                i1+= 1

        matches[i] = text[i0:i1]
        # Replace the ids.
        if eliminate_ids:
            matches[i] = matches[i].replace(id0,'')
            matches[i] = matches[i].replace(id1,'')
        matches[i] = matches[i].strip()

        if len(matches[i])>threshold:
            ans.append(matches[i])

    if both_ways:
        return ans + extract_text(id1, id0, text, window=0, both_ways = both_ways, whole_sentence = whole_sentence,eliminate_ids = eliminate_ids)
    else:
        return matches
