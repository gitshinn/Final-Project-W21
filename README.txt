Serebii Pokedex Web Scraper
	This application scrapes Serebii.net for Pokemon information in the latest game in the franchise, Sword and Shield. There are 898 Pokemon in the game, but not all of them are accounted for in the latest build of the game. 
	The application builds a dictionary of all 898 Pokemon and allows users to input Pokemon names, which will scrapes and returns information on those Pokemon including whether or not that Pokemon is in Sword and Shield presently. It also gives users multiple views of Pokemon stats using Plotly. 
Required Python Packages:
* json
* BeautifulSoup4 (bs4)
* requests
* re
* sqlite3
* plotly
How to use the app:
	Simply run the application in the terminal with the required packages (already set-up in the code). If the SQL database is not already established/downloaded, the application will automatically create a database of the Pokemon among the first 151 that are in Sword and Shield.
	When running the application, a prompt in the terminal will ask the user to input the name of a Pokemon or terminate the program. The name of the Pokemon is not case-sensitive but spelling is important (you can try as many times as you need to!). The app will access the information either by scraping data from Serebii, the SQL database, or a Cache that continues to build the more the application is used by the user. 
	If the Pokemon is not in Sword and Shield, the application will report this and prompt the user to try again. If the Pokemon is in Sword and Shield, the application will present a new prompt asking for what kind of stats the user would like to see. Entering the desired text (also case-insensitive) will produce a bar graph of that Pokemon's stats based on the stated condition. The application will continue to let you compare and view stats or go back and choose another Pokemon to view until the user choose to terminate the application. 


