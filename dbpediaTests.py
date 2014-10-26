# -*- coding: utf8 -*-
#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        dbpediaTests.py
#
# Author:      Horacio
#
# Created:     2014/04/01
# Testing dbpedia 
# 
#-----------------------------------------------------------------------------


import inspect
import os
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from copy import deepcopy
import pickle
import igraph
import inflect


endpoint = "http://dbpedia.org/sparql"
sparql = SPARQLWrapper(endpoint)
##dirDDI = '/home/usuaris/horacio/corpora/ddi/DDICorpus/'
dirDDI = 'L:/NQ/intercambio/experimentos/experimentosSeptiembre2011/semanticTagging/ddi/'
##dirDDI = '/homes(talp03/users/horacio/intercambio/experimentos/experimentosSeptiembre2011/semanticTagging/ddi/'

notInWP = []
collectedVariants = {}

##auxiliar functions

def setFoundTerms(fT):
    global foundTerms
    foundTerms = fT
    
def getVariables():
    global foundTerms, notInWP, pairs, predicatesFoundTerms, pend, collectedVariants
    return (foundTerms, notInWP, pairs, predicatesFoundTerms, pend, collectedVariants)


def getOtherVariations(w):
    rta = set([w])
    for i in getSingPlurVariations(w):
        rta.add(i)
    for i in deepcopy(rta):
        rta.add(i[0].lower()+i[1:])
        rta.add(i[0].upper()+i[1:])
    for i in deepcopy(rta):
        rta.add(i.replace(' ','_'))
    return rta
    
def getSingPlurVariations(w):
    global inflectEngine
    rta=set([w])
    rta.add(inflectEngine.plural_noun(w))
    try:
        w1=inflectEngine.singular_noun(w)
    except:
        w1 = w
    if w1:
        rta.add(w1)
    rta=list(rta)
    rta.sort(reverse=True, key=lambda x:len(x))
    return rta[:2]

def collectVariants(v):
    global collectedVariants
    v=set(v)
    for i in v:
        if i not in collectedVariants:
            collectedVariants[i]=set([])
        collectedVariants[i]=collectedVariants[i].union(v)

def _encode(data):
	return data.encode('utf8')

def _decode(data):
	return data.decode('utf8')
    
##functions

def prova1():
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label
        WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
    results.print_results()

def prova1_1():
    global pairs
    query = """
        SELECT ?type
        WHERE { ?type a owl:Class }
    """
    sparql.setReturnFormat(JSON)
    results = sparql.query()
    sparql.setQuery(query)
    rta = results.convert()
    pairs = set(map(lambda x:x['type']['value'],rta['results']['bindings']))
    if len(pairs) >0:
        print len(pairs), 'classes extracted from dbpedia '


def prova2():
    """
    get all classes 
    """
    global rta, classes
    sparql.setQuery("""
        SELECT DISTINCT * { ?x a owl:Class }
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
##    results.print_results()
    rta = results.convert()
    classes = set(map(lambda x:x['x']['value'],rta['results']['bindings']))
    print len(classes), 'classes extracted from dbpedia'

def prova3():
    """
    get all predicates
    """
    global rta, predicates
    sparql.setQuery("""
        SELECT DISTINCT * { ?x a rdf:Property }
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
##    results.print_results()
    rta = results.convert()
    predicates = set(map(lambda x:x['x']['value'],rta['results']['bindings']))
    print len(predicates), 'predicates extracted from dbpedia'


def prova4(c):
    """
    get all predicates of a given class c
    """
    global rta, predicatesXclass
    try:
        print len(predicatesXclass), 'predicatesXclass exist'
    except:
        predicatesXclass={}
    query = """
        SELECT distinct ?subject
        FROM <http://dbpedia.org>
        {
        ?subject rdfs:domain ?object .
        **1** rdfs:subClassOf ?object
        OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0) ).
        }"""
    query = query.replace('**1**',c)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
##    results.print_results()
    rta = results.convert()
    predicatesXclass[c] = set(map(lambda x:x['subject']['value'],rta['results']['bindings']))
    print len(predicatesXclass[c]), 'predicates extracted from dbpedia for class', c


def prova5(p, limit = 1000):
    """
    get all subject classes of a given predicate p
    """
    global rta, classesSubjectXpredicates
    try:
        print len(classesSubjectXpredicates), 'classesSubjectXpredicates exist'
    except:
        classesSubjectXpredicates={}
    query = """
        SELECT distinct ?subject
        {
        ?subject **1** ?o 
        }"""
    query = query.replace('**1**',p)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
##    results.print_results()
    rta = results.convert()
    classesSubjectXpredicates[p] = set(map(lambda x:x['subject']['value'],rta['results']['bindings']))
    print len(classesSubjectXpredicates[p]), 'subject classes extracted from dbpedia for predicate', p

def prova6(p, limit = None):
    """
    get all objct classes of a given predicate p
    """
    global rta, classesObjectXpredicates
    try:
        print len(classesObjectXpredicates), 'classesObjectXpredicates exist'
    except:
        classesObjectXpredicates={}
    query = """
        SELECT distinct ?object
        {
        ?s **1** ?object 
        }
        **2**
        """
    query = query.replace('**1**',p)
    if limit:
        query = query.replace('**2**','LIMIT '+str(limit))
    else:
        query = query.replace('**2**','')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
##    results.print_results()
    rta = results.convert()
    classesObjectXpredicates[p] = set(map(lambda x:x['object']['value'],rta['results']['bindings']))
    print len(classesObjectXpredicates[p]), 'object classes extracted from dbpedia for predicate', p

def prova7(s):
    """
    get all classes containing a substring s
    """
    global rta, classes
    query ="""
        SELECT DISTINCT * { ?x a owl:Class 
        FILTER (regex(str(?x), '**1**', 'i'))}
        """
    query = query.replace('**1**', s)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
##    results.print_results()
    rta = results.convert()
    classes = set(map(lambda x:x['x']['value'],rta['results']['bindings']))
    print len(classes), 'classes extracted from dbpedia containing', s

def prova71(s):
    """
    get all classes containing a substring s
    """
    global rta, pairs
    pairs=[]
    query ="""
        SELECT DISTINCT * { <http://dbpedia.org/resource/**1**> ?p ?o}
        """
    query = query.replace('**1**', s)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
    rta = results.convert()
    pairs = set(map(lambda x:(x['p']['value'],x['o']['value']),rta['results']['bindings']))
    if len(pairs) >0:
        print len(pairs), 'classes extracted from dbpedia containing', s

def prova72(p):
    """
    get all pairs for a given predicate
    """
    global rta, pairs
    pairs=[]
    query ="""
        SELECT DISTINCT * { ?s <**1**> ?o}
        """
    query = query.replace('**1**', p)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
    rta = results.convert()
    pairs = set(map(lambda x:(x['s']['value'],x['o']['value']),rta['results']['bindings']))
    if len(pairs) >0:
        print len(pairs), 'pairs extracted from dbpedia with predicate', p

def prova73(t, el, re1, re2):
    """
    Un elemento instanciado, se devuelven pares de los otros dos filtrados
    por re
    t = elemento instanciado: 's','p' u 'o'
    el = valor del elemento instanciado
    re1, re2 = filtros sobre los otros elementos
    """
    global rta, pairs
    pairs=[]
    if t == 's':
        query ="""
            SELECT DISTINCT * { **1** ?x ?y
            FILTER (regex(str(?x), '**2**', 'i'))
            FILTER (regex(str(?y), '**3**', 'i'))}
            """
    elif t == 'p':
        query ="""
            SELECT DISTINCT * { ?x **1**  ?y
            FILTER (regex(str(?x), '**2**', 'i'))
            FILTER (regex(str(?y), '**3**', 'i'))}
            """
    elif t == 'o':
        query ="""
            SELECT DISTINCT * { ?x ?y **1**  
            FILTER (regex(str(?x), '**2**', 'i'))
            FILTER (regex(str(?y), '**3**', 'i'))}
            """
    query = query.replace('**1**', el)
    query = query.replace('**2**', re1)
    query = query.replace('**3**', re2)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
    rta = results.convert()
    pairs = set(map(lambda x:(x['x']['value'],x['y']['value']),rta['results']['bindings']))
    if len(pairs) >0:
        print len(pairs), 'pairs extracted from dbpedia', t, el, re1, re2

def prova74(t, el1, el2, re1):
    """
    Dos elementos instanciados, se devuelve el otro filtrado por re1
    t = elemento no instanciado (restringido: 's','p' u 'o'
    el1, el2 = valor de los elementos instanciados
    re1 = filtro sobre el elemento no instanciado
    """
    global rta, classes
    classes=[]
    if t == 's':
        query ="""
            SELECT DISTINCT * { ?x **2**  **3**
            FILTER (regex(str(?x), '**1**', 'i'))}
            """
    elif t == 'p':
        query ="""
            SELECT DISTINCT * { **2** ?x **3**
            FILTER (regex(str(?x), '**1**', 'i'))}
            """
    elif t == 'o':
        query ="""
            SELECT DISTINCT * { **2**  **3** ?x  
            FILTER (regex(str(?x), '**1**', 'i'))}
            """
    query = query.replace('**1**', re1)
    query = query.replace('**2**', el1)
    query = query.replace('**3**', el2)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
    rta = results.convert()
    classes = set(map(lambda x:x['x']['value'],rta['results']['bindings']))
    if len(pairs) >0:
        print len(classes), 'classes extracted from dbpedia', t, el1, el2, re1

def prova8(s):
    """
    get all predicates containing a substring s
    """
    global rta, predicates
    query ="""
        SELECT DISTINCT * {
        ?x a rdf:Property 
        FILTER (regex(str(?x), '**1**', 'i'))}
        """
    query = query.replace('**1**', s)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
##    results.print_results()
    rta = results.convert()
    predicates = set(map(lambda x:x['x']['value'],rta['results']['bindings']))
    print len(predicates), 'predicates extracted from dbpedia containing', s

def prova9(c):
    """
    get all subclasses of a class c
    """
    global rta, classes
    query ="""
        SELECT ?x

        WHERE
          {
            {
              SELECT *
              WHERE
                {
                  ?x rdfs:subClassOf ?y .
                }
            }  OPTION (transitive, t_distinct, t_in (?x), t_out (?y) ).
          FILTER (?y = **1**)
        }
    """
    query = query.replace('**1**', c)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
##    results.print_results()
    rta = results.convert()
    classes = set(map(lambda x:x['x']['value'],rta['results']['bindings']))
    print len(classes), 'subclasses extracted from dbpedia class', c

def prova10(c):
    """
    get all instances of a class c
    """
    global rta, instances
    query ="""
        ## Inference Context Enabled ##
        DEFINE input:inference "http://dbpedia.org/resource/inference/rules/dbpedia#"
        SELECT ?x
        WHERE {
          ?x a <http://dbpedia.org/ontology/NaturalPlace>
        }
    """
    query = query.replace('**1**', c)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query()
##    results.print_results()
    rta = results.convert()
    instances = set(map(lambda x:x['x']['value'],rta['results']['bindings']))
    print len(instances), 'instances extracted from dbpedia class', c

def printData(t, limit=None):
    global classes, predicates, predicatesXclass, classesSubjectXpredicates, classesObjectXpredicates, instances
    global pairs
    print t
    if t == 'classes':
        if not limit:
            limit =len(classes)
        for i in list(classes)[:limit]:
            print '\t', i
    elif t == 'pairs':
        if not limit:
            limit =len(pairs)
        for i in list(pairs)[:limit]:
            print '\t', i
    elif t == 'predicates':
        if not limit:
            limit =len(predicates)
        for i in list(predicates)[:limit]:
            print '\t', i
    elif t == 'instances':
        if not limit:
            limit =len(instances)
        for i in list(instances)[:limit]:
            print '\t', i
    elif t == 'predicatesXclass':
        predicatesXclassKeys = predicatesXclass.keys()
        if not limit:
            limit1 =len(predicatesXclassKeys)
        else:
            limit1 = limit
        for i in predicatesXclassKeys[:limit1]:
            print '\t', i
            if not limit:
                limit2 =len(predicatesXclass[i])
            else:
                limit2 = limit
            for j in list(predicatesXclass[i])[:limit2]:
                print '\t\t', j
    elif t == 'classesSubjectXpredicates':
        classesSubjectXpredicatesKeys = classesSubjectXpredicates.keys()
        if not limit:
            limit1 =len(classesSubjectXpredicatesKeys)
        else:
            limit1 = limit
        for i in classesSubjectXpredicatesKeys[:limit1]:
            print '\t', i
            if not limit:
                limit2 =len(classesSubjectXpredicates[i])
            else:
                limit2 = limit
            for j in list(classesSubjectXpredicates[i])[:limit2]:
                print '\t\t', j
    elif t == 'classesObjectXpredicates':
        classesObjectXpredicatesKeys = classesObjectXpredicates.keys()
        if not limit:
            limit1 =len(classesObjectXpredicatesKeys)
        else:
            limit1 = limit
        for i in classesObjectXpredicatesKeys[:limit1]:
            print '\t', i
            if not limit:
                limit2 =len(classesObjectXpredicates[i])
            else:
                limit2 = limit
            for j in list(classesObjectXpredicates[i])[:limit2]:
                print '\t\t', j
            

def loadFoundTerms(inF):
    global foundTerms
    foundTerms = map(lambda x:x.replace('\n',''),open(inF).readlines()) 
    print len(foundTerms), 'foundTerms'
    
def loadNotInWP(inF):
    global notInWP
    notInWP = map(lambda x:x.replace('\n',''),open(inF).readlines()) 
    print len(notInWP), 'notInWP'
    
def prova11():
    global foundTerms, notInWP, classesFoundTerms, classesNotInWP, classes
    errors =[]
    classesFoundTerms = {}
    classesNotInWP = {}
    for t in foundTerms:
        prova7(t)
        if len(classes)==0:
            continue
        classesFoundTerms[t]=deepcopy(classes)
    for t in notInWP:
        try:
            prova7(t)
        except:
            errors.append(t)
            continue
        if len(classes)==0:
            continue
        classesNotInWP[t]=deepcopy(classes)
    print 'errors found', len(errors)
    for i in errors:
        print '\t',i

def prova12(verbose=False):
    global foundTerms, notInWP, classesFoundTerms, classesNotInWP, classes
    global pairs, predicatesFoundTerms, pend, collectedVariants
    predicatesFoundTerms={}
    collectedVariants = {}
    errors =set([])
    pend=set([])
    for iT in range(len(foundTerms)):
        t= foundTerms[iT]
        tS = getOtherVariations(t)
        if iT%10 == 0:
            print iT, 'from', len(foundTerms)
        ok=False
        for i in tS:
            try:
                prova71(i)
            except:
                pairs = []
                continue
            if len(pairs)==0:
                continue
            ok = True
            break
        if ok:
            for p,o in pairs:
                if p not in predicatesFoundTerms:
                    predicatesFoundTerms[p] = set((t,i))
                else:
                    predicatesFoundTerms[p].add((t,i))
                collectVariants(tS)
        else:
            pend.add(t)
    for iT in range(len(notInWP)):
        t= notInWP[iT]
        tS = getOtherVariations(t)
        if iT%10 == 0:
            print iT, 'from', len(notInWP)
        ok=False
        for i in tS:
            try:
                prova71(i)
            except:
                pairs = []
                continue
            if len(pairs)==0:
                continue
            ok = True
            break
        if ok:
            for p,o in pairs:
                if p not in predicatesFoundTerms:
                    predicatesFoundTerms[p] = set((t,i))
                else:
                    predicatesFoundTerms[p].add((t,i))
                collectVariants(tS)
        else:
            pend.add(t)
    print 'errors found', len(errors)
    if verbose:
        for i in errors:
            print '\t',i
    print 'pend found', len(pend)
    if verbose:
        for i in pend:
            print '\t',i
    print 'predicates found', len(predicatesFoundTerms)
    if verbose:
        for i in predicatesFoundTerms:
            print '\t',i, len(predicatesFoundTerms[i])
    c=set([])
    for i in predicatesFoundTerms:
        for j in predicatesFoundTerms[i]:
            c.add(j)
    print len(c), 'pairs found'
    c=set([])
    for i in predicatesFoundTerms:
        for j in predicatesFoundTerms[i]:
            c.add(j[0])
    print len(c), 'terms found'
    return len(c)



    
def histograms_1(size=100):
    global pairs, predicatesFoundTerms, pend
    a = []
    for i in predicatesFoundTerms:
        a.append((len(predicatesFoundTerms[i]),i))
    a= filter(lambda x:x[0]>size,a)
    a.sort(reverse=True)
    for i in a:
        print i

def histograms_2(p):
    global pairs, predicatesFoundTerms
    print len(predicatesFoundTerms[p]), 'original terms'
    print len(pairs), 'pairs for predicate', p
    a = set(map(lambda x:x[0],predicatesFoundTerms[p]))
    b = set(map(lambda x:x[0].replace('http://dbpedia.org/resource/',''),pairs))
    a_b = a.difference(b)
    print 'a - b',len(a_b)
    b_a = b.difference(a)
    print 'b - a',len(b_a)
    ab = a.intersection(b)
    print 'a intersection b', len(ab)
    ab=list(ab)
    ab.sort()
    a_b=list(a_b)
    a_b.sort()
    b_a=list(b_a)
    b_a.sort()
    print 'a - b***************'
    for i in a_b:
        print '\t'+i
    print 'b - a***************'
    for i in b_a:
        print '\t'+i
    print 'ab***************'
    for i in ab:
        print '\t'+i
    
def histograms_3(p):
    global pairs, predicatesFoundTerms, collectedVariants
    print len(predicatesFoundTerms[p]), 'original terms'
    print len(pairs), 'pairs for predicate', p
    a = set(map(lambda x:x[0],predicatesFoundTerms[p]))
    b = set(map(lambda x:x[0].replace('http://dbpedia.org/resource/',''),pairs))
    a_b = set([])
    b_a = set([])
    ab = set([])
    for i in a:
        if i in b:
            ab.add(i)
            continue
        if i in collectedVariants:
            iS = collectedVariants[i]
        else:
            iS=[]
        ok = False
        for j in iS:
            if j in b:
                ab.add(i)
                ok = True
                break
        if not ok:
            a_b.add(i)
    for i in b:
        if i in a:
            continue
        if i in collectedVariants:
            iS = collectedVariants[i]
        else:
            iS=[]
        ok = False
        for j in iS:
            if j in a:
                ok = True
                break
        if not ok:
            b_a.add(i)
    print 'a - b',len(a_b)
    print 'a intersection b', len(ab)
    ab=list(ab)
    ab.sort()
    a_b=list(a_b)
    a_b.sort()
    b_a=list(b_a)
    b_a.sort()
    print 'a - b***************'
    for i in a_b:
        print '\t'+i
    print 'b - a***************'
    for i in b_a:
        print '\t'+i
    print 'ab***************'
    for i in ab:
        print '\t'+i
    
def histograms_4():
    global predicatesFoundTerms
    for p in predicatesFoundTerms:
        print 'predicate', p
        histograms_4_1(p)
        
def histograms_4_1(p):
    global predicatesFoundTerms
    oS={}
    for i in predicatesFoundTerms[p]:
        if i not in oS:
            oS[i]=1
        else:
            oS[i]+=1
    c = float(len(predicatesFoundTerms[p]))
    print '\toS', len(oS), 'total', c, 'ratio', c/len(oS)
    oS = map(lambda x:(oS[x],x),oS.keys())
    oS.sort(reverse=True)
    for i in range(min(10,len(oS))):
        print '\t\t',oS[i]
        
def save_pickle_classesFoundTerms_NotInWP(outF):
    global classesFoundTerms, classesNotInWP
    outF=open(outF,'wb')
    pickle.dump(classesFoundTerms, outF)
    print len(classesFoundTerms), 'classesFoundTerms'
    pickle.dump(classesNotInWP, outF)
    print len(classesNotInWP), 'classesNotInWP'
    outF.close()

def save_pickle_predicatesFound(outF):
    global pairs, predicatesFoundTerms, pend
    outF=open(outF,'wb')
    pickle.dump(predicatesFoundTerms, outF)
    print len(predicatesFoundTerms), 'predicatesFoundTerms'
    pickle.dump(pend, outF)
    print len(pend), 'pend'
    outF.close()

def load_pickle_predicatesFound(inF):
    global pairs, predicatesFoundTerms, pend
    inF=open(inF,'rb')
    predicatesFoundTerms = pickle.load(inF)
    print len(predicatesFoundTerms), 'predicatesFoundTerms'
    pend = pickle.load(inF) 
    print len(pend), 'pend'
    inF.close()


##global

inflectEngine = inflect.engine()

    
##main

##prova2()
##printData('classes',10)
                
##prova3()
##printData('predicates',10)
                
##prova4('<http://dbpedia.org/ontology/Band>')
##printData('predicatesXclass',10)

##prova5(u'<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>', limit = 1000)                
##printData('classesSubjectXpredicates',10)

##prova6(u'<http://dbpedia.org/ontology/age>', 100)
##prova6(u'<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>', 100)
##printData('classesObjectXpredicates',10)

##prova7('person')
##printData('classes',10)

##prova8('person')
##printData('predicates',10)

##prova9('<http://dbpedia.org/class/yago/Church103028079>')
##printData('classes',10)

##prova10('<http://dbpedia.org/class/yago/Church103028079>')
##printData('instances',10)

##prova8('person')
##printData('predicates',10)

##loadFoundTerms(dirDDI+'foundTerms.txt')
##loadNotInWP(dirDDI+'savenotInWP.txt')
##prova12()
##save_pickle_classesFoundTerms_NotInWP(dirDDI+'classesFoundTerms_NotInWP.pic')
##t='Progesterone'
##p=u'http://dbpedia.org/property/drugbank'
##prova72(p)
##histograms_2(p)
##save_pickle_predicatesFound(dirDDI+'predicatesFound.pic')
##histograms_3(p)
