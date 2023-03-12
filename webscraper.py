import requests
from bs4 import BeautifulSoup


def scraper():
  # Make a request to the website
  response = requests.get('https://www.india.gov.in/news_feeds?rand?')

      # Parse the HTML content using BeautifulSoup
  soup = BeautifulSoup(response.content, 'html.parser')

      # Find the div with the specified id
  highlight_elements = soup.find_all('a', {'class': 'ext-link-ajax'})
  data = []

  for i in highlight_elements:
      d = {"link": i.get('href'), "title": i.text}
      data.append(d)
  return data
