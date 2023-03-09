prefix='?'
myToken=''
weather_API_Key = ''


#==================================================================
from discord.ext.commands import Bot
import os
import json
import requests
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = Bot(command_prefix=commands.when_mentioned_or(prefix), intents=intents)

@bot.command(name = 'hello',
        description= 'say hello to some fuck that needs a friend',
        )
async def hello(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        if ctx.channel.permissions_for(ctx.me).send_messages:
            await ctx.send('Hello!')
        else:
            print('I don\'t have permission to send messages in this channel.')
    else:
        await ctx.author.send('This command can only be used in a server/channel.')


# for adding user Loc
@bot.command(name = 'add',
        description= 'Add location for weather api',
        )
async def addLocation(ctx,*, location) -> None: 
    #chk in a mom joke then save
    if location.find('house') != -1 and location.find('mom') != -1:
        # joke good, saving
        await ctx.send(content='adding')   
        wther().setWordCount(ctx.author, location)
        return
    # else chk in a real Loc then save
    else: 
        lonLan = locationChk(location)
        if len(lonLan) < 2 :
            await ctx.send(lonLan[0])
            return      
        # Loc good, saving    
        await ctx.send(content='adding')  
        wther().setWordCount(ctx.author, location)


# for adding user Loc
@bot.command(name = 'w',
        description= 'Check the weather',
        )
async def weather(ctx,*, location: str = '+') -> None:
    # the bot does not handle emp str well so I used a +, I could have used None I guess but W.E
    if location == '+':
        locations = wther().getLocations()
        # chk to see if we have a location as none was given
        try:
            location = locations[str(ctx.author)]            
        except:
            await ctx.send(f'Sorry, you need to eather use {prefix}add, to add a location or send one while using {prefix}w')
            return
            
    # If Loc is mom joke         
    if location.find('house') != -1 and location.find('mom') != -1:
        embed = discord.Embed(
            title=f'Weather in {location}',
            description=f'Temperature: 🌡️ It\'s always warm in her bed',
            color=0x9C84EF
        )
        await ctx.send(embed=embed)
        return

    # chk Loc 
    lonLan = locationChk(location)
    if len(lonLan) < 2 :
        # Bad Loc or Server Error
        await ctx.send(lonLan[0])
        return

    latitude = lonLan[0]
    longitude = lonLan[1]

    # make a request to the OpenWeatherMap API for the current weather data for the specified location
    owm_response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={weather_API_Key}')
    if owm_response.status_code != 200:
        await ctx.send('Sorry, there was an error retrieving the weather data.')
        return

    # extract the weather data from the API response
    data = owm_response.json()
    tempC = data['main']['temp']
    tempF = c2f(tempC)
    temperature = f'{tempC}°C/{tempF}°F'
    feels_likeC = data['main']['feels_like']
    feels_likeF = c2f(feels_likeC)
    feels_like  = f'{feels_likeC}°C/{feels_likeF}°F'
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    clouds = data['clouds']['all']
    description = data['weather'][0]['description']
    location_name = data['name']

    # determine the appropriate emoji based on the weather description
    emoji = ""
    if "clear" in description:
        emoji = "☀️"
    elif "cloud" in description:
        emoji = "☁️"
    elif "rain" in description:
        emoji = "🌧️"
    elif "thunderstorm" in description:
        emoji = "⛈️"
    elif "snow" in description:
        emoji = "❄️"

    # send a message to the channel with the current weather data for the specified location, along with an appropriate emoji
    embed = discord.Embed(
        title=f'Weather in {location_name}',
        description=f'Temperature: 🌡️ {temperature}\nFeels Like: {feels_like}\nHumidity: {humidity}%\nWind Speed: {wind_speed} m/s\nClouds: {clouds}%\nDescription: {emoji} {description}',
        color=0x9C84EF
    )
    await ctx.send(embed=embed)


def c2f(tempc):
    x = (tempc * 9/5) + 32
    tempF = round(x, 2)
    return tempF


# for saving usr Loc
# didnt need the class but eh
class wther():
    def __init__(self):
        dirName = f'{os.path.dirname(os.path.abspath(__file__))}'
        self.userLocationsFile = f'{dirName}/userLocations.json'
        self.getLocations()
       
    def getLocations(self):
        if os.path.isfile(self.userLocationsFile):
            with open(self.userLocationsFile, 'r') as openfile:
                self.userLocations = json.load(openfile)
        else: 
            self.userLocations = {}      
            with open(self.userLocationsFile, 'a') as outfile:
                json.dump(self.userLocations, outfile)
        return self.userLocations

    def setWordCount(self, user, location):
        self.userLocations.update({str(user):str(location)}) 
        with open(self.userLocationsFile, 'w') as outfile:
            json.dump(self.userLocations, outfile) 
        return self.userLocations


def locationChk(location):
        # make a request to the OpenStreetMap API to retrieve the latitude and longitude for the location
    nominatim_response = requests.get(f"https://nominatim.openstreetmap.org/search?q={location}&format=json")
    if nominatim_response.status_code != 200:
        return ['Sorry, there was an error retrieving the location data.']

    # extract the latitude and longitude from the API response
    nominatim_data = nominatim_response.json()
    if len(nominatim_data) == 0:
        return [f'No results found for location: {location}']

    latitude = nominatim_data[0]["lat"]
    longitude = nominatim_data[0]["lon"]
    return [latitude, longitude]
    

@bot.event
async def on_ready():
    print('Connected to Discord!')

bot.run(myToken)
