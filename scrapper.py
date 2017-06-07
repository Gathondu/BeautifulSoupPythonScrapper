import requests
import re

from bs4 import BeautifulSoup


class Scrapper(object):

    def get_data(self):
        # url for wikipedia page containing kenya's counties and their constituents
        wiki = "https://en.m.wikipedia.org/wiki/List_of_constituencies_of_Kenya"
        request = requests.get(wiki)  # request data from the url
        data = request.text  # get data from the request
        # make a soup object from the data
        soup = BeautifulSoup(data, "html.parser")
        # get div with county data
        county_data = soup.find('div', class_='mf-section-1')
        county_title = []
        population = []
        constituencies = []

        for child in county_data.children:
            if child.name == 'h4' and child['class'][0] == 'in-block':
                county_title.append(child.find(class_='mw-headline').a.text)
            if child.name == 'ul':
                population.append(child.find_all('li')[0].text)
                try:
                    constituencies.append(child.find_all('li')[2].text)
                except:
                    continue
            if child.name == 'table' and child['class'][0] == 'wikitable':
                for constituent in child.find_all('th'):
                    if re.match(r'^[0-9]', constituent.text):
                        constituencies.append(constituent.text)


if __name__ == '__main__':
    scrap = Scrapper()
    scrap.get_data()
