import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('stopwords')

from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymysql.cursors
import os
import jellyfish


#mysql connection
mysql = pymysql.connect(
    host=os.getenv('your_host'),
    user=os.getenv('your_username'),
    password=os.getenv('your_password'),
    db=os.getenv('your_database'),
    ssl = {'ssl_ca':os.getenv('your_ssl_ca')},
    cursorclass=pymysql.cursors.DictCursor
)

#implicit morphological analysis using WordNetLemmatizer
def get_wordnet_pos(word):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)
  
#Preprocess text by tokenizing, lemmatizing, and removing stopwords
def preprocess_text(text):
    tokens = nltk.word_tokenize(text.lower())
    lemmatizer = WordNetLemmatizer()
    lem_tokens = [lemmatizer.lemmatize(token, get_wordnet_pos(token)) for token in tokens]
    stop_words = set(nltk.corpus.stopwords.words('english'))
    filtered_tokens = [token for token in lem_tokens if token not in stop_words]
    return " ".join(filtered_tokens)
  
#synonyms of a word using WordNet
def get_synonyms(word):
    synonyms = set()
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name().lower())
    return synonyms

def expand_query(query):
    """Expand query by adding synonyms of each word"""
    expanded_query = set()
    for word in query.split():
        expanded_query.add(word)
        synonyms = get_synonyms(word)
        expanded_query.update(synonyms)
    return " ".join(expanded_query)

def similarity(email):

  with mysql.cursor() as cursor:
    #retrieving priority weightage from database 
    id = 'admin'
    cursor.execute("select gender, age, state, category , marriage from priority where id= %s ",(id))
    priority_weightage = cursor.fetchone()
    #retrieving user details
    cursor.execute("select gender, age, state, category , marriage  from account  where email = %s",(email))
    user_profile = cursor.fetchone()
    #retrieving schemas
    cursor.execute("select * from links")
    links = cursor.fetchall()
  
    # create a dictionary mapping each profile attribute to its corresponding weightage
    user_profile_with_weightage = {user_profile [key]: int(priority_weightage[key]) for key in user_profile}
    
    # combine profile attributes into a single text string, weighted by their weightages
    profile_text = ''
    for key, value in user_profile_with_weightage.items():
        profile_text += (key + ' ') * value
    
    # get descriptions of each link and preprocess them by tokenizing, lemmatizing, and removing stopwords
    link_descriptions = [link['descriptions'] for link in links]
    preprocessed_links = [preprocess_text(description) for description in link_descriptions]
    
    # create a TfidfVectorizer object to compute TF-IDF scores for each word in the link descriptions
    vectorizer = TfidfVectorizer()
    
    # compute the TF-IDF matrix for the combined profile text and the preprocessed link descriptions
    tfidf_matrix = vectorizer.fit_transform([preprocess_text(profile_text), *preprocessed_links])
    
    # expand query by adding synonyms of each word
    query = preprocess_text(profile_text)
    expanded_query = expand_query(query)
    
    # compute cosine similarities between expanded query and link descriptions
    expanded_query_tfidf = vectorizer.transform([expanded_query])
    cosine_similarities = cosine_similarity(expanded_query_tfidf, tfidf_matrix[1:]).flatten()
    
  
    # select relevant links based on cosine similarity score
    relevant_links = [{'name': link['name'], 'link': link['link'],'desc':link['descriptions'], 'score': score} for link, score in zip(links, cosine_similarities) if score > 0]
    #sort the relevant links based on their cosine similarity score in descending order
    relevant_links = sorted(relevant_links, key=lambda x: x['score'], reverse=True)
    #return the list of relevant links with their names, links and cosine similarity scores
    return relevant_links



def search_nlp(search_element):

  with mysql.cursor() as cursor:
    cursor.execute("select * from links")
    links = cursor.fetchall()

    matches = []
    for link in links:
        inp = search_element.lower()
        lnk = link['name'].lower()
        similarity = jellyfish.jaro_winkler(inp,lnk)
        if similarity > 0.625: 
            link['similarity'] = similarity
            matches.append(link)
    matches.sort(key=lambda x: x['similarity'], reverse=True)
  return matches
    
    