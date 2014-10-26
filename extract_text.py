import re

def extract_text(id0, id1, text, window=0):
    id0 = id0.replace('_',' ')
    id1 = id1.replace('_',' ')
    regexp = '.*('+id0+'.*?'+id1+').*'
    print(regexp)
    pattern = re.compile(regexp,re.DOTALL)
    m = pattern.match(text)
    if m is None or len(m.groups()) ==0:
        return 'Pattern not found'
    groups = m.groups()
    # We work with the first occurence of the id0+ id1 relation.
    # We assume that it is the most relevant one.
    t = groups[0]

    '''
    The following lines of code augment the obtained text with a window of size window_size
    Note that this is an exploratory version: a more optimal version would extract this
    in the regular expressions.
    '''
    lt = len(t)
    for i in range(0,len(text)-lt):
        if text[i:i+lt] == t:
            t = text[max(0,i-window):min(len(text),i+lt+window)]
    t = t.replace(id0,'')
    t = t.replace(id1,'')
    return t
