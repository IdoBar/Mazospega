

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 16:34:57 2020

@author: Ido Bar
"""


from pyzotero import zotero
import re, os, csv, configparser
import easygui as eg
from urllib.error import HTTPError

# get zotero connection details from ~/.zoterorc file

config = configparser.ConfigParser()
zotero_config_file=eg.fileopenbox(msg='Please select Zotero configuration file (which should include your API key, Library id and type, see documentation for details.)', title='Zotero config file', filetypes =["*.*", "All files"], default="%s\\*.zotero*" % os.getcwd())
config.read(zotero_config_file)
api_key = config['zotero']['api_key'] # Use your Zotero api key here
# print('api_key: ' + api_key)
library_id = config['zotero']['library_id'] # Use your Zotero library id here
# print('library_id: ' + library_id)
library_type = config['zotero']['library_type'] # set to 'group' if you are accessing a shared group library
# print('library_type: ' + library_type)

# read these from a csv file...
Items_input = [] # empty input list
updated_entries=[] # empty output titles list
# Prompt for manual input
User_input=eg.enterbox(msg='''
    Enter genus names to be searched and italicized, seperated by commas and press enter.
    Example: Botrytis, Cicer, Lens,Oryza, etc.
    If genus names are in CSV file, enter CSV and wait to be prompted to open the file.''', title='Input Genus names')



# File input
if User_input.upper() == 'CSV':
    csv_input_file=eg.fileopenbox(msg='Please select csv input file', title='CSV input file', filetypes =["*.csv", "CSV files"], default="%s\\*.csv" % os.getcwd())
   # csv_input_path=ntpath.split(csv_input_file)[0]
    with open(csv_input_file, 'rb') as fileread:
        inputreader = csv.reader(fileread)
        for row in inputreader:
            Items_input.append(row[0])
    fileread.close()

# Use manual input data instead of file
else:
    Items_User_input = User_input.split(',')
    for z in Items_User_input:
        Items_input.append(z.strip())
   
# plantsPathogens = ["Cryptobranchus", "Fusarium", "Mycosphaerella", "Pochonia", "Pogona", "Nannizziopsis", "Armillaria", "Parastagonospora", "Pseudoperonospora", "Phytophthora", "Heterobasidion", "Cochliobolus", "Rhynchosporium", "Aspergillus", "Ascochyta", "Sclerotinia", "Botrytis", "Cicer", "Lens","Oryza", "Eucalyptus", "Arabidopsis", "Vigna", "Phaseolus", "Vicia"]
# aquaticSpecies = ["Oreochromis", "Dicentrarchus", "Pagrus", "Gonostoma","Tursiops", "Gadus", "Danio", "Acanthosentis", "Oryzias", "Seriola", "Cyprinus", "Euthynnus", "Solea", "Nibea", "Thunnus thynnus","Argyrosomus", "Thunnus", "Misgurnus", "Oncorhynchus", "Epinephelus", "Rachycentron", "Clarias", "Tetraodon", "Proterocara", "Latimeria", "Oithona", "Sarda", "Glaucosoma", "Scomberomorus", "Allium", "Aulopus", "Plecoglossus", "Anguilla", "Hoplias", "Poecilia", "Sardinops", "Cyprinus", "Acanthopagrus", "Mus", "Rana", "Chlamys", "Anas", "Nerita", "Nodipecten", "Megalobrama", "Squalus","Mytilus", "Scomber", "Acipenser", "Torpedo", "Takifugu", "Sparus","Morone", "Lepomis","Cichlasoma", "Limanda", "Polyprion","Chelon","Paralichthys" ,"Litopenaeus" ,"Rutilus","Ictalurus" ,"Pelteobagrus","Macrobrachium","Amphiprion","Arapaima", "Huso", "Sciaenops", "Lutjanus", "Perca", "Pangasius", "Latris","Scophthalmus", "Macquaria", "Pleuronectes", "Lates", "Clarias", "Salmo", "Pisum", "Pinctada", "Cristaria", "Mugil", "Chanos", "Pangasius", "Halichoeres"]

# connect to Zotero
try:
    zot = zotero.Zotero(library_id, library_type, api_key)
except HTTPError:
    print("Error: Could not connect to Zotero library")
    exit(0)
for genus in Items_input:
    
    # oldValue = "Ascochyta"
    search_string = r"(.*(?<!>)\b)(%s [a-z]+)(\b(?!<).*$)" % genus
    regex = re.compile(search_string)
    # print("Search string: r(.+[^>])(%s \\w+)(([^w]*\\w?$))" % genus)
    # regExFilt = "(.+[^>])(" + oldValue + " \\w+)(([^w]*\\w?$))"
    try:
        items = zot.everything(zot.top(q=genus))
    except HTTPError:
        print("Error: Could not connect to Zotero library to search for titles with %s." % genus)
        next(genus)
    
    # print(len(items))
    print("%d items containing %s in their title were found in your Zotero library, processing them now." % (len(items), genus))
    # we've retrieved the latest five top-level items in our library
    # we can print each item's item type and ID
    for i, item in enumerate(items):
        genus_match = re.match(search_string, item['data']['title'])
        if genus_match:
            
        #re.search(r"(.+[^>])(%s [a-z]+)(([^w]*\w?$))" % genus, item['data']['title']):
            newSpecies =  re.sub(search_string , '<i><span class="nocase">\g<2></span></i>', item['data']['title'])
            newTitle = re.sub(search_string, '\g<1><i><span class="nocase">\g<2></span></i>\g<3>', item['data']['title'])
    # Ask interactively if the entry should be changed
            annotYN=eg.boolbox(msg='%d. Do you want to italicize species name in title "%s"?\nFrom this: %s To this: %s' % (i+1, item['data']['title'], genus_match[2], newSpecies), title='Italicize "%s" in Zotero Titles' % genus, choices=('Yes', 'No'))
            if annotYN:
                print('Updating entry %s' % item['key'])
                item['data']['title'] = newTitle
                updated_entries.append(newTitle)
                zot.update_item(item)
if updated_entries:
    print('The following titles were updated:')#, '\n '.join(map(str, updated_entries)))            
    for j, title in enumerate(updated_entries):
       print('%s. %s.\n' % (j+1, title))            
    # print('The following entries were updated for Genus , '.join(map(str, updated_entries)))
    
