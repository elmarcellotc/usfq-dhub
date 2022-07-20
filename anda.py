#
# Author: Marcello Coletti; USFQ Data Hub
#
# Contact: coletti.marcello@gmail.com; +593939076444 (Ecuador)
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
import magic
import re
import time

start = time.time()

def get_soup(url, get_content=True, url_type='html.parser'):
    
    # BeautifulSoup parses the content of the html document. This proccess is repeated along all this
    # script.
    
    if get_content == True:
        page = requests.get(url).content
    else:
        page = requests.get(url).text

    soup = BeautifulSoup(page, url_type)

    return soup

def get_next_pages(url):
    links_set = [url]

    # There are more than one page with the variables descriptions. Then, it is necessary to
    # get all of them.
    
    k = len(links_set)
    j = 0
    
    # The while loop will finish when the program has finished to scrap pages in the catalog.
    # At this point, the k counter will stop increasing. j counter will get alllinks of
    # "next page" in the catalog, and this is why at the last page j is going to be equal to k.
    
    # While k != j, the loop is recolecting the links of the different pages in the catalog.
    
    while k != j:
        k = len(links_set)
        url = links_set[-1]
        soup = get_soup(url)

        for div in soup.findAll("div", {"class","pager"}):
            for content in div.contents:
                if "Siguiente" in content.text and content.attrs['href'] not in links_set:
                    links_set.append(content.attrs['href'])
                    print(f'{j} links in set')
                    j = len(links_set)

    return links_set
               

def get_next_pages_2(url):
    links_set = [url]
    j=0
    
    k = 0
    
    soup = get_soup(url)
    
    for div in soup.findAll("ul", {"class", "variable-pager"}):
        for soup2 in div.findAll("li"):
            for content in soup2.contents:
                
                try:
                    new_link = content.attrs['href']
                    links_set.append(new_link)
                    print(new_link)
                    print(f'{len(links_set)} links found')
                    
                    
                except:
                    new_link = content
                    
    return links_set

class Realization():

    def __init__(self):

        self.id = "This is the title found in ANDA catalog"
        self.url = "url"                              # This is the url of the realization.
        self.date = 0                               # Date of realization.
        self.divs = []                              # List of the names of survey's divisions.
        self.description_url = []                   # List of the variables and their description url.

    def split_year_from_name(self, name, edate):
        name = re.sub(r'\([^)]*\)', '', name)
        edate = edate.strip()

        # In the case of ANDA system, we know that the name of the survey can be separate after the year of realization.
        
        name = name.replace('.',' ')
        name = name.replace('-',' ')
        name = name.replace('_',' ')
        name = name.replace(':','')
        name = name.split(' ')
        date = 0
        special_case = []
        roman = ["I","V", "X", "L", "M", "C"]
        roman_found = []

        for w in range(len(name)):
            name[w] = name[w].upper()
            counter = 0
            for l in name[w]:
                if l not in roman:
                    counter+=1

            if counter == 0:
                roman_found.append(name[w].lower())

            h = name[w]
            
            
            name[w] = unidecode(name[w])
            name[w] = name[w].lower()
            
            if h == name[w]:
                special_case.append(name[w])                
            
            if len(name[w]) == 4 and name[w].isnumeric():
                if int( name[w]) > date and name[w-1] not in ["base:", ":", "base", "ano", "de"]:
                    date = int( name[w])
        
        for r in roman_found:
            if r in name:
                name.remove(r)

        if date == 0:
            date = edate  
        
        
        name = " ".join(name)
        self.date = date
        self.id = name

def gen_realization_data(links_set):
    
    print('#####################################')
    print('#####################################')
    print('Realizations data:')
    print('#####################################')
    print('#####################################')
    
    realizations = []

    for url in links_set:
        soup = get_soup(url)

        for div in soup.findAll("div", {"class", "survey-row"}):

            realization = Realization()
            realization.url = div.find("a")["href"]
            realization.id = (div.find("a").text).strip()
            print(realization.id)
            
            realization.split_year_from_name(realization.id, div.find("div", {"class", "study-country"}).text )
            
            realizations.append(realization)

    return realizations

def find_descriptions(realizations):
    import os

    print('#####################################')
    print('#####################################')
    print('Seaching for survies divisions:')
    print('#####################################')
    print('#####################################')

    if not os.path.exists("ANDA"):
            os.mkdir("ANDA")

    for realization in realizations:

        dir = r'ANDA'+'/'+realization.id
        
        if not os.path.isdir(dir):
            os.mkdir(dir)

        soup = get_soup(realization.url)

        print(f'\n{realization.id}')
        
        for div in soup.findAll("a"):
            if div.text == "Descripción de Variables":
                son = get_soup(div["href"])

                for child in son.findAll("li", {"class", "sub-item"}):
                    brother = child.find("a")
                    
                    realization.description_url.append( get_next_pages_2( brother["href"] ) )
                    
                    title = brother["title"]
                    print(title)
                    
                    title = "".join([v for v in title if v != "."])
                    realization.divs.append(title)
                    dir = r'ANDA'+'/'+realization.id+'/'+title
        
                    if not os.path.isdir(dir):
                        os.mkdir(dir)

                    print(realization.divs[-1])
        


def get_descriptions(realizations):
    
    print('#####################################')
    print('#####################################')
    print('Geting vars descriptions baby!')
    print('#####################################')
    print('#####################################')
    
    h = 0
    g = []
    
    for realization in realizations:
        print(f'\n{realization.id}')

        for i in range(len(realization.divs)):
            print(realization.divs[i])
            
            for j in realization.description_url[i]:
                
                soup = get_soup(j)

                for div in soup.findAll("td", attrs={"class": "var-td"}):
                    var_name = div.find("a")
                    
                    if var_name == None:
                        continue

                    else:
                        print(var_name)
                        son = get_soup(var_name["href"])
                        var_name = var_name.text
                    
                    try:
                        my_text = son.find("div", {"class": "tab-body"}).get_text()
                        m = magic.Magic(mime_encoding=True)
                        encoding = m.from_buffer(my_text)
                        
                        with open(r'ANDA'+'/'+realization.id+'/'+realization.divs[i]+'/'+var_name+'.txt', 'w', encoding='utf-8') as f:
                            f.write(my_text)
                        
                        print(var_name+" created")

                    except:
                        print("Couldn't gen variable "+var_name+" from "+realization.id+" in "+realization.divs[i])
                        with open(r'ANDA'+'/'+realization.id+'/'+realization.divs[i]+'/'+var_name+'.txt', 'w') as f:
                            f.write("Empty")
                        
                        g.append(var_name+" from "+realization.id+" in "+realization.divs[i])    
                        h+=1
                        
    with open("Report.txt", "w") as f:
        
        f.write(f'There are {h} empty variables. There are:')
        for i in g:
            f.write(f'\n {i}')

            
print("Starting program...")

links_set = get_next_pages('https://anda.inec.gob.ec/anda/index.php/catalog')
realizations = gen_realization_data(links_set)
find_descriptions(realizations)
get_descriptions(realizations)

end = time.time()
from time import strftime
from time import gmtime

with open("Time.txt", "w") as f:
    f.write('The script took '+ strftime("%H:%M:%S", gmtime(end)) + ' to complete itself')