#################################
##### Name: Kristian Shin
##### Uniqname: shinkris
#################################

from bs4 import BeautifulSoup
import requests
import json
import re
import sqlite3

###########################################################################
###CACHE DICTIONARY, FILENAME, AND FUNCTIONS FOR CACHING POKEDEX ENTRIES###
###########################################################################
CACHE_FILENAME = "pokedex_cache.json"
CACHE_DICT = {}

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

#################################################
###POKEMON CLASS AND CONSTRUCTING DICTIONARIES###
#################################################

class Pokemon:
    '''A Pokemon

    Instance Attributes
    --------------
    name: string
    The name of the Pokemon

    dex: integer
    The number of the Pokemon. Ranges from 001 to 897

    types: string
    Pokemon can at least 1 type of 18. Pokemon can have up to two types simultaneously.

    HP: integer
    Amount of damage a Pokemon can take before it is knocked out.

    ATK: integer
    Amount of physical damage a Pokemon can inflict when attacking.

    DEF: integer
    Amount of physical damage a Pokemon can resist when being attacked.

    SPATK: integer
    Amount of special damage a Pokemon can inflict when attacking.

    SPDEF: integer
    Amount of special damage a Pokemon can resist when being attacked.

    SPD: integer
    Number that determines turn order in combat along with other minor factors.

    classification: integer
    Unique classifier for a Pokemon. Example: Bulbasaur is the "Seed" Pokemon

    height: integer
    How tall a Pokemon is in feet or meters

    weight: integer
    How heavy a Pokemon is in lbs or kilograms.

    genderR: string
    Male to Female ratio by percentage. Pokemon can be sexless.
    '''

    def __init__(self, name="No Name", dex="No Dex", types="No Types", HP = "No HP", ATK = "No ATK", DEF = "No DEF", SPATK = "No SPATK", SPDEF = "No SPDEF", SPD = "No SPD", classification="No Classification", height = "No Height", weight = "No Weight", genderR = "No GenderR"):
        self.name = name
        self.dex = dex
        self.types = types
        self.hp = HP
        self.attack = ATK
        self.defense = DEF
        self.special_attack = SPATK
        self.special_defense = SPDEF
        self.speed = SPD
        self.classification = classification
        self.height = height
        self.weight = weight
        self.genderRatio = genderR

    # def toJson(self):
    #     with open('result.json', 'w') as fp:
    #         json.dump(CACHE_DICT, fp)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def toDict(self):
        return dict(
            (key, value)
            for (key, value) in self.__dict__.items()
            )

def build_pokemon_dict():
    ''' Make a dictionary that maps Pokemon name to Serebii Pokedex url from "https://serebii.net/pokedex-swsh"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a Pokemon name and value is the url
        e.g. {'Pikachu':'https://serebii.net/pokedex-swsh/Pikachu', ...}
    '''
    ###using response and soup to parse the page for state list elements
    #getting pokemon names from pokemondb.net instead of serebii formatting is messy to parse for pokemon names
    url = 'https://pokemondb.net/pokedex/all'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pokemon_list_elements = soup.find_all(class_ = "ent-name")

    ###making dictionary that maps state name to state page url
    serebii_url_dict = {}
    base_url = "https://serebii.net/pokedex-swsh/"
    for list_element in pokemon_list_elements:
        db_url = list_element["href"]
        pokemon_name = db_url[9:]
        full_url = base_url + pokemon_name
        serebii_url_dict[list_element.string.lower()] = full_url
    #print(serebii_url_dict)
    return(serebii_url_dict)

def get_pokemon_instance(site_url):
    '''Make an instance from a Pokemon URL.

    Parameters
    ----------
    site_url: string
        The URL for a Pokemon Dex page in Serebii.net

    Returns
    -------
    instance
        a  Pokemon instance
    '''
    CACHE_DICT = open_cache()
    if site_url in CACHE_DICT:
        print("Fetching cached data")
        #print(CACHE_DICT[site_url])
        return CACHE_DICT[site_url]
    else:
        print("Making new entry")
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cells = soup.find_all(class_ = "fooinfo")
        type_cells = soup.find_all(class_ = "typeimg")
        base_stats_table = soup.find('a', attrs={'name': 'stats'}).find_next('table')
        base_stats = base_stats_table.findAll('td')
        name = cells[1].text.strip()
        dex = cells[3].text.replace('\n',' ').strip()
        if len(type_cells) == 1:
            type1 = type_cells[0]['alt']
            pokemon_types = type1
        else:
            type1 = type_cells[0]['alt']
            type2 = type_cells[1]['alt']
            pokemon_types = type1 + " and " + type2
        hp = base_stats[9].text.strip()
        attack = base_stats[10].text.strip()
        defense = base_stats[11].text.strip()
        special_attack = base_stats[12].text.strip()
        special_defense = base_stats[13].text.strip()
        speed = base_stats[14].text.strip()
        classification = cells[5].text.strip()
        height = cells[6].text.replace("\'", "ft ").replace('"', 'in').replace('\r\n\t\t\t', ' ').strip()
        weight = cells[7].text.replace('\r\n\t\t\t', ' ').strip()
        gender_ratio = cells[4].text.replace(':', ': ').replace('%', '% ').strip()
        # print(hp)
        # print(attack)
        # print(defense)
        # print(special_attack)
        # print(special_defense)
        # print(speed)
        This_Pokemon = Pokemon(name, dex, pokemon_types, hp, attack, defense, special_attack, special_defense, speed, classification, height, weight, gender_ratio)
        #print(This_Pokemon)
        CACHE_DICT[site_url] = This_Pokemon.toJson()
        #print(CACHE_DICT[site_url])
        #print(This_Pokemon.toDict())
        save_cache(CACHE_DICT)
        return This_Pokemon

##################################################
###Creating Database Tables with SQL and Python###
##################################################

###TABLE 1: Pokemon Data (Name, Dex, Types, Stats)
def make_pokemon_data_table():
    conn = sqlite3.connect("PokemonData.sqlite")
    cur = conn.cursor()

    drop_pokemon = '''
        DROP TABLE IF EXISTS Pokemon;
    '''

    create_pokemon = '''
        CREATE TABLE IF NOT EXISTS Pokemon(
            name TEXT PRIMARY KEY,
            classification TEXT NOT NULL,
            types TEXT NOT NULL,
            hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            defense INTEGER NOT NULL,
            special_attack INTEGER NOT NULL,
            special_defense INTEGER NOT NULL,
            speed INTEGER NOT NULL
        );
    '''
    cur.execute(drop_pokemon)
    cur.execute(create_pokemon)

    drop_extra_data = '''
        DROP TABLE IF EXISTS Pokemon_Extra;
    '''

    create_extra_data = '''
        CREATE TABLE IF NOT EXISTS Pokemon_Extra(
            dex TEXT PRIMARY KEY UNIQUE,
            height TEXT NOT NULL,
            weight TEXT NOT NULL,
            gender_ratio TEXT NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (name) REFERENCES Pokemon(name)
        );
    '''
    cur.execute(drop_extra_data)
    cur.execute(create_extra_data)

    conn.commit()
    conn.close()
    return

###TABLE 2: Pokemon Extra Data (Classification, Height, Weight, Gender Ratio)
def make_pokemon_extra_data_table():
    conn = sqlite3.connect("PokemonData.sqlite")
    cur = conn.cursor()

    drop_extra_data = '''
        DROP TABLE IF EXISTS Pokemon_Extra;
    '''

    create_extra_data = '''
        CREATE TABLE IF NOT EXISTS Pokemon_Extra(
            dex TEXT PRIMARY KEY UNIQUE,
            height TEXT NOT NULL,
            weight TEXT NOT NULL,
            gender_ratio TEXT NOT NULL,
            name TEXT,
            FOREIGN KEY (name) REFERENCES Pokemon(name)
        );
    '''
    cur.execute(drop_extra_data)
    cur.execute(create_extra_data)

    conn.commit()
    conn.close()
    return

make_pokemon_data_table()
#make_pokemon_extra_data_table()

def store_pokemon_in_database1():
    '''Store static pokemon data into the first establised SQLite Table'''

    conn = sqlite3.connect("PokemonData.sqlite")
    cur = conn.cursor()
    insert_pokemon = '''
    INSERT INTO Pokemon (name, classification, types, hp, attack, defense, special_attack, special_defense, speed) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

    CACHE_DICT = open_cache()
    for pokemon in CACHE_DICT:
        current_pokemon_instance = CACHE_DICT[pokemon]
        current_pokemon_dict = json.loads(current_pokemon_instance)
        pokemon_to_add = [current_pokemon_dict["name"], current_pokemon_dict["classification"], current_pokemon_dict["types"], current_pokemon_dict["hp"], current_pokemon_dict["attack"], current_pokemon_dict["defense"], current_pokemon_dict["special_attack"], current_pokemon_dict["special_defense"], current_pokemon_dict["speed"]]
        #print(pokemon_to_add)
        cur.execute(insert_pokemon, pokemon_to_add)
        conn.commit()

    return

def store_pokemon_in_database2():
    '''Store static extra pokemon data into the second establised SQLite Table'''

    conn = sqlite3.connect("PokemonData.sqlite")
    cur = conn.cursor()
    insert_pokemon_extra = '''
    INSERT INTO Pokemon_Extra (dex, height, weight, gender_ratio, name)
    VALUES (?, ?, ?, ?, ?)
'''
    CACHE_DICT = open_cache()
    for pokemon in CACHE_DICT:
        current_pokemon_instance = CACHE_DICT[pokemon]
        current_pokemon_dict = json.loads(current_pokemon_instance)
        pokemon_to_add = [current_pokemon_dict["dex"], current_pokemon_dict["height"], current_pokemon_dict["weight"], current_pokemon_dict["genderRatio"], current_pokemon_dict['name']]
        #print(pokemon_to_add)
        cur.execute(insert_pokemon_extra, pokemon_to_add)
        conn.commit()

    return

#########################################################
######ADDING ITEMS TO THE DATABASE IN SQL################
#########################################################
def adding_first_151_to_database():
    serebii_poke_dict = build_pokemon_dict()
    CACHE_DICT = open_cache()
    ct = 0
    for url in serebii_poke_dict.values():
        try:
            print("Seeing if Pokemon exists in Sword and Shield")
            instance = get_pokemon_instance(url)
            #print(instance)
        except:
            print("Pokemon does not exist in Sword and Shield as of yet")
        ct += 1
        if ct == 151:
            break
    print("Storing Pokemon in Database...")
    store_pokemon_in_database1()
    store_pokemon_in_database2()
    return

########################
####FUNCTION TESTING####
########################
# a = build_pokemon_dict()
# print(a)
#get_pokemon_instance('https://serebii.net/pokedex-swsh/bulbasaur/')
#get_pokemon_instance('https://serebii.net/pokedex-swsh/mew/')
# get_pokemon_instance('https://serebii.net/pokedex-swsh/cutiefly/')
#get_pokemon_instance('https://serebii.net/pokedex-swsh/abomasnow/')
#store_pokemon_in_database1()
#store_pokemon_in_database2()
#adding_first_151_to_cache()
adding_first_151_to_database()