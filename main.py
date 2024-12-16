# Author: Heikki Martikainen

import textExtract
import tableExtract
import combine
import openpyxl
from openpyxl.styles import Alignment

def main():
    print("\nTerveetuloa Direktiivikoneeseen.\n")
    print("Direktiivikone tarvitsee EUR-Lex URL-osoitteet käsiteltäviin dokumentteihin.")
    current = input("Anna voimassaolevan direktiivin URL-osoite: ")
    print("\nDirektiivikone olettaa, että vertailutaulukko löytyy uudesta ehdotuksesta, viimeisenä taulukkona.")
    proposal = input("\nAnna uuden ehdotuksen URL-osoite: ")
    print("\nDirektiivikone tarvitsee vertailutaulukosta 2 luettavaa saraketta. Ensin voimassaoleva, sitten uusi.")
    inp = input("Anna luettavat sarakkeet välilyönnillä erotettuna: ")
    settings = int(input("Jos haluat tekstisisällön Artiklan tarkkuudella, vastaa 1: "))

    cols = list(map(int, inp.split()))
    sites = [current,proposal]
    print("Luetaan tekstit direktiiveistä")
    result = textExtract.get_text(sites)
    print("Luetaan vertailutaulukko")
    rel_df = tableExtract.get_table(sites[1], cols)
    print("Yhdistetään tiedot vertailutaulukon mukaisesti")
    df_combined = combine.combine(result[0],result[1],rel_df,settings)
    table_path = 'C:/Users/03272740/Projektit/py/Direktiivikone/Direktiivikone.xlsx'
    df_combined.to_excel(table_path, index=False) # , encoding='utf-8-sig'
    print(f'Tiedosto tallennettu osoitteeseen {table_path}')


    # Muotoillaan Excel-työkirja
    wb = openpyxl.load_workbook(table_path)
    sheet = wb.active  

    # Sarakkeiden leveydet
    sheet.column_dimensions['A'].width = 10
    sheet.column_dimensions['B'].width = 10
    sheet.column_dimensions['C'].width = 100
    sheet.column_dimensions['D'].width = 10
    sheet.column_dimensions['E'].width = 10
    sheet.column_dimensions['F'].width = 100

    # Tekstin rivitys ja teksti keskelle solua
    wrap_alignment = Alignment(wrap_text=True,vertical='center')

    # Iterate through all cells and apply formatting
    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = wrap_alignment

    # Tallenetaan muutokset
    wb.save(table_path)
    print("Direktiivikoneen ajo suoritettu.")

main()
