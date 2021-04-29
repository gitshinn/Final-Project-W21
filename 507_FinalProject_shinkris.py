#################################
##### Name: Kristian Shin
##### Uniqname: shinkris
#################################

from bs4 import BeautifulSoup
import requests
import json
import re
import sqlite3
import plotly.graph_objs as go

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

    classification: string
    Unique classifier for a Pokemon. Example: Bulbasaur is the "Seed" Pokemon

    height: string
    How tall a Pokemon is in feet or meters

    weight: string
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

    #converts object to a json
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    #converts object to a dict
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
    #constructing the full url based off of the BS4 scraping results
    for list_element in pokemon_list_elements:
        db_url = list_element["href"]
        pokemon_name = db_url[9:]
        full_url = base_url + pokemon_name
        serebii_url_dict[list_element.string.lower()] = full_url
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
    #If Pokemon object is in the Cache Dictionary, retrieve that data instead of scraping the page
    if site_url in CACHE_DICT:
        print("Fetching cached data")
        return CACHE_DICT[site_url]
    else:
        print("Making new entry")
        #If Pokemon object not already in the Cache dictionary, use BS4 to scrape the page for the appropriate Pokemon objects
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        #Finds almost all of the information on each Pokemon's page on Serebii
        cells = soup.find_all(class_ = "fooinfo")
        #Types have a different class tag
        type_cells = soup.find_all(class_ = "typeimg")
        #Base stats require specific find since they are listed after TMs on the Serebii page, which are different per each Pokemon
        base_stats_table = soup.find('a', attrs={'name': 'stats'}).find_next('table')
        base_stats = base_stats_table.findAll('td')
        #name of the Pokemon
        name = cells[1].text.strip()
        #dex number of the Pokemon
        dex = cells[3].text.replace('\n',' ').strip()
        #Pokemon can have 1-2 types
        if len(type_cells) == 1:
            type1 = type_cells[0]['alt']
            pokemon_types = type1
        else:
            type1 = type_cells[0]['alt']
            type2 = type_cells[1]['alt']
            pokemon_types = type1 + " and " + type2
        #hp, attack, defense, special attack, special defense, and speed of Pokemon
        hp = base_stats[9].text.strip()
        attack = base_stats[10].text.strip()
        defense = base_stats[11].text.strip()
        special_attack = base_stats[12].text.strip()
        special_defense = base_stats[13].text.strip()
        speed = base_stats[14].text.strip()
        #classification, height, weight, and gender ratio of the Pokemon. Height, Weight, and Gender Ratio are formatted awkwardly and require more cleaning.
        classification = cells[5].text.strip()
        height = cells[6].text.replace("\'", "ft ").replace('"', 'in').replace('\r\n\t\t\t', ' ').strip()
        weight = cells[7].text.replace('\r\n\t\t\t', ' ').strip()
        gender_ratio = cells[4].text.replace(':', ': ').replace('%', '% ').strip()
        #calling class object Pokemon based on the scrapped page data above
        This_Pokemon = Pokemon(name, dex, pokemon_types, hp, attack, defense, special_attack, special_defense, speed, classification, height, weight, gender_ratio)
        #saving the Pokemon into the Cache Dictionary
        CACHE_DICT[site_url] = This_Pokemon.toJson()
        save_cache(CACHE_DICT)
        return CACHE_DICT[site_url]

##################################################
###Creating Database Tables with SQL and Python###
##################################################

def make_pokemon_data_table():
    '''Function to make PokemonData in sqlite with two tables: Pokemon and Pokemon_Extra

    Parameters
    ----------
    None

    Returns
    -------
    Object
        a Sqlite Object
    '''
    #establish and connect to new table PokemonData
    conn = sqlite3.connect("PokemonData.sqlite")
    cur = conn.cursor()

    #make sure Pokemon doesn't already exist
    drop_pokemon = '''
        DROP TABLE IF EXISTS Pokemon;
    '''
    #make table Pokemon with name, class, types, and stats
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
    #execute the drop + creation of Pokemon
    cur.execute(drop_pokemon)
    cur.execute(create_pokemon)

    #make sure Pokemon_Extra doesn't exist
    drop_extra_data = '''
        DROP TABLE IF EXISTS Pokemon_Extra;
    '''
    #create Pokemon_Extra with dex number, height, weight, gender_ratio. Also add name as foreign key
    create_extra_data = '''
        CREATE TABLE IF NOT EXISTS Pokemon_Extra(
            dex TEXT PRIMARY KEY,
            height TEXT NOT NULL,
            weight TEXT NOT NULL,
            gender_ratio TEXT NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (name) REFERENCES Pokemon(name)
        );
    '''

    #execute drop + creation of Pokemon_Extra
    cur.execute(drop_extra_data)
    cur.execute(create_extra_data)

    #commit changes and close the database
    conn.commit()
    conn.close()
    return

def store_pokemon_in_database1():
    '''Store static pokemon data into the first establised SQLite Table'''

    #Connect to PokemonData then insert rows and columns into Pokemon table
    conn = sqlite3.connect("PokemonData.sqlite")
    cur = conn.cursor()
    insert_pokemon = '''
    INSERT OR REPLACE INTO Pokemon (name, classification, types, hp, attack, defense, special_attack, special_defense, speed)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

    #Check the Cache Dictionary to see if Pokemon is in there. If not, proceed to add with the appropriate values.
    CACHE_DICT = open_cache()
    for pokemon in CACHE_DICT:
        current_pokemon_instance = CACHE_DICT[pokemon]
        current_pokemon_dict = json.loads(current_pokemon_instance)
        pokemon_to_add = [current_pokemon_dict["name"], current_pokemon_dict["classification"], current_pokemon_dict["types"], current_pokemon_dict["hp"], current_pokemon_dict["attack"], current_pokemon_dict["defense"], current_pokemon_dict["special_attack"], current_pokemon_dict["special_defense"], current_pokemon_dict["speed"]]
        cur.execute(insert_pokemon, pokemon_to_add)
        conn.commit()

    return

def store_pokemon_in_database2():
    '''Store static extra pokemon data into the second establised SQLite Table'''

    #Connect to PokemonData then insert rows and columns into Pokemon_Extra table
    conn = sqlite3.connect("PokemonData.sqlite")
    cur = conn.cursor()
    insert_pokemon_extra = '''
    INSERT OR REPLACE INTO Pokemon_Extra (dex, height, weight, gender_ratio, name)
    VALUES (?, ?, ?, ?, ?)
'''
    #Check the Cache Dictionary to see if Pokemon is in there. If not, proceed to add with the appropriate values.
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
    'Adds the first 151 Pokemon to the SQL Database PokemonData. Will skip over Pokemon in the first 151 that are not currently added to Sword and Shield'
    #creating dictionaries to loop over and check
    serebii_poke_dict = build_pokemon_dict()
    CACHE_DICT = open_cache()
    ct = 0
    for url in serebii_poke_dict.values():
        #break out of the loop if the dictionary is already established
        if len(CACHE_DICT) >= 110:
            break
        else:
            try:
                #get Pokemon data if the Pokemon is in Sword and Shield
                print("Seeing if Pokemon exists in Sword and Shield")
                instance = get_pokemon_instance(url)
            except:
                #if Pokemon is not in Sword and Shield, try the next Pokemon
                print("Pokemon does not exist in Sword and Shield as of yet")
            ct += 1
            #once the 151 are checked, break out of the loop
            if ct == 151:
                break
    #store everything to the Database
    print("Establishing Database...")
    store_pokemon_in_database1()
    store_pokemon_in_database2()
    return

###Run these functions before main
make_pokemon_data_table()
adding_first_151_to_database()

##############################
########MAIN FUNCTION#########
##############################
if __name__ == "__main__":
    ###user prompted to enter a Pokemon name or exit
    user_input = input('Enter a Pokemon name (e.g. Pikachu, pikachu), or "exit" to quit:').lower()
    #make a dictionary of state names to abbreviations
    pokemon_dictionary = build_pokemon_dict()
    #keep repeating function until user types exit
    while user_input != "exit":
        #connect to the PokemonData database
        conn = sqlite3.connect("PokemonData.sqlite")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Pokemon INNER JOIN Pokemon_Extra ON Pokemon.name=Pokemon_Extra.name")
        rows = cur.fetchall()
        #checking database to see if pokemon name is present
        for row in rows:
            if user_input.capitalize() == row[0]:
                print("Retrieved " + user_input.capitalize() + " from Database")
                pokemon_from_database = row
                #new input
                #takes inputs of physical, special, offensive, or defensive stats and displays as a barplot. extra shows height/weight.
                #continue checks outside of the database for more Pokemon. exit terminates the program.
                db_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "continue" to check outside of the database, or "exit" to quit:').lower()
                while db_five_opt_user_input:
                    #exit quits out
                    if db_five_opt_user_input == "exit":
                        print("Thanks for using my program!")
                        quit()
                    #continue proceeds to checking outside of the database (checks cache/validity of new Pokemon)
                    elif db_five_opt_user_input == "continue":
                        user_input = input('Enter a Pokemon name (e.g. Pikachu, pikachu), or "exit" to quit:').lower()
                        break
                    #physical stats attack and defense are plotted in a bar graph and displayed in html
                    elif db_five_opt_user_input == 'physical':
                        print('Creating graph of Pokemon physical attributes')
                        xvals = ['stat', 'attack', 'defense']
                        yvals = [' ', pokemon_from_database[4], pokemon_from_database[5]]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_from_database[0])
                        fig=go.Figure(data=bar_data, layout_title_text="Physical Properties of" + ' ' + pokemon_from_database[0])
                        fig.show()
                        db_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "continue" to check outside of the database, or "exit" to quit:').lower()
                    #special stats special_attack and special_defense are plotted in a bar graph and displayed in html
                    elif db_five_opt_user_input == 'special':
                        print('Creating graph of Pokemon special attributes')
                        xvals = ['stat', 'special attack', 'special defense']
                        yvals = [' ', pokemon_from_database[6], pokemon_from_database[7]]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_from_database[0])
                        fig=go.Figure(data=bar_data, layout_title_text="Special Properties of" + ' ' + pokemon_from_database[0])
                        fig.show()
                        db_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "continue" to check outside of the database, or "exit" to quit:').lower()
                    #offensive stats attack, special_attack, and speed are plotted in a bar graph and displayed in html
                    elif db_five_opt_user_input == 'offense':
                        print('Creating graph of Pokemon offensive attributes')
                        xvals = ['stat', 'attack', 'special_attack', 'speed']
                        yvals = [' ', pokemon_from_database[4], pokemon_from_database[6], pokemon_from_database[8]]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_from_database[0])
                        fig=go.Figure(data=bar_data, layout_title_text="Offensive Properties of" + ' ' + pokemon_from_database[0])
                        fig.show()
                        db_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "continue" to check outside of the database, or "exit" to quit:').lower()
                    #defensive stats hp, defense, and speed are plotted in a bar graph and displayed in html
                    elif db_five_opt_user_input == 'defense':
                        print('Creating graph of Pokemon defensive attributes')
                        xvals = ['stat', 'hp', 'defense', 'special_defense']
                        yvals = [' ', pokemon_from_database[3], pokemon_from_database[5], pokemon_from_database[7]]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_from_database[0])
                        fig=go.Figure(data=bar_data, layout_title_text="Defensive Properties of" + ' ' + pokemon_from_database[0])
                        fig.show()
                        db_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "continue" to check outside of the database, or "exit" to quit:').lower()
                    #height and weight are plotted in a bar graph and displayed in html
                    elif db_five_opt_user_input == 'extra':
                        print('Creating graph of Pokemon extra properties')
                        xvals = ['stat', 'height', 'weight']
                        yvals = [' ', pokemon_from_database[10], pokemon_from_database[11]]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_from_database[0])
                        fig=go.Figure(data=bar_data, layout_title_text="Extra Properties of" + ' ' + pokemon_from_database[0])
                        fig.show()
                        db_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "continue" to check outside of the database, or "exit" to quit:').lower()
                    #invalid input
                    else:
                        print("[Error] Enter an applicable stat display")
                        db_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "continue" to check outside of the database, or "exit" to quit:').lower()
        #if pokemon not in database, check the complete pokedex
        if user_input in pokemon_dictionary:
            pokemon_url = pokemon_dictionary[user_input]
            print("Seeing if Pokemon is in Cache")
            #checking if pokemon is actually in the Sword and Shield game presently
            try:
                pokemon_info = get_pokemon_instance(pokemon_url)
            except:
                print("Pokemon does not exist in Sword and Shield as of yet. Try a different Pokemon.")
            #proceeding if pokemon_url is valid in Sword and Shield
            else:
                #loading it into dictionary form for more convenience in plotting
                pokemon_info_dict = json.loads(pokemon_info)
                #new input
                #takes inputs of physical, special, offensive, or defensive stats and displays as a barplot. extra shows height/weight.
                #back returns to the begin of the function to input another Pokemon. exit terminates the program.
                standard_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "back" to choose another Pokemon, or "exit" to quit:').lower()
                if standard_five_opt_user_input == "exit":
                    exit()
                while standard_five_opt_user_input:
                    #break out and return to the first user_input prompt
                    if standard_five_opt_user_input == "back":
                        break
                    #quits out of the program
                    elif standard_five_opt_user_input == "exit":
                        print("Thanks for using my program!")
                        exit()
                    #physical stats attack and defense are plotted in a bar graph and displayed in html
                    elif standard_five_opt_user_input == 'physical':
                        print('Creating graph of Pokemon physical attributes')
                        xvals = ['stat', 'attack', 'defense']
                        yvals = [' ', pokemon_info_dict['attack'], pokemon_info_dict['defense']]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_info_dict['name'])
                        fig=go.Figure(data=bar_data, layout_title_text="Physical Stats of" + ' ' + pokemon_info_dict['name'])
                        fig.show()
                        standard_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "back" to choose another Pokemon, or "exit" to quit:').lower()
                    #special stats special_attack and special_defense are plotted in a bar graph and displayed in html
                    elif standard_five_opt_user_input == 'special':
                        print('Creating graph of Pokemon special attributes')
                        xvals = ['stat', 'special attack', 'special defense']
                        yvals = [' ', pokemon_info_dict['special_attack'], pokemon_info_dict['special_defense']]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_info_dict['name'])
                        fig=go.Figure(data=bar_data, layout_title_text="Special Stats of" + ' ' + pokemon_info_dict['name'])
                        fig.show()
                        standard_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "back" to choose another Pokemon, or "exit" to quit:').lower()
                    #offensive stats attack, special_attack, and speed are plotted in a bar graph and displayed in html
                    elif standard_five_opt_user_input == 'offense':
                        print('Creating graph of Pokemon offensive attributes')
                        xvals = ['stat', 'attack', 'special_attack', 'speed']
                        yvals = [' ', pokemon_info_dict['attack'], pokemon_info_dict['special_attack'], pokemon_info_dict['speed']]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_info_dict['name'])
                        fig=go.Figure(data=bar_data, layout_title_text="Offensive Stats of" + ' ' + pokemon_info_dict['name'])
                        fig.show()
                        standard_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "back" to choose another Pokemon, or "exit" to quit:').lower()
                    #defensive stats hp, defense, and speed are plotted in a bar graph and displayed in html
                    elif standard_five_opt_user_input == 'defense':
                        print('Creating graph of Pokemon defensive attributes')
                        xvals = ['stat', 'hp', 'defense', 'special_defense']
                        yvals = [' ', pokemon_info_dict['hp'], pokemon_info_dict['defense'], pokemon_info_dict['special_defense']]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_info_dict['name'])
                        fig=go.Figure(data=bar_data, layout_title_text="Defensive Stats of" + ' ' + pokemon_info_dict['name'])
                        fig.show()
                        standard_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "back" to choose another Pokemon, or "exit" to quit:').lower()
                    #height and weight are plotted in a bar graph and displayed in html
                    elif standard_five_opt_user_input == 'extra':
                        print('Creating graph of Pokemon extra properties')
                        xvals = ['stat', 'height', 'weight']
                        yvals = [' ', pokemon_info_dict['height'], pokemon_info_dict['weight']]
                        bar_data = go.Bar(x=xvals,y=yvals)
                        basic_layout = go.Layout(title=pokemon_info_dict['name'])
                        fig=go.Figure(data=bar_data, layout_title_text="Extra Properties of" + ' ' + pokemon_info_dict['name'])
                        fig.show()
                        standard_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "back" to choose another Pokemon, or "exit" to quit:').lower()
                    #invalid input
                    else:
                        print("[Error] Enter an applicable stat display")
                        standard_five_opt_user_input = input('Enter Physical, Special, Offense, Defense, Extra, "back" to choose another Pokemon, or "exit" to quit:').lower()
        #if not a pokemon or command
        else:
            print("[Error] Enter proper Pokemon name")
        user_input = input('Enter a Pokemon name (e.g. Pikachu, pikachu), or "exit" to quit:').lower()