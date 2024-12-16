# Author: Heikki Martikainen

import requests
import pandas as pd
import re
from bs4 import BeautifulSoup as bs
import sys

# Tekstin siivoamiseen käytettävä funktio
def clean_text(text):
    text = re.sub(r'\b(article|articles|point|points|and|,|letter|letters|:)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*(\(\d+\)|\(\w+\))', r'\1', text)
    text = re.sub(r':', '', text)
    text = re.sub(r'[,\s]+', ' ', text).strip()
    return text

############################### VERTAILUTAULUKKO ####################################

# Vertailutaulukon poimiminen perustuu siihen oletukseen, että se on aina uuden direktiivin viimeisenä liitteenä (näin vaikutti olevan kaikissa kehityksen aikana tarkastetuissa tiedostoissa)
# Esim. HTML-tie
def get_table(url_table,cols):
    response = requests.get(url_table)
    soup = bs(response.content,'html.parser')
    tables = soup.find_all('table')

    # Select the last table
    table = tables[-1]

# Lista 'cols' määrää vertailutaulukosta luettavat sarakkeet. Sarakkeiden määrä ja järjestys voi vaihdella tapauksesta riippuen
# Ota huomioon kun vaihdat listan arvoja, että Pythonissa listan indeksointi alkaa luvusta 0
# Jos esim. haluat lukea kaksi ensimmäistä saraketta taulukosta, päivitä cols listan arvoiksi [0,1]
# Tallenna muutokset.


    data = []
    for row in table.find_all('tr'):
        columns = [col.text for col in row.find_all(['td', 'th'])]
        data.append(columns)
    #Muutetaan lista Pandas dataframeksi Convert the list of lists to a Pandas DataFrame
    tbl_df = pd.DataFrame(data[1:], columns=data[0])
    tbl_df = tbl_df.map(lambda x: x.replace("\n",""))
    try:
        # valitaan käyttäjän antamat sarakkeet 
        list1 = tbl_df.iloc[:,cols[0]-1].values.tolist()
        list2 = tbl_df.iloc[:,cols[1]-1].values.tolist()
    # Jos taulukon lukeminen epäonnistuu, johtuu se luultavimmin sarakkeiden indexi virheestä. Jos yritetään lukea sarakkeita jota ei ole, nostetaan IndexError 
    except (IndexError):
        print(f"Error: Direktiivikone yrittää lukea vertailutaulukon sarakkeet {cols[0]+1} ja {cols[1]+1}. Tarkista taulukon muoto.")
        sys.exit()

    # cpy muuttujiin jemataan Esim artiklan numero, kun taulukon seuraavilla riveillä on tämän alakohtiin liittyvää tietoa joka on yhdistettävä koodiin esim. 1(1), 1(2) ja 1(2)(a) jne.
    cpy1 = ""
    cpy2 = ""

    # Muokataan vertailutaulukon muoto sellaiseksi, että sitä voidaan käyttää direktiivien teksitsisältöjen yhdistämiseen
    for i in range(0,len(list1)):
        list1[i] = list1[i].lower()
        list2[i] = list2[i].lower()
        if "article" in list1[i]:
            cpy1 = list1[i]
        if list1[i] == "-":
            list1[i] = "-"
        elif "point" in list1[i] and "letter" in list1[i+1]:
            cpy11 = str(cpy1+list1[i])
            continue
        elif "letter" in list1[i] or "point" in list1[i]:
            list1[i] = str(cpy1+" "+list1[i])
        
        if "article" in list2[i]:
            cpy2 = list2[i]
        elif list2[i] == "-":
            list2[i] = ""
        elif "letter" in list2[i] or "point" in list2[i]:
            list2[i] = str(cpy2+" "+list2[i])  
        
    
    rel_df = pd.DataFrame({'Code C': list1[1:],'Code P': list2[1:]})
            
        



    rel_df['Code C'] = rel_df['Code C'].apply(clean_text)
    rel_df['Code P'] = rel_df['Code P'].apply(clean_text)
    return rel_df