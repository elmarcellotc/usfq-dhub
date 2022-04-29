#
# Author: Marcello Coletti; USFQ Data Hub
#
# Contact: coletti.marcello@gmail.com; +593939076444
#


# Description:

# Thise code is to download the description of the maximum possible Data Bases in INEC ANDA webb.
# https://anda.inec.gob.ec/anda/index.php/catalog#_r=&collection=&country=&dtype=&from=2007&page=1&ps=100&sk=&sort_by=titl&sort_order=&to=2022&topic=&view=s&vk=
# With this, the USFQ DHub will be able to automitize the proccess of repeated variables with different names using
# my other code named varSelector.py and its dependencies.
#
#  However, this code is made to also download description of Data Bases in similar pages to ANDA system. It means, if a web page has
# a class of the of the Data Base and, in the Data Base sub page a class for the variable and it description, this code will
# be useful to scrappy it.

# Required libraries:
import requests # To download the html
from bs4 import BeautifulSoup
from unidecode import unidecode # To parse the html

class Finder():

    def __init__(self, url, page_name):
        self.id = page_name                     # This is the name of the central to scrappy.
        self.url = url                          # The current url that is being scraped.
        self.soup = "Didn't create soup yet."   # The current html parsed from the current
        self.survies_set = [[], [], [], [], []] # A vector of the survies name,
                                                # one with their corresponding URLs, one with the
                                                # tag of the survey, other with the year of realization, and the
                                                # last one with the link of the descriptions (if have it).
        self.links_set = [self.url]             # The links of the pages of the central catalog
        self.current_survey = []                # The current survey
        self.survies_names = []                 # A vector of the unique survies name
        self.survies_tags = []                  # A vector of the unique survies tags
        self.survies_divisions = []
        
        self.get_next_pages()
        print(f'\nThere are {len(self.links_set)} catalog pages.\n')
        
        self.get_survy_descriptions()
        self.get_sub_survies()

    def get_soup(self, get_content=True, url_type='html.parser'):
        
        # BeautifulSoup parses the content of the html document. This proccess is repeated along all this
        # script.
        
        if get_content == True:
            html_page = requests.get(self.url).content
        else:
            html_page = requests.get(self.url).text
        self.soup = BeautifulSoup(html_page, url_type)

    def get_next_pages(self):
        
        # There are more than one page with the variables descriptions. Then, it is necessary to
        # get all of them.
        
        k = len(self.links_set)
        j = 0
        
        # The while loop will finish when the program has finished to scrap pages in the catalog.
        # At this point, the k counter will stop increasing. j counter will get alllinks of
        # "next page" in the catalog, and this is why at the last page j is going to be equal to k.
        
        # While k != j, the loop is recolecting the links of the different pages in the catalog.
        
        while k != j:
            k = len(self.links_set)
            self.url = self.links_set[-1]
            self.get_soup()

            for div in self.soup.findAll("div", {"class","pager"}):
                for content in div.contents:
                    if "Siguiente" in content.text and content.attrs['href'] not in self.links_set:

                        self.links_set.append(content.attrs['href'])
                        j = len(self.links_set)

    def split_year_from_name(self, name):
        
        # In the case of ANDA system, we know that the name of the survey can be separate after the year of realization.
        
        name = name.replace(',',' ')
        name = name.replace('.',' ')
        name = name.replace(';',' ')
        name = name.split(' ')
        date = 0
        
        for w in range(len(name)):
            g = 0
            name[w] = unidecode(name[w])
            name[w] = name[w].lower()
            if len(name[w]) == 4 and name[w].isnumeric():
                g = w
                if int( name[w]) > date:
                    date = int( name[w])
                break
                
            elif '-' in name[w] and len(name[w]) == 9:
                if name[w].split('-')[0].isnumeric() and name[w].split('-')[1].isnumeric():
                    if int(name[w].split('-')[1]) > date:
                        date = int(name[w].split('-')[1])
                    break
        
        print(name, date)
        
        return date, date
    
    def get_survy_descriptions(self):
        
        # Each page of the catalog have its own set of survies. This function gets the links of all of them.
        from unidecode import unidecode
        for url in self.links_set:
            self.url = url
            self.get_soup()

            for div in self.soup.findAll('h2', {'class', "title"}):
                
                for content in div.findAll('a'):
                    self.survies_set[1].append(content.attrs['href'])           # This get the link of the survey
                    original_name = content.attrs['title']
                    a, b = self.split_year_from_name(original_name)
                    self.survies_set[0].append(a)
                    self.survies_set[3].append(b)
                
                for sdiv in self.soup.findAll('div', {'class', "owner-collection"}):
                    tag = sdiv.find('a').text
                    if tag not in  self.survies_tags:
                        self.survies_tags.append(tag)                           # This get update the total tags list
                    self.survies_set[2].append(tag)
                    
        exit()                   
        
        print('#####################################')
        print(f'\nStarting with survies scrapping proccess:\n')
        print('#####################################')
        self.survies_set[4] = [None] * len(self.survies_set[0])
        
        for s in range(len(self.survies_set[1])):
            print(f'\nSearching variables description in survey:\n"{self.survies_set[0][s]}", realization: {self.survies_set[3][s]}')
            self.url = self.survies_set[1][s]
            self.get_soup()

            for div in self.soup.findAll("li"):
                
                for content in div.contents:
                    
                    if "Descripción de Variables" in content.text:
                        self.survies_set[4][s] = content.attrs['href']
                        print("Found variables description:\n",self.survies_set[4][s],'\n')
                        
    def get_sub_survies(self):
        import os
        if not os.path.exists('ANDA'):
            os.mkdir('ANDA')        
        
        print('#####################################')
        print('#####################################')
        print(f'\nSeaching for survies divisions:\n')
        print('#####################################')
        print('#####################################') 
        k = len(self.survies_set[4])
        
        for i in range(k):
            if self.survies_set[4][i] != None:
                
                dir = 'ANDA'+'\\'+self.survies_set[2][i]
                
                if not os.path.exists(dir):
                    os.mkdir(dir)
                
                dir = dir + '\\'+self.survies_set[0][i]
                
                if not os.path.exists(dir):
                    os.mkdir(dir)
                
                self.url = self.survies_set[4][i]
                self.get_soup()
                
                print('#####################################')
                print(f'\n{self.survies_set[0][i]} has the next divisions:\n')
                print('#####################################')
                
                for div in self.soup.findAll('li', {'class', "sub-item"}):
                    for content in div.contents:
                        
                        # Each survey has a division of how was made. For example,
                        # a survey of the public workers could be made to workers of the National Government,
                        # to provincial workers, town public workers, etc. Each of them has its own
                        # variables and description.
                        
                        self.url = content.attrs['href']
                        print(content.attrs['title'])
                        
                        dir = '\\'+content.attrs['title']
                        if not os.path.exists(dir):
                            os.mkdir(dir)
                            
                        if [self.survies_set[0][i], content.attrs['title']] not in self.survies_divisions:
                            self.survies_divisions.append([self.survies_set[0][i], content.attrs['title']])
                            print(self.survies_divisions[-1],len(self.survies_divisions))

    # def get_vars_description(self, url):                               # The description returns the variable name,
    #                                                              # the var description, definitions, and
    #                                                              # categories (ie: 1 means urban, 2 means rural)
    #                                                              # Those items are collected in h, wich is going to
    #                                                              # be append in self.survies_set[4][s] in function
    #                                                              # self.get_survy_descriptions()
    #     self.get_soup()
    #     self.soup.original_encoding
    #     k = 0
    #     h = [None, None, [], []]

    #     for div in self.soup.findAll('td', {'class',"var-td"}):
    #         k+=1

    #         if k == 1:
    #             h[k-1]= div.text
                
    #             for cont in div.contents:
    #                 soup_2 = get_soup(cont.attrs['href'])
                    
    #                 for temp in soup_2.findAll('div',{'style': 'padding:5px;'}):
    #                     s = str(temp.find_next_sibling)
    #                     start = s.find(">") + len(">")
    #                     end = s.find("</")             
    #                     h[2].append(s[start:end])
                    
    #                 r = 0
    #                 r_max = None
    #                 for temp in soup_2.findAll('table',{'class', 'varCatgry'}):
    #                     temp = temp.find_next_sibling
    #                     if '<th align="left">' in str(temp):
    #                         r_max = str(temp).count('<th align="left">')
    #                     temp = BeautifulSoup(str(temp), 'html.parser')
                        
    #                     if r_max != None and r_max > 0:
    #                         r = 0
    #                         for i in range(r_max):
    #                             h[3].append([])
                            
    #                         for temp2 in temp.findAll('td'):
    #                             h[3][r].append(temp2.text.strip())
    #                             r+=1
    #                             if r == r_max: r = 0
                                
    #                     else:
    #                         h[3] = None
                        
    #             h[2] = ' '.join(h[2])
    #             h[2] = h[2].replace("<br/><br/>",'')
    #             h[2] = h[2].replace('<div class="xsl-caption">','')

    #         elif k == 2:
    #             h[k-1]= div.text.strip()

    #         else:
    #             k = 0
    #             h = [None, None, [], []]
    #    returns h

url = 'https://anda.inec.gob.ec/anda/index.php/catalog'

Finder(url, "ANDA")