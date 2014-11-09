import re

def extract_text(id0, id1, text, window=0, both_ways = False):
    id0 = id0.replace('_',' ')
    id0 = 'Canzoniere'
    id1 = id1.replace('_',' ')
    regexp = '(.*)('+id0+'.*?'+id1+').*'
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

    for i in range(0,len(matches)):
        
        # Augment the obtained text with a window of size window
        matches[i] = text[positions[i]-window:positions[i]+len(matches[i])+window]
        # Replace the ids.

        matches[i] = matches[i].replace(id0,'')
        matches[i] = matches[i].replace(id1,'')
 
    if both_ways:
        return matches + extract_text(id1, id0, text, window)
    else:
        return matches
