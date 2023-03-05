#cosine similarity with synonym
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

def get_wordnet_pos(word):
    """Map POS tag to first character used by WordNetLemmatizer"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

def preprocess_text(text):
    """Preprocess text by tokenizing, lemmatizing, and removing stopwords"""
    tokens = nltk.word_tokenize(text.lower())
    lemmatizer = WordNetLemmatizer()
    lem_tokens = [lemmatizer.lemmatize(token, get_wordnet_pos(token)) for token in tokens]
    stop_words = set(nltk.corpus.stopwords.words('english'))
    filtered_tokens = [token for token in lem_tokens if token not in stop_words]
    return " ".join(filtered_tokens)

def get_synonyms(word):
    """Get synonyms of a word using WordNet"""
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


def similarity(user_profile, links):
  priority_weightage = {
      'gender': 10,
      'age': 20,
      'state': 5,
      'category': 15,
      'marriage':25
      
  }
  user_profile_with_weightage = {user_profile [key]: priority_weightage[key] for key in user_profile}
  profile_text = ''
  for key, value in user_profile_with_weightage.items():
      profile_text += (key + ' ') * value
  link_descriptions = [link['descriptions'] for link in links]
  preprocessed_links = [preprocess_text(description) for description in link_descriptions]
  vectorizer = TfidfVectorizer()
  tfidf_matrix = vectorizer.fit_transform([preprocess_text(profile_text), *preprocessed_links])
  
  # expand query by adding synonyms of each word
  query = preprocess_text(profile_text)
  expanded_query = expand_query(query)
  
  # compute cosine similarities between expanded query and link descriptions
  expanded_query_tfidf = vectorizer.transform([expanded_query])
  cosine_similarities = cosine_similarity(expanded_query_tfidf, tfidf_matrix[1:]).flatten()
  
  # select relevant links based on cosine similarity score
  relevant_links = [{'name': link['name'], 'link': link['link'], 'score': score} for link, score in zip(links, cosine_similarities) if score > -1]
  relevant_links = sorted(relevant_links, key=lambda x: x['score'], reverse=True)
  
  return relevant_links