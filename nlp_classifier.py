from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import pymysql.cursors
import os
def predict(data1):
# Define the categories and their corresponding labels
  categories = {
      'Education': 0,
      'Health': 1,
      'Social Welfare': 2,
      'Agriculture': 3
  }
  
  #mysql connection
  mysql = pymysql.connect(
      host=os.getenv('your_host'),
      user=os.getenv('your_username'),
      password=os.getenv('your_password'),
      db=os.getenv('your_database'),
      ssl = {'ssl_ca':os.getenv('your_ssl_ca')},
      cursorclass=pymysql.cursors.DictCursor
  )
  
  with mysql.cursor() as cursor:
    cursor.execute('select * from schemes')
    data = cursor.fetchall()
  
  # Preprocess the data
  for d in data:
      # Remove commas and add spaces
      d['keywords'] = " ".join(d['keywords'].split(","))
  
  # Convert the data into feature vectors using the Bag-of-Words model
  corpus = [d['keywords'] for d in data]
  vectorizer = CountVectorizer()
  X = vectorizer.fit_transform(corpus)
  
  # Split the data into training and testing sets
  y = [categories[d['category']] for d in data]
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
  
  # Train the SVM classifier
  svm = SVC(kernel='linear')
  svm.fit(X_train, y_train)
  
  # Evaluate the performance of the classifier on the testing set
  accuracy = svm.score(X_test, y_test)
  print(f"Accuracy: {accuracy}")
  
  
# Use the trained SVM classifier to predict the category of a new scheme
 
  new_data = " ".join(data1.split(","))
  new_corpus = [new_data]
  new_X = vectorizer.transform(new_corpus)
  predicted_category = svm.predict(new_X)[0]
  for category, label in categories.items():
      if label == predicted_category:
          print(f"Predicted category: {category}")
          return category
  