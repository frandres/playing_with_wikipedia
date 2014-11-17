from HTMLParser import HTMLParser
#from nltk.stem import WordNetLemmatizer
from string import punctuation

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        acum = ''
        for i in range(0,len(self.fed)):
            if self.fed[i] == '.':
                self.fed[i] = '. '
            acum+=self.fed[i]
        return acum

def preprocess_id(ids):
    ids = ids.replace('_',' ')
    ids = ids.replace('(','\\\\(')
    ids = ids.replace(')','\\\\)')
    return ids

def preprocess_context(context):
    # Remove punctuation signs
    punctuation='()?:;,.!/"\''
    for p in punctuation:
        context.replace(p,' ')
    '''
    # Lemmatize
    wnl = WordNetLemmatizer()
    context = wnl.lemmatize(context)
    '''
    return context

    

def strip_html(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


