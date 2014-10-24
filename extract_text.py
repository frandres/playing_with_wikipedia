import re

def extract_text(id0, id1, text, window):
    pattern = re.compile('.*('+ id0+'.*'+id1+ ').*')
    groups =  pattern.match(text).groups()
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

text = '"The Raven" is a narrative poem by American writer Edgar Allan Poe. First published in January 1845, the poem is often noted for its musicality, stylized language, and supernatural atmosphere. It tells of a talking ravens mysterious visit to a distraught lover, tracing the mans slow fall into madness. The lover, often identified as being a student,[1][2] is lamenting the loss of his love, Lenore. Sitting on a bust of Pallas, the raven seems to further instigate his distress with its constant repetition of the word "Nevermore". The poem makes use of a number of folk and classical references.'

id0= 'The Raven'
id1= 'Edgar Allan Poe'
print(extract_text(id0,id1,text,20))
