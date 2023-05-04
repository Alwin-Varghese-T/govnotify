import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymysql.cursors
from pymysqlpool import ConnectionPool
import os
from rapidfuzz import process, fuzz

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('stopwords')


#mysql pool connection
pool =ConnectionPool(
    size=5,
    name='flask_pool',
    host=os.getenv('your_host'),
    user=os.getenv('your_username'),
    password=os.getenv('your_password'),
    db=os.getenv('your_database'),
    ssl = {'ssl_ca':os.getenv('your_ssl_ca')},
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
mysql = pool.get_connection()


# Define the preprocess_text function to tokenize, lemmatize, and remove stopwords
def preprocess_text(text):
    # Tokenize the text into words
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.lower() not in stop_words]
    # Lemmatize the remaining words
    lemmatizer = WordNetLemmatizer()
    lem_tokens = [lemmatizer.lemmatize(token, get_wordnet_pos(token)) for token in tokens]
    # Join the lemmatized tokens back into a string
    text = " ".join(lem_tokens)
    return text


# Define the get_wordnet_pos function to get the WordNet part of speech for a given token
def get_wordnet_pos(token):
    tag = nltk.pos_tag([token])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


# Define the get_relevant_links function to calculate the cosine similarities between the preprocessed profile and preprocessed descriptions of the links, and return a list of relevant links with their cosine similarity scores
def get_relevant_links(links, profile_text):
    # Preprocess the user profile
    preprocessed_profile = preprocess_text(profile_text)
    
    # Preprocess the links and store the preprocessed descriptions in a list
    preprocessed_descs = []
    for link in links:
        preprocessed_desc = preprocess_text(link['keywords'])
        preprocessed_descs.append(preprocessed_desc)

    # Calculate the TF-IDF matrix for the preprocessed descriptions
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(preprocessed_descs)

    # Calculate the cosine similarities between the preprocessed profile and preprocessed descriptions
    cosine_similarities = cosine_similarity(tfidf_matrix, tfidf_vectorizer.transform([preprocessed_profile])).flatten()

    # Create a list of relevant links with their scores
    relevant_links = [{'name': link['sname'], 'link': link['links'], 'desc': link['descripton'], 'score': score} for link, score in zip(links, cosine_similarities) if score > -1]

    # Sort the relevant links based on their cosine similarity score in descending order
    relevant_links = sorted(relevant_links, key=lambda x: x['score'], reverse=True)
    return relevant_links

def similarity(email):

    
    with mysql.cursor() as cursor:
        # retrieving user details
        
        cursor.execute("select gender, age, marriage, seniorty, belong, diff, ration, income, category, checkbox from accounts  where email = %s",(email))
        user_profile = cursor.fetchone()
        profile_text = ' '.join(str(val) for val in user_profile.values())

        # retrieving category
        category = user_profile["category"]

        # retrieving schemas based on category
        cursor.execute("select * from schemes where category = %s",category)
        links = cursor.fetchall()
        links_on_selected_category = get_relevant_links(links,profile_text)
      
        #retrieving other schemas not in selected category
        cursor.execute("select * from schemes where not category = %s",category)
        links = cursor.fetchall()
        other_links = get_relevant_links(links,profile_text)
       
        return links_on_selected_category, other_links


def search_nlp(search_element):

  with mysql.cursor() as cursor:
    cursor.execute("select * from schemes")
    results = cursor.fetchall()

    search_term = search_element
    title_threshold = 10
    desc_threshold = 60

    # Use rapidfuzz to match search term with title and description columns
    matching_schemes = []
    for r in results:
        title_score = fuzz.token_sort_ratio(search_term, r['sname'])
        if title_score >= title_threshold:
            matching_schemes.append({'title': r['sname'], 'description': r['descripton'], 'link': r['links'], 'score': title_score})
        else:
            desc_score = fuzz.token_sort_ratio(search_term, r['descripton'])
            if desc_score >= desc_threshold:
                matching_schemes.append({'title': r['sname'], 'description': r['descripton'], 'link': r['links'], 'score': desc_score})
    
    # Remove duplicates by using a set to store matching scheme names
    matching_schemes_set = set()
    unique_matching_schemes = []
    for scheme in matching_schemes:
        if scheme['title'] not in matching_schemes_set:
            matching_schemes_set.add(scheme['title'])
            unique_matching_schemes.append(scheme)
    
    # Sort matching schemes by score in descending order
    unique_matching_schemes = sorted(unique_matching_schemes, key=lambda x: x['score'], reverse=True)
    
  return unique_matching_schemes