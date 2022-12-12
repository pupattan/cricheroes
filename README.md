# cricheroes
Python APIs to fetch and store team data from cricheroes.in

# Set up 
## Install Google Chrome
* Windows: Download and install google chrome for windows 
* Linux: Refer to https://linuxconfig.org/how-to-install-google-chrome-browser-on-linux
  * For selenium webdriver refer : https://gist.github.com/siumhossain/1aa24622d8fda5053581c87ca6457638
* Docker: For Alpine run following
  * apk add chromium
  * apk add  chromium-chromedriver
  
## Install module
Download and install 'cricheroes' python module from pypi.
Use the following command
```
pip install cricheroes
```
# Usage
Create Team object and use it as per your requirement
```python
from cricheroes import Team
# Create Team Object 
team = Team(url='2580003/CP-Sm@shers')

# Get all players, returns list of Player object in cricheroes module
players = team.get_players()

# Print player names
for player in players:
    print(player.name)
    
# Get recent matches played by the team, returns list of Match object
matches = team.get_matches()
# Print match results
for match in matches:
    print(match.result)

# Get over all team statistics from Stats tab
stats = team.get_team_stats()
# Print match results
for stat in stats:
    print(stat.label)
    print(stat.value)
    
# Get leaderboard/top performer of the team, returns dictionary with batting, bowling, fielding statistics
# Each value contains list of LeaderboardStat
leaderboard = team.get_leaderboard()
# Print batting stat
for item in leaderboard['batting']:
    print(item.player_name, item.stat)

# Print batting stat
for item in leaderboard['bowling']:
    print(item.player_name, item.stat)

# Print fielding stat
for item in leaderboard['fielding']:
    print(item.player_name, item.stat)

# Get all data and dump to json
from cricheroes import Team
# Create Team Object 
team = Team(url='2580003/CP-Sm@shers')
team.dump_all()

# This will craete a json file 'out.json' at current directory
```

# To test:
Download gist file https://gist.githubusercontent.com/pupattan/02e6e2cad7edfd78c4620adbb9dfa992/raw/973fa27444f1865d3f9b6538f3a49e30971428e4/cricheroes_test.py
Run file after doing the set up 
```python
python cricheroes_test.py
```
out.json file will be created at current directory 
