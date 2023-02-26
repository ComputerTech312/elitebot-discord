from discord.ext.commands import Bot
import os
import requests
import discord
from discord.ext import commands

prefix='?'
myToken='Your-Discord-Bot-Token'
OPENWEATHERMAP_API_KEY = 'Your-Openweathermap-API'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = Bot(command_prefix=commands.when_mentioned_or(prefix), intents=intents)

@bot.command(name='hello',
        description="say hello to some lone;y fuck that needs a friend",
    )
async def hello(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        if ctx.channel.permissions_for(ctx.me).send_messages:
            await ctx.send('Hello!')
        else:
            print('I don\'t have permission to send messages in this channel.')
    else:
        await ctx.author.send('This command can only be used in a server/channel.')

@bot.command(name='w')
async def weather(ctx, location: str):
    # make a request to the OpenStreetMap API to retrieve the latitude and longitude for the location
    nominatim_response = requests.get(f"https://nominatim.openstreetmap.org/search?q={location}&format=json")
    if nominatim_response.status_code != 200:
        await ctx.send('Sorry, there was an error retrieving the location data.')
        return

    # extract the latitude and longitude from the API response
    nominatim_data = nominatim_response.json()
    if len(nominatim_data) == 0:
        await ctx.send(f"No results found for location: {location}")
        return
    latitude = nominatim_data[0]["lat"]
    longitude = nominatim_data[0]["lon"]

    # make a request to the OpenWeatherMap API for the current weather data for the specified location
    owm_response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={OPENWEATHERMAP_API_KEY}')
    if owm_response.status_code != 200:
        await ctx.send('Sorry, there was an error retrieving the weather data.')
        return

    # extract the weather data from the API response
    data = owm_response.json()
    temperature = data['main']['temp']
    feels_like = data['main']['feels_like']
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
        description=f'{emoji} Temperature: {temperature}°C\nFeels Like: {feels_like}°C\nHumidity: {humidity}%\nWind Speed: {wind_speed} m/s\nClouds: {clouds}%\nDescription: {description}',
        color=0x9C84EF
    )
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print('Connected to Discord!')

bot.run(myToken)
