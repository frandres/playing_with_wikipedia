from wikitools import wiki, api
import pprint
from extract_text import extract_text
from unidecode import unidecode

def readCategoryToList(filename):
    lines = [line.strip() for line in open(filename)][2:]
    new_list = []
    for line in lines:
        line = line.rsplit(",", 5)
        new_list.append(line[0].replace("\"", ""))

    return new_list

def readCategory(infile):
    lines = [line.strip() for line in open(infile)]
    return lines[1:]

def toDictionary(list):
    pageDict = dict()
    for line in list:
        line = line.rsplit(",", 5)
        pageDict[line[0].replace("\"", "")] = line[1]

    return pageDict

def outLinks(pageDict):
    site = wiki.Wiki("http://en.wikipedia.org/w/api.php")
    main_dict = dict()
    i = 0
    for key in pageDict:
        if i>30:
            break

        print "QUERY "+str(i)+": "+key
        params = {'action':'query',
            'prop':'links',
            'format':'json',
            'plnamespace':'0',
            'pllimit':'500',
            'plcontinue':'||',
            'titles':key}
        req = api.APIRequest(site, params)
        res = req.query(querycontinue=False)
        x = res['query']['pages'].keys()[0]
        list_of_dicts = res['query']['pages'][x]['links']

        title_list = []
        for elem in list_of_dicts:
            title_list.append(elem['title'])
        main_dict[key] = title_list
        i+=1

    #for key in main_dict:
    #    print key+":"+str(main_dict[key])
    return main_dict

def findPairs(cat1dict, cat2list):
    tuple_list = []
    for key in cat1dict:
        list_of_pages = cat1dict[key]
        for page in list_of_pages:
            if page in cat2list:
                tuple_list.append((key,page))
    return tuple_list

def find_redirects(p1):
    site = wiki.Wiki("http://en.wikipedia.org/w/api.php")

    print "QUERY "+p1+" redirects"
    params = {'action':'query',
        'prop':'redirects',
        'format':'json',
        'rdprop':'title',
        'rdnamespace':'0',
        'rdlimit':'20',
        'titles':p1}
    req = api.APIRequest(site, params)
    res = req.query(querycontinue=False)
    x = res['query']['pages'].keys()[0]
    dict_of_redirects = res['query']['pages'][x]['redirects']

    list_of_redirects = []
    for elem in dict_of_redirects:
        list_of_redirects.append(elem['title'])

    return list_of_redirects

def find_text((p1,p2), l1, l2):
    site = wiki.Wiki("http://en.wikipedia.org/w/api.php")
    params = {'action':'query',
        'prop':'extracts',
        'format':'json',
        'exlimit':'1',
        'export':'',
        'titles':p1}
    req = api.APIRequest(site, params)
    res = req.query(querycontinue=False)
    text = res['query']['export']['*']

    #for e in l1:
    #    text = text.replace(e,p1)

    #for e in l2:
    #    text = text.replace(e,p2)

    #print text
    return text

######################################################################
# START
######################################################################
category1 = "List_of_poems_depth_100.txt"   #poems
category2 = "List_of_poets_depth_100.txt"   #poets

#cat1_dict = toDictionary(readCategory(category1))
#cat2_list = readCategoryToList(category2)

#main_dict = outLinks(cat1_dict)
#pair_list = findPairs(main_dict,cat2_list)
list_of_redirects1 = find_redirects('Il_Canzoniere')
list_of_redirects2 = find_redirects('Aeneid')

text = find_text(('Il_Canzoniere','Aeneid'), list_of_redirects1, list_of_redirects2)
print text
print(extract_text('Il_Canzoniere','Petrarch',text,10))




# al extraer el texto, reemplazar todas las ocurrencias de los redirects
# por un solo identificador
#francesco petrarca / petrarca