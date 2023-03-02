import discord
import os
from dotenv import load_dotenv
from urllib.request import urlopen
import urllib.error
import json
import datetime

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))
TOKEN              = os.getenv('DISCORD_TOKEN')
RESTAURANT_API_URL = "https://kitchen.kanttiinit.fi/restaurants?lang=fi&ids=1,2,3,5,7,8,41,45,50,51,52,59,64&priceCategories=student,studentPremium"
MENU_API_URL       = "https://kitchen.kanttiinit.fi/menus?lang=fi"


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        command = check_command(message)
        if command is not None:
            response = handle_command(command)
            if response is not None:
                if (type(response) is str):
                    await message.channel.send(response)
                else:
                    for r in response:
                        await message.channel.send(r)



def check_command(message):
    if message.content.startswith('!'):
        return message.content[1:]
    return None

def handle_command(input):
    args = input.split(' ')

    command = args[0]

    if command == 'ruokalista' or command == 'ruoka' or command == 'food':
        return get_food_list(args)
    if command == 'help':
        return get_help()
    if command == 'ping':
        return 'pong'

def get_food_list(args):    

    restaurant_data = None
    menu_data       = None

    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d")

    outputs = []

    try:
        response1 = urlopen(RESTAURANT_API_URL)
        response2 = urlopen(MENU_API_URL + "&days=" + date) 
        restaurant_data = json.loads(response1.read())
        menu_data       = json.loads(response2.read())

    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())
        restaurant_data = None
        menu_data       = None
    except urllib.error.URLError as e:
        print(e.args)
        restaurant_data = None
        menu_data       = None



    if menu_data is not None and restaurant_data is not None:

        restaurant_strings = []
        menu_strings       = []

        for restaurant in restaurant_data:
            restaurant_strings.append(restaurant)
        
        for menu in menu_data:
            menu_strings.append(menu)
            
        # Print each restaurant and its menu
        for i in range(len(restaurant_strings)):
            restaurant_menu = ""
            for j in range(len(menu_strings)):

                if len(args) > 1:
                    if (args[1].lower() not in restaurant_strings[i]['name'].lower()):
                        continue
                restaurantId = restaurant_strings[i]['id']
                
                if  str(restaurantId) == str(menu_strings[j]):
                    restaurant_menu += restaurant_strings[i]['name'] + "\n"
                    
                    menu = menu_data[str(restaurantId)].get("{date}".format(date=date))
                    for item in menu or []:
                        
                        line = "- " + item['title'.replace('\\n', ' ')]

                        properties = item['properties']
                        if properties is not None:
                            line += " ("
                            for property in properties:
                                line += property + ", "
                            line += ")"
                        restaurant_menu += line + "\n"
                    outputs.append(restaurant_menu)

                        

    else:
        print("Error fetching data.")
        return["Error fetching data."]

    return outputs
        
def get_help():
    return 'Commands: !ruokalista, !ruoka, !food, !help, !ping'

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)