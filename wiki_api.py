from wikitools import wiki, api
import xml.etree.ElementTree as ET
import pprint


#Receives a filename string as input and will return a list with each of the lines.
def read_category_to_list(filename):
    lines = [line.strip() for line in open(filename)]
    new_list = []
    for line in lines:
        line = line.rsplit(",", 5)
        new_list.append(unicode(line[0].replace("\"", ""), "utf8"))

    return new_list


##Yield successive n-sized chunks from l.
def chunks(l, n):
    if n < 1:
        n = 1
    return [l[i:i + n] for i in range(0, len(l), n)]


#Will generate strings joined by '|' according to the window size, and will return
#a list of these query strings.
def generate_query_strings(page_list, window_size):
    query_strings = chunks(page_list, window_size)

    for i in range(0, len(query_strings)):
        query_strings[i] = "|".join(query_strings[i])

    return query_strings


#Will create a dictionary with keys being each of the pages in the category,
#and the values being all of the output links for that page. Receives as parameter
#a list of pages for a certain category, and a window size that will define
#how many pages to process per query. CURRENTLY WORKS ONLY FOR WINDOW SIZE 1.
def find_outlinks(page_list, window_size):
    site = wiki.Wiki("http://en.wikipedia.org/w/api.php")
    page_link_dict = dict()

    #List of query strings, where each element in the list is a string joined
    #by '|' containing the number of pages specified by window size.
    query_strings = generate_query_strings(page_list, window_size)
    print query_strings

    #Now executing each of the queries in query strings.
    i=1
    for query in query_strings:
        params = {'action' : 'query',
            'prop' : 'links',
            'format' : 'json',
            'plnamespace' : '0',
            'pllimit':'500',
            'titles' : query}

        #Will put a request to the MediaWiki api with the parameters
        #specified above
        request = api.APIRequest(site, params)

        #Result of the query in JSON format
        query_result = request.query(querycontinue=True)

        #Retrieve list of page IDs from the query result
        #THIS HAS TO CHANGE WHEN WE GENERALIZE FOR A BIGGER WINDOW SIZE.
        page_ids = query_result['query']['pages'].keys()[0]

        # Dictionary of the form:
        #   {
        #   "ns": 0,
        #   "title": "Metaphysics"
        #   }
        # Contains all the links (in the pllimit) and the property ns (not used).
        raw_title_list = query_result['query']['pages'][page_ids]['links']

        # Save all the page titles into a list by scrolling on the previous dictionary.
        title_list = []
        for elem in raw_title_list:
            title_list.append(elem['title'].replace(" ", "_"))

        # Save all the output links in the dictionary for the current query.
        page_link_dict[query] = title_list

        print("Outlink query "+str(i)+" of "+str(len(query_strings))+" complete.")
        i += 1

    return page_link_dict


#Will receive two lists of categories and will find which elements of the second
#are in the first list, and will create a list of tuples.
def find_pairs(outlinks_dict_of_category1, category2_list):
    tuple_list = []

    for page_id in outlinks_dict_of_category1:
        list_of_pages = outlinks_dict_of_category1[page_id]

        for page in list_of_pages:
            # TODO : FIX UNICODE ISSUE
            if page in category2_list:
                tuple_list.append((page_id, page))

    return tuple_list


# Receives the list of pairs for two categories and returns a
# dictionary with category 1 pages as keys and category 2 pages
# as values
def group_pairs_into_dict(pair_list):
    key_set_dict = {}
    for pair in pair_list:
        if pair[0] not in key_set_dict:
            key_set_dict[pair[0]] = set()
        key_set_dict[pair[0]].add(pair[1])

    #for key in key_set_dict:
    #   print str(key)+","+str(key_set_dict[key])

    return key_set_dict

#Builds a list of triple (text, key, list).
#Text is the text in the category 1 pages (of the key)
#Key are the category 1 pages
#List is  the list of pages in category 2 that appear in the category 1 page
def tkl_triple(pair_list):
    # Dictionary with category 1 pages as keys and category 2 pages
    # as values
    key_set_dict = group_pairs_into_dict(pair_list)

    # List that concatenates the result of each query and makes the tkl triple
    tkl_list = []
    i = 1
    # Execute a query for each page in category 1 (first page of the tuple of pair_list)
    for page_key in key_set_dict.keys():
        site = wiki.Wiki("http://en.wikipedia.org/w/api.php")
        params = {'action': 'query',
            'prop': 'extracts',
            'format': 'json',
            'exlimit': '1',
            'export':'',
            'titles': page_key}
        req = api.APIRequest(site, params)
        res = req.query(querycontinue=False)
        #pprint.pprint(res)
        text = res['query']['export']['*']
        tkl_list.append([text, [page_key], list(key_set_dict[page_key])])

        print("Text query "+str(i)+" of "+str(len(key_set_dict.keys()))+" complete.")
        i += 1

    return tkl_list

#Builds a list of triple (text, key, list).
#Same as above method, retrieves the query result in XML and produces cleaner text.
def tkl_triple_xml(pair_list):
    # Dictionary with category 1 pages as keys and category 2 pages
    # as values
    key_set_dict = group_pairs_into_dict(pair_list)

    # List that concatenates the result of each query and makes the tkl triple
    tkl_list = []
    i = 1
    # Execute a query for each page in category 1 (first page of the tuple of pair_list)
    for page_key in key_set_dict.keys():
        site = wiki.Wiki("http://en.wikipedia.org/w/api.php")
        params = {'action': 'query',
            'prop': 'extracts',
            'format': 'xml',
            'titles': page_key}
        req = api.APIRequest(site, params)
        res = req.query(querycontinue=False)
        #pprint.pprint(res)
        key = res['query']['pages'].keys()[0]
        text = res['query']['pages'][key]['extract']

        tkl_list.append([text, [page_key], list(key_set_dict[page_key])])

        print("Text query "+str(i)+" of "+str(len(key_set_dict.keys()))+" complete.")
        i += 1

    return tkl_list

def main():
    #Input files for the categories generated with Catscan2
    category1 = "List_of_poems_depth_100.txt"
    category2 = "List_of_poets_depth_100.txt"

    #Reads the category text files and generates a list with each line.
    cat1_page_list = read_category_to_list(category1)
    cat2_page_list = read_category_to_list(category2)

    #Will create a dictionary with keys being each of the pages in the category,
    #and the values being all of the output links for that page. Receives as parameter
    #a list of pages for a certain category, and a window size that will define
    #how many pages to process per query.
    outlinks_dict_of_category1 = find_outlinks([u'Il_Canzoniere',u'The_Raven', u'The_Canterbury_Tales'], 1)
    #outlinks_dict_of_category1 = find_outlinks(cat1_page_list, 1)
    print "Outlinks of category1: "+str(outlinks_dict_of_category1)

    #Will create a list of tuples. Each tuple is a pair of (page_in_category1, page_in_category2).
    #The tuple exists in the list if page_in_category2 is in the output links of page_in_category1.
    pair_list = find_pairs(outlinks_dict_of_category1, cat2_page_list)
    print "Pair list: "+str(pair_list)

    #Builds a list of triple (text, key, list).
    #Text is the text in the category 1 pages (of the key)
    #Key are the category 1 pages
    #List is  the list of pages in category 2 that appear in the category 1 page
    # RAW TEXT TRIPLET
    # tkl_triple_list = tkl_triple(pair_list)
    # CLEAN TRIPLET
    tkl_triple_list = tkl_triple_xml(pair_list)

    print "*******************************"
    for t in tkl_triple_list:
        print "*******************************"
        print t
        print "*******************************"
    print "*******************************"

main()