import requests
import re

from bs4 import BeautifulSoup
from pprint import pprint as pp


class Scrapper(object):

    def __init__(self):
        self.county_title = []
        self.population = []
        self.constituencies = []
        self.counties = {}


    def get_data(self):
        # url for wikipedia page containing kenya's counties and their constituents
        wiki = "https://en.m.wikipedia.org/wiki/List_of_constituencies_of_Kenya"
        request = requests.get(wiki)  # request data from the url
        data = request.text  # get data from the request
        # make a soup object from the data
        soup = BeautifulSoup(data, "html.parser")
        # get div with county data
        county_data = soup.find('div', class_='mf-section-1')

        for child in county_data.children:
            if child.name == 'h4' and child['class'][0] == 'in-block':
                self.county_title.append(child.find(class_='mw-headline').a.text.encode('utf-8'))
            if child.name == 'ul':
                self.population.append(child.find_all('li')[0].text.encode('utf-8'))
                try:
                    self.constituencies.append(child.find_all('li')[2].text.encode('utf-8')[:-1])
                except:
                    continue
            if child.name == 'table' and child['class'][0] == 'wikitable':
                nairobi_county = 'Constituencies:'
                for constituent in child.find_all('th'):
                    if re.match(r'^[0-9]', constituent.text):
                        nairobi_county = nairobi_county + ' ' + constituent.text.encode('utf-8') + ','
                self.constituencies.append(nairobi_county[:-1])
        self.clean_data()

    def clean_data(self):
        kenya = zip(self.county_title, self.population, self.constituencies)
        for county in kenya:
            self.counties[county[0]] = {
                "population (2009)": county[1].split()[2],
                "constituencies": [cnty.split('.')[-1] for cnty in county[2].split(',')]
                }
        pp(self.counties)

if __name__ == '__main__':
    scrap = Scrapper()
    scrap.get_data()
