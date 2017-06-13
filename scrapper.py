import json
import requests
import re

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from pprint import pprint as pp


class Scrapper(object):
    def __init__(self):
        self.county_title = []
        self.population = []
        self.constituencies = []
        self.counties = []
        self.bulk_data = []
        self.ES_HOST = "https://elastic:cUWiP2WUvkz61Kcihvg3PZd2@6697ac01589eb72a5f7d26f94e7b5c8d.us-east-1.aws.found.io:9243"
        self.INDEX_NAME = "counties"
        self.TYPE_NAME = "county"
        self._ID = 1

    def get_data(self):
        """
        get data from the url
        """
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
                # get the county name minus the county word
                self.county_title.append(child.find(class_='mw-headline').a.text.encode('utf-8').split()[0])
            if child.name == 'ul':
                self.population.append(child.find_all('li')[0].text.encode('utf-8'))
                try:
                    # remove the trailing full stop
                    self.constituencies.append(child.find_all('li')[2].text.encode('utf-8')[:-1])
                except:  # ignore error relating to html tags
                    continue
            # get nairobi constituencies from a table and format it to ba similar to other data
            if child.name == 'table' and child['class'][0] == 'wikitable':
                nairobi_county = 'Constituencies:'
                for constituent in child.find_all('th'):
                    if re.match(r'^[0-9]', constituent.text):
                        nairobi_county = nairobi_county + ' ' + constituent.text.encode('utf-8') + ','
                # remove trailing comma
                self.constituencies.append(nairobi_county[:-1])

    def clean_data(self):
        """
        clean the data and put it into a list of dictionaries
        """
        kenya = zip(self.county_title, self.population, self.constituencies)
        for county in kenya:
            self.counties.append({
                "title": county[0],
                "population": county[1].split()[2][:-1],  # population as of 2009, remove trailing full stop
                "constituencies": [cnty.split('.')[-1] for cnty in county[2].split(',')]
                })

    def upload_data(self):
        """
        upload data to elastic search
        """
        for county in self.counties:
            # all bulk data need meta data describing the data
            meta_dict = {
                "index": {
                    "_index": self.INDEX_NAME,
                    "_type": self.TYPE_NAME,
                    "_id": self._ID
                    }
                }
            self.bulk_data.append(meta_dict)
            self.bulk_data.append(json.dumps(county))
            self._ID += 1
        esclient = Elasticsearch([self.ES_HOST])
        if esclient.indices.exists(self.INDEX_NAME):
            print "deleting '%s' index..." % self.INDEX_NAME
            res = esclient.indices.delete(index=self.INDEX_NAME)
            print " response: '%s'" % res

        # since we are running locally, use one shard and no replicas
        request_body = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
                }
            }
        print "creating '%s' index..." % self.INDEX_NAME
        res = esclient.indices.create(index=self.INDEX_NAME, body=request_body)
        print " response: '%s'" % res

        # bulk index the data and use refresh to ensure that our data will be immediately available
        print "bulk indexing..."
        res = esclient.bulk(index=self.INDEX_NAME, body=self.bulk_data, refresh=True)
        pp(res)


if __name__ == '__main__':
    scrap = Scrapper()
    scrap.get_data()
    scrap.clean_data()
    scrap.upload_data()
