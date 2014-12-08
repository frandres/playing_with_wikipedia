from wikitools import wiki, api
import pprint
from extract_text import get_ranking
import sys
import cPickle as pickle


# Class that allows redirecting all prints and system messages to a file, and printing to the console at the same time.
class Redirect(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)


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
    #print query_strings

    #Now executing each of the queries in query strings.
    i = 1
    skipped = 0
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

        try:
            # Contains all the links (in the pllimit) and the property ns (not used).
            raw_title_list = query_result['query']['pages'][page_ids]['links']

            # Save all the page titles into a list by scrolling on the previous dictionary.
            title_list = []
            for elem in raw_title_list:
                title_list.append(elem['title'].replace(" ", "_"))

            # Save all the output links in the dictionary for the current query.
            page_link_dict[query] = title_list

            print("Outlink query "+str(i)+" of "+str(len(query_strings))+" complete.")
        except Exception:
            print("Outlink query "+str(i)+" of "+str(len(query_strings))+" failed.")
            skipped += 1
        i += 1

    if skipped != 0:
        print("Skipped: "+str(skipped)+" outlink searches due to error in keys.")
    return page_link_dict


#Will receive two lists of categories and will find which elements of the second
#are in the first list, and will create a list of tuples.
def find_pairs(outlinks_dict_of_category1, category2_list):
    tuple_list = []

    print("Creating pairs...")
    for page_id in outlinks_dict_of_category1:
        list_of_pages = outlinks_dict_of_category1[page_id]

        for page in list_of_pages:
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


#Receives a page and returns a list with the names of its redirects.
#Note that the query returns the names with spaces, and this method
#will replace the spaces by the underscores before returning.
def find_redirects(page):
    site = wiki.Wiki("http://en.wikipedia.org/w/api.php")

    params = {'action':'query',
        'prop':'redirects',
        'format':'json',
        'rdprop':'title',
        'rdnamespace':'0',
        'rdlimit':'10',
        'titles':page}
    req = api.APIRequest(site, params)
    res = req.query(querycontinue=False)
    x = res['query']['pages'].keys()[0]
    dict_of_redirects = res['query']['pages'][x]['redirects']

    list_of_redirects = []
    for elem in dict_of_redirects:
        list_of_redirects.append(elem['title'].replace(" ","_"))

    return list_of_redirects


#Builds a list of triple (text, key, list).
#Text is the text in the category 1 pages (of the key)
#Key are the category 1 pages
#List is the list of pages in category 2 that appear in the category 1 page
def tkl_triple_xml(pair_list, redirects):
    site = wiki.Wiki("http://en.wikipedia.org/w/api.php")

    # Dictionary with category 1 pages as keys and category 2 pages
    # as values
    key_set_dict = group_pairs_into_dict(pair_list)

    # List that concatenates the result of each query and makes the tkl triple
    tkl_list = []
    i = 1

    # Execute a query for each page in category 1 (first page of the tuple of pair_list)
    for page_key in key_set_dict.keys():
        params = {'action': 'query',
            'prop': 'extracts',
            'format': 'xml',
            'titles': page_key}
        req = api.APIRequest(site, params)
        res = req.query(querycontinue=False)
        #pprint.pprint(res)
        key = res['query']['pages'].keys()[0]
        text = res['query']['pages'][key]['extract']

        list_of_pages = list(key_set_dict[page_key])

        #If the redirects flag is true, the redirects for each of the page
        #will be computed and added to the list of pages.
        if redirects:
            print "Computing redirects"
            list_of_redirects = []
            redirect_size = len(list_of_pages)

            for j, page in enumerate(list_of_pages):
                if j < 10:                                      #Will search only first 10 redirs for first 10 elements
                    try:
                        list_of_redirects += find_redirects(page)
                        print "Redirect "+str(j+1)+" of "+str(redirect_size)
                    except Exception as e:
                        print "Redirect exception: "+str(e)
                else:
                    break

            list_of_pages += list_of_redirects

        tkl_list.append([text, [page_key], list_of_pages])

        print("Text query "+str(i)+" of "+str(len(key_set_dict.keys()))+" complete.")
        i += 1

    return tkl_list


def create_triplet_database(pickle_filename, category1, category2, redirects):
    #Initialize writer to console and file
    f = open('output.txt', 'w')
    sys.stdout = Redirect(sys.stdout, f)

    #Reads the category text files and generates a list with each line.
    cat1_page_list = read_category_to_list(category1)
    cat2_page_list = read_category_to_list(category2)

    #Will create a dictionary with keys being each of the pages in the category,
    #and the values being all of the output links for that page. Receives as parameter
    #a list of pages for a certain category, and a window size that will define
    #how many pages to process per query.
    #outlinks_dict_of_category1 = find_outlinks([u'Il_Canzoniere',u'The_Raven', u'The_Canterbury_Tales'], 1)
    outlinks_dict_of_category1 = find_outlinks(cat1_page_list, 1)
    #print "Outlinks of category1: "+str(outlinks_dict_of_category1)

    #Will create a list of tuples. Each tuple is a pair of (page_in_category1, page_in_category2).
    #The tuple exists in the list if page_in_category2 is in the output links of page_in_category1.
    pair_list = find_pairs(outlinks_dict_of_category1, cat2_page_list)
    #print "Pair list: "+str(pair_list)

    #Builds a list of triple (text, key, list).
    #Text is the text in the category 1 pages (of the key)
    #Key are the category 1 pages
    #List is  the list of pages in category 2 that appear in the category 1 page
    tkl_triple_list = tkl_triple_xml(pair_list, redirects=redirects)

    #Once the queries are finished, will dump triplet object to file:
    pickle.dump(tkl_triple_list, open(pickle_filename, 'wb'), -1)
    print "Pickle dumped triplets successfully!"

    '''
    print "*******************************"
    for t in tkl_triple_list:
        print "*******************************"
        print t
        print "*******************************"
    print "*******************************"
    '''

###############
# START
###############
#If the line below is enabled, all the queries will be executed, a "triplets_poems.pkl" file containing all the
#triplets will be generated.
#Input files for the categories generated with Catscan2
c1 = "List_of_poems_depth_100.txt"
c2 = "List_of_poets_depth_100.txt"
redirects = True
create_triplet_database(pickle_filename="triplets_poems_redirects.pkl", category1=c1, category2=c2, redirects=redirects)

#Loading the triplets from file and running the ranking function
#tkl_triple_list = pickle.load(open("triplets_poems.pkl", 'rb'))
#get_ranking(tkl_triple_list)