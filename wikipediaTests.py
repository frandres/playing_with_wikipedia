# -*- coding: utf8 -*-
#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        wikipediaTests.py
#
# Author:      Horacio
#
# Created:     2014/05/22
# Testing wikipedia 
# 
#-----------------------------------------------------------------------------


import inspect
import re
import os
import sys
#from SPARQLWrapper import SPARQLWrapper, JSON
from copy import deepcopy
import pickle
import locale
#import igraph
import inflect


##Para facilitar el acceso a la Wikipedia (wp) es conveniente usar el módulo
##wikitools (http://code.google.com/p/python-wikitools/)
##del cual importamos los siguientes ficheros
##El principal objetivo de wikitools es hacer de wrapper a los servicios de la
##api de mediawiki que es la que soporta los procesos.
##La página principal de mediawiki api: http://www.mediawiki.org/wiki/API
##Se puede consultar además el código de los ficheros que se importan
 
from wikitools import wiki
from wikitools import api
from wikitools import page
from wikitools import category

##Al usar una WP que pueda contener en su Namespace algún string con caracteres
##no ASCII (me ha ocurrido con la WP española) da un error de UnicodeException.
##Es posible que el bug ya esté solucionado (yo he usado la versión 2.5 de Python
##y la versión 1.1.1 de wikitools) pero si no fuera así y quisierais utilizar la
##WP española o alguna otra con códigos no ASCII podeis cambiar en wiki.py
##la línea
##                        setattr(self, attr, Namespace(ns))
##por las 4 líneas siguientes:
##			try:
##                                setattr(self, attr, Namespace(ns))
##                        except:
##                                pass
##Es una solución chapucera ya que elimina del Namespace el atring problemático
##pero para nuestro caso funciona.

##Lo siguiente es necesario para poder funcionar razonablemente con unicode

locale.setlocale(locale.LC_ALL, '')

##global

dirDDI = 'L:/NQ/intercambio/experimentos/experimentosSeptiembre2011/semanticTagging/ddi/'
lang = 'en'

wikiAPI = {
    'en': "http://en.wikipedia.org/w/api.php",
    'es': "http://es.wikipedia.org/w/api.php"}

site = wiki.Wiki(wikiAPI[lang])

##classes


##functions

##########################################################################
# Guess Character Encoding
##########################################################################

# adapted from io.py in the docutils extension module (http://docutils.sourceforge.net)
# http://www.pyzine.com/Issue008/Section_Articles/article_Encodings.html

def guess_encoding(data):
    """
    Given a byte string, attempt to decode it.
    Tries the standard 'UTF8' and 'latin-1' encodings,
    Plus several gathered from locale information.

    The calling program *must* first call::

        locale.setlocale(locale.LC_ALL, '')

    If successful it returns C{(decoded_unicode, successful_encoding)}.
    If unsuccessful it raises a C{UnicodeError}.
    """
    successful_encoding = None
    # we make 'utf-8' the first encoding
    encodings = ['utf-8']
    #
    # next we add anything we can learn from the locale
    try:
        encodings.append(locale.nl_langinfo(locale.CODESET))
    except AttributeError:
        pass
    try:
        encodings.append(locale.getlocale()[1])
    except (AttributeError, IndexError):
        pass
    try: 
        encodings.append(locale.getdefaultlocale()[1])
    except (AttributeError, IndexError):
        pass
    #
    # we try 'latin-1' last
    encodings.append('latin-1')
    for enc in encodings:
        # some of the locale calls 
        # may have returned None
        if not enc:
            continue
        try:
            decoded = unicode(data, enc)
            successful_encoding = enc

        except (UnicodeError, LookupError):
            pass
        else:
            break
    if not successful_encoding:
         raise UnicodeError(
        'Unable to decode input data.  Tried the following encodings: %s.'
        % ', '.join([repr(enc) for enc in encodings if enc]))
    else:
         return (decoded, successful_encoding)

def _encode(data):
	return data.encode('utf8')

def _decode(data):
	return data.decode('utf8')

def multiple_replace(dict, text): 

  """ Replace in 'text' all occurences of any key in the given
  dictionary by its corresponding value.  Returns the new tring.""" 

  # Create a regular expression  from the dictionary keys
  regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

  # For each match, look-up corresponding value in dictionary
  return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

def normalizeFileName(fN):
    return multiple_replace({'?':'_','/':'_',' ':'_'},fN).lower()

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

def describePage(p, verbose = False):
        if not p.exists:
            print 'page does not exist'
            return None
        print 'title', p.title
        print 'wikitext len', len(p.wikitext)
        if verbose:
            print p.wikitext
        print 'templates len', len(p.templates)
        if verbose:
            print p.templates
        print 'links len', len(p.links)
        if verbose:
            print p.links
        print 'categories len', len(p.categories)
        if verbose:
            print p.categories
        
def save_pickle_FoundPagesInWP(outF):
    global foundedPagesInWP
    global pend
    outF=open(outF,'wb')
    pickle.dump(foundedPagesInWP, outF)
    print len(foundedPagesInWP), 'foundedPagesInWP'
    pickle.dump(pend, outF)
    print len(pend), 'pend'
    outF.close()

def loadFoundTerms(inF):
    global foundTerms
    foundTerms = map(lambda x:x.replace('\n',''),open(inF).readlines()) 
    print len(foundTerms), 'foundTerms'
    
def loadNotInWP(inF):
    global notInWP
    notInWP = map(lambda x:x.replace('\n',''),open(inF).readlines()) 
    print len(notInWP), 'notInWP'
    
def getWPPage(name):
    global page, site
    try:
        pageTerm = page.Page(site,name)
    except:
        return None
    if not pageTerm.exists:
        return None
    pageTerm.setPageInfo()
    return pageTerm

def getWPCategory(name):
    global category, site
    try:
        categoryTerm = category.Category(site,name)
    except:
        return None
    if not categoryTerm.exists:
        return None
    categoryTerm.setPageInfo()
    return categoryTerm

def getPageText(mode, p):
    """
    mode = 'n' if p is just the name of the page
    mode = 'p' if p is an instance of page
    returns the list of sentences in text
    """
    rta = []
    if mode == 'n':
        p = getWPPage(p)
        if not p:
            return rta
    return map(lambda x:guess_encoding(x)[0],p.getWikiText().split('\n'))
        
def savePageOnFile(name,d,fn):
    t = getPageText('n', name)
    outF = open(d+normalizeFileName(fn),'w')
    for i in t:
        outF.write(_encode(i)+'\n')
    outF.close()

def getCatParent(mode, cat):
    """
    mode = 'n' if cat is just the name of the category
    mode = 'c' if cat is an instance of category
    accordingly the result is either a set of names or a set of category instances
    """
    rta = set([])
    if mode == 'n':
        cat = getWPCategory(cat)
        if not cat:
            return rta
    if not isinstance(cat,category.Category):
        return rta
    rta = cat.getCategories()
    if mode == 'c':
        rta = map (getWPCategory, rta)
    return set(rta)

def getCatChild(mode, cat):
    """
    mode = 'n' if cat is just the name of the category
    mode = 'c' if cat is an instance of category
    accordingly the result is either a set of names or a set of category instances
    """
    rta = set([])
    if mode == 'n':
        cat = getWPCategory(cat)
        if not cat:
            return rta
    if not isinstance(cat,category.Category):
        return rta
    rta = filter(
        lambda x:x.title.startswith('Category:'),
        cat.getAllMembers())
    rta = map(lambda x:x.title, rta)
    if mode == 'n':
        return set(rta)
    else:    
        return set(map (getWPCategory, rta))

def getCatAncestors(mode, cat, limit):
    """
    mode = 'n' if cat is just the name of the category
    mode = 'c' if cat is an instance of category
    accordingly the result is either a set of
    tuples <name, distance> or a set of tuples <category instance, distance>
    """
    rta = set([])
    if mode == 'n':
        cat = getWPCategory(cat)
        if not cat:
            return rta
    rta = getCatAncestors_1([(cat,0)], limit)
    if mode == 'n':
        return set(map(lambda x:(x[0].title,x[1]),rta))
    return rta
                   
def getCatDescendants(mode, cat, limit):
    """
    mode = 'n' if cat is just the name of the category
    mode = 'c' if cat is an instance of category
    accordingly the result is either a set of
    tuples <name, distance> or a set of tuples <category instance, distance>
    """
    rta = set([])
    if mode == 'n':
        cat = getWPCategory(cat)
        if not cat:
            return rta
    rta = getCatDescendants_1([(cat,0)], limit)
    if mode == 'n':
        return set(map(lambda x:(x[0].title,x[1]),rta))
    return rta

def getCatAncestors_1(cats, limit):
##    print '*1*',cats,limit
    rta = set([])
    for cat,d in cats:
        if d+1>limit:
            continue
        rta = rta.union(set(map (lambda x:(x,d+1),getCatParent('c',cat))))
##    print '*2*',rta
    if rta == set([]):
        return rta
    return rta.union(getCatAncestors_1(rta, limit))

def getCatDescendants_1(cats, limit):
##    print '*1*',cats,limit
    rta = set([])
    for cat,d in cats:
        if d+1>limit:
            continue
        rta = rta.union(set(map (lambda x:(x,d+1),getCatChild('c',cat))))
##    print '*2*',rta
    if rta == set([]):
        return rta
    return rta.union(getCatDescendants_1(rta, limit))

def areRelatedCats(c1,c2,p,limit):
    """
    whether or not there is a path between c1 and c2
    returns None if no path exists
    returns <d> path length
    limit max path length
    p: path pattern:
        u up length 1
        u* up length > 1
        d down length 1
        d* down length > 1
        * whatever
        (u|d)+
    """
    if p == 'u':
        if c2.title in map(lambda x:x.title,getCatParent('c',c1)):
            return 1
        else:
            return None
    elif p == 'u*':
        x = getCatAncestors('c',c1,limit)
        for i in x:
            if c2 == i[0]:
                return i[1]
        return None
    elif p == 'd':
        if c2.title in map(lambda x:x.title,getCatChild('c',c1)):
            return 1
        else:
            return None
    elif p == 'd*':
        x = getCatDescendants('c',c1,limit)
        for i in x:
            if c2 == i[0]:
                return i[1]
        return None
    elif p == '*':
        x = getCatDescendants('c',c1,limit)
        for i in x:
            if c2 == i[0]:
                return i[1]
        x = getCatAncestors('c',c1,limit)
        for i in x:
            if c2 == i[0]:
                return i[1]
        return None
    elif re.match('^(u|d)+$',p) and len(p) <= limit:
        related = set([c1])
        for ip in range(len(p)):
            p1 = p[ip]
            relatedNew = set([])
            if p1 == 'u':
                map(lambda x:relatedNew.add(x),getCatParent('c',c1))
            elif p1 == 'd':
                map(lambda x:relatedNew.add(x),getCatChild('c',c1))
            if c2.title in map(lambda x:x.title,relatedNew):
                return ip
            related = deepcopy(relatedNew)
        return None
    else:
        return None
                    
def getCatOfPage(mode, p):
    """
    mode = 'n' if p is just the name of the page
    mode = 'p' if p is an instance of page
    accordingly the result is either a set of names or a set of category instances
    """
    rta = set([])
    if mode == 'n':
        p = getWPPage(p)
        if not p:
            return rta
    if not isinstance(p,page.Page):
        return rta
    rta = p.getCategories()
    if mode == 'n':
        rta = map(lambda x:x.title.replace('Category:',''),rta)
    return set(rta)

##lines=pageDemonym.getWikiText().split('\n')
##lines = map(lambda x:guess_encoding(x)[0],lines)
##len(lines)


def prova1(verbose=False):
    global foundTerms, notInWP, foundedPagesInfoundTerms, foundedPagesInnotInWP
    global pend, foundedPagesInWP
    foundedPagesInfoundTerms={}
    foundedPagesInnotInWP={}
    pend=set([])
    for iT in range(len(foundTerms)):
        if iT%10 == 0:
            print iT, 'from', len(foundTerms)
        t= foundTerms[iT]
        tS = getOtherVariations(t)
        ok = False
        for i in tS:
            pageTerm = getWPPage(i)
            if not pageTerm:
                continue
            else:
                ok = True
                foundedPagesInfoundTerms[t] = pageTerm
                break
        if not ok:
            pend.add(t)
    for iT in range(len(notInWP)):
        if iT%10 == 0:
            print iT, 'from', len(notInWP)
        t= notInWP[iT]
        tS = getOtherVariations(t)
        ok = False
        for i in tS:
            pageTerm = getWPPage(i)
            if not pageTerm:
                continue
            else:
                ok = True
                foundedPagesInnotInWP[t] = pageTerm
                break
        if not ok:
            pend.add(t)
    print 'pend not found', len(pend)
    if verbose:
        for i in pend:
            print '\t',i
    print 'foundedPagesInfoundTerms', len(foundedPagesInfoundTerms)
    if verbose:
        for i in foundedPagesInfoundTerms:
            print '\t',i
    print 'foundedPagesInnotInWP', len(foundedPagesInnotInWP)
    if verbose:
        for i in foundedPagesInnotInWP:
            print '\t',i
    foundedPagesInWP = set(foundedPagesInfoundTerms.keys()+ foundedPagesInnotInWP.keys())
    print 'foundedPagesInWP', len(foundedPagesInWP)
    if verbose:
        for i in foundedPagesInWP:
            print '\t',i

    
    
##global

inflectEngine = inflect.engine()

##main
            
##loadFoundTerms(dirDDI+'foundTerms.txt')
##loadNotInWP(dirDDI+'savenotInWP.txt')
prova1()
##save_pickle_FoundPagesInWP(dirDDI+'foundPagesInWP.pic')

