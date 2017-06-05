import requests

from bs4 import BeautifulSoup


class Scrapper(object):

    def getData(self):
        # url = raw_input("Enter a website to extract the URL's from: ")
        wiki = "https://en.wikipedia.org/wiki/List_of_state_and_union_territory_capitals_in_India"
        request = requests.get(wiki)
        # data = request.text
        soup = BeautifulSoup(request.text, "html.parser")
        import pdb; pdb.set_trace()


if __name__ == '__main__':
    scrap = Scrapper()
    scrap.getData()
