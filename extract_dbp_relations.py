from SPARQLWrapper import SPARQLWrapper, JSON
import itertools
from functools import reduce
from collections import Counter
from urllib.error import HTTPError
from urllib import parse

def get_pages_simple(rdf_type, blacklist_prefixes):
    """Given an rdf:type, find all pages in DBpedia that have that
    rdf:type, as long as that page doesn't start with one of the prefixes in
    blacklist_prefixes """
    pages = set()

    offset = 0
    new_res = True
    while new_res:
        new_res = False
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?page {{
                SELECT ?page
                WHERE { ?page rdf:type """ + rdf_type + """ }
                ORDER BY ?page
            }}
            LIMIT 10000
            OFFSET """ + str(offset) + """
        """
        print(query)
        sparql.setQuery(query)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            page = result["page"]["value"]
            print("asdf")
            if all(not page.lower().startswith(x) for x in blacklist_prefixes):
                pages.add(page)
                print("New page: " + page)
            new_res = True

        offset += 10000

    return pages

def get_relations(type1s, type2s):
    """"Given type1s and type2s, lists of rdf:types, find all
    relations in DBpedia that occur between any entity of type 1 and any
    entity of type2 """

    type1subq = ["{ ?t1 a " + typ + " } " for typ in type1s]
    type1unions     = "UNION ".join(type1subq)
    type2subq = ["{ ?t2 a " + typ + " } " for typ in type2s]
    type2unions     = "UNION ".join(type2subq)
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = """
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       SELECT ?relation
       WHERE { """ + type1unions + type2unions + """
               ?t1 ?relation ?t2}
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    relations = []
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        relations.append(result["relation"]["value"].lower())

    return Counter(relations)

def get_pages_and_write_to_file(rdf_types, filename):
    """Given a list of rdf types, search DBpedia for pages with those types
       and write the pags to a file"""
    pages = reduce(set.union,
                [get_pages_simple(typ, []) for typ in rdf_types])
    print("Wrote " + str(len(pages)) + " pages to " + filename)
    with open(filename, 'w') as f:
        for p in sorted(list(pages)):
            f.write('"' + parse.unquote_plus(p.split("/")[-1]) + '"\n')

###############################################################################
# Get all the pages that are used for the wikipedia part
###############################################################################
river_types = ["dbpedia-owl:River"]
get_pages_and_write_to_file(river_types, "rivers.txt")

country_types = ["dbpedia-owl:Country"]
get_pages_and_write_to_file(country_types, "countries.txt")

band_types = ["dbpedia-owl:Band", "yago:Artist109812338",
            "dbpedia-owl:MusicalArtist"]
get_pages_and_write_to_file(band_types, "bands.txt")

album_types = ["<http://schema.org/MusicAlbum>"]
get_pages_and_write_to_file(album_types, "albums.txt")

poem_types = ["yago:Poem106377442"]
get_pages_and_write_to_file(poem_types, "poems.txt")

poet_types = ["yago:Poet110444194"]
get_pages_and_write_to_file(poet_types, "poets.txt")

def print_relations(t1, t2, filename):
    rels = get_relations(t1, t2)
    with open(filename, 'w') as f:
        f.write(str(rels))

###############################################################################
# Get and write all relationships found in dbpedia to files
###############################################################################

print_relations(poet_types, poem_types, "poet_poem_rels.txt")
print_relations(poem_types, poet_types, "poem_poet_rels.txt")
print_relations(album_types, band_types, "album_band_rels.txt")
print_relations(band_types, album_types, "band_album_rels.txt")
print_relations(river_types, country_types, "river_country_rels.txt")
print_relations(country_types, river_types, "country_river_rels.txt")



