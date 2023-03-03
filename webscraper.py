import requests
from bs4 import BeautifulSoup
import pymysql.cursors
import os


mysql = pymysql.connect(
    host=os.getenv('your_host'),
    user=os.getenv('your_username'),
    password=os.getenv('your_password'),
    db=os.getenv('your_database'),
    ssl = {'ssl_ca':os.getenv('your_ssl_ca')},
    cursorclass=pymysql.cursors.DictCursor
)

def delete_data():
  
  with mysql.cursor() as cursor:

    sql = "DELETE FROM latest_news "
    cursor.execute(sql,)
    mysql.commit()



def scraper():
  # Make a request to the website
  response = requests.get('https://www.india.gov.in/')

      # Parse the HTML content using BeautifulSoup
  soup = BeautifulSoup(response.content, 'html.parser')

      # Find the div with the specified id
  highlight_elements = soup.find_all('a', {'class': 'ext-link-ajax'})
  data = []

  for i in highlight_elements:
      d = {"link": i.get('href'), "title": i.text}
      data.append(d)

      # Insert the data into MySQL table
  try:
      with mysql.cursor() as cursor:
              # Create a new record
          for d in data:
              sql = "INSERT INTO `latest_news` (`link`, `title`) VALUES (%s, %s)"
              cursor.execute(sql, (d['link'], d['title']))

          # Commit the changes to the database
      mysql.commit()
      print("Data inserted successfully!")
  except Exception as e:
          # Handle any errors that might occur
      print(f"Error inserting data: {e}")

      # Close the MySQL connection
  mysql.close()
