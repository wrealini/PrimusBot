import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.command()
async def roll(ctx, *args):
    arguments = ''.join(args)
    embedVar = discord.Embed(title="Roll", description=arguments)
    await ctx.send(embed=embedVar)
    await ctx.message.delete()

f = open('token.txt')
token = f.read()
f.close()
bot.run(token)