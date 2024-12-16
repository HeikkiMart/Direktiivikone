# Author: Heikki Martikainen

# Käytetyt moduulit
# 1 Requests avulla saadaan yhteys netissä olevaan lähtömateriaaliin
# 2 BeautifulSoup avulla luetaan HTML sisältö
# 3 Pandas tarvitaan dataframejen luomiseeen

import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd


# Listat direktiivien sisällön keräämiseen ja dataframejen luomiseen

articles = []
points = []
letters = []
subsections = []
contents = []

# Ilmaisut artiklojen, pointtien, kirjainten ja alakohtien tunnistamiseen tekstistä - Regular expressions to match the article, point, letter, and subsection patterns
# Etsittävät merkinnät ovat aina rivin alussa - Notation for expressing article, point etc. always in the begining of the line.
article_pattern = r'Article\s+(\d+)'  # Yhdistä "Artikla #" rivin alusta - Match "Article X" at the beginning of a line
point_pattern = r'^\(\d+\)|^\d+\.\s*'   # Yhdistä eri kirjoitusasut pointeille rivin alusta - Match "1.", "(1)", etc. at the beginning of a line
letter_pattern = r'^\([a-z]\)'       # Yhdistä kirjain rivin alusta - Match "(a)", "(b)", etc. at the beginning of a line
subsection_pattern = r'^\(i{1,3}|iv|v|vi{0,3}|ix|x\)'  # Yhdistä roomalaisin kirjaimin merkityt alakohdat rivin alusta. Match lowercase Roman numerals "(i)", "(ii)", etc. at the start
class Track:
    def __init__(self):
        
    # Muuttujat seuraamaan, mitä kohtaa tekstistä tällä hetkellä käsitellään - Variables to store the current article, point, letter, subsection, and content
        self.current_article = None
        self.previous_article = 0  # Pitää kirjaa viimeisimpänä käsitellystä artiklasta numerojärjestyksessä etenemistä varten. - Track the previous article number for sequential check
        self.current_point = None
        self.previous_point = 0  # Pitää kirjaa viimeisimpänä käsitellystä pointista numerojärjestyksessä etenemistä varten. - Track the previous point number for sequential check
        self.current_letter = None
        self.exletter = 'a'
        self.current_subsection = None
        self.current_content = []
        self.previous_letter = None

def append_content(track):
    if track.current_article:
        articles.append(track.current_article)
        points.append(track.current_point)
        letters.append(track.current_letter)
        subsections.append(track.current_subsection)
        contents.append(" ".join(track.current_content).strip())  # Yhdistä ja siivoa sisältö - Combine and clean the content
        track.current_content.clear()

def get_text(sites):
    track = Track()
    result = [] # lista tuloksena saaduille dataframeille
    for url in sites:
        # Avataan PDF-tiedosto pdfplumberilla - Open the PDF file using pdfplumber
        response = requests.get(url)
        soup = bs(response.content,'html.parser')
        # Etsitään HTML-sisällöstä tietty 'div'-elementti, jonka luokka on 'eli-subdivision' ja id 'enc_1'.
        #subsoup = soup.find('div', class_='eli-subdivision', id='enc_1')
        # Käydään järjestyksessä läpi jokainen sivu PDF-tiedostosta - Iterate through all the pages
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()

    # Break the text into individual lines and strip leading/trailing spaces from each line.
        lines = (line.strip() for line in text.splitlines())

        # Further split each line into phrases, removing extra spaces between them.
        # This handles cases where there are multiple spaces, ensuring each phrase is treated as a separate line.
        for line in lines:
            for phrase in line.split("  "):
                chunk = phrase.strip()
                if chunk:
                    article_match = re.match(article_pattern, chunk)
                    
                    if article_match:
                        # Poimitaan artiklan numero - Extract the current article number
                        current_article_num = abs(int(article_match.group(1)))
                        
                        # Varmistetaan että artikloissa edetään numerojärjestyksessä - Only consider this a new article if the article number is greater than the previous one
                        if current_article_num == 1 + track.previous_article:
                            # Kun nämä ehdot täyttyvät siirrtyään käsittelemään uutta artiklaa

                            append_content(track)  # Tallennetaan aikaisemmin kerätty tieto ennen uuden artiklan käsittelyn aloittamista - Save previous content before switching articles
                            track.current_article = article_match.group(1)
                            track.previous_article = current_article_num  # Päivitetään edeltävän artiklan arvo - Update the previous article number
                            track.current_point = None  # Resetoidaan käsiteltävän pointin, kirjaimen ja alakohdan arvo - Reset point, letter, and subsection when switching articles
                            track.previous_point = 0  # Resetoidaan viimeisimpänä käsitellyn pointin arvo - Reset the point sequence when a new article starts
                            track.current_letter = None
                            
                            track.current_subsection = None
                            track.current_content = []
                            continue

                    # Tarkistetaan viittaako rivin alku uuden pointin alkamiseen - Check if the line strictly indicates a new point (at the beginning of the line)
                    point_match = re.match(point_pattern, chunk)
                    if point_match:
                        # Poimitaan pointin numero - Extract the current point number
                        current_point_num = abs(int(re.findall(r'\d+', chunk)[0]))
                        
                        # Varmistetaan että pointeissa edetään numerojärjestyksessä - Only consider this a new point if the point number is greater than the previous one
                        if current_point_num == 1 + track.previous_point:
                            # Kun nämä ehdot täyttyvät siirrtyään käsittelemään uutta artiklaa
                            append_content(track)  # Tallennetaan aikaisemmin kerätty tieto ennen uuden pointin käsittelyn aloittamista - Save previous content before switching points
                            track.current_point = str(current_point_num)
                            track.previous_point = current_point_num  # Päivitetään edetävän pointin arvo - Update the previous point number
                            track.current_letter = None  # Resetoidaan käsiteltävät kirjain ja alakohdat - Reset the letter and subsection for a new point
                            track.current_subsection = None
                            track.exletter = 'a'
                            track.current_content = [chunk.strip(f"{track.current_point}.")]  # Aloitetaan tekstisisällön keräämine - Start a new content block for the point
                            continue

      

                    # Tarkistetaan viittaako rivin alku uuden kirjaimen alkamiseen - Check if the line strictly indicates a new letter (at the beginning of the line)
                    letter_match = re.match(letter_pattern, chunk)
                    if letter_match:
                        if track.current_letter != letter_match.group(0):
                            
                            append_content(track)  # Save previous content before switching letters
                            track.current_letter = letter_match.group(0)

                            track.current_subsection = None  # Reset subsection for a new letter
                            track.current_content = [chunk.split(track.current_letter)[-1].strip()]  # Start new content for the letter
                        continue

                    track.current_content.append(chunk)

            # Append the last piece of content
        append_content(track)
        # Create a pandas DataFrame
        df = pd.DataFrame({
            'Code #': [f"{x if x is not None else ''}{f"({y})" if y is not None else ''}{z if z is not None else ''}".strip() 
                    for x, y, z in zip(articles, points, letters)],
            'Article #': articles,
            'Point #': points,
            'Letter #': letters,
            'Subsection #': subsections,
            'Content': contents
        })
        # Kun yksi direktiivi on luettu kokonaan, tallennetaan tulos dataframe, tyhjennetään listat, ja siirrytään käsittelemään seuraavaa direktiiviä
        result.append(df)
        articles.clear()
        points.clear()
        letters.clear()
        subsections.clear()
        contents.clear()
        track = Track()
    return result