import asyncio
import json
import os
import time

import discord
import requests

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

last_reply_times = {}

game_active = False
board = [' '] * 9
current_player = 'X'


def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)

  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return quote


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):

  if message.content.startswith('$commands'):
    await message.channel.send(
        'To play a game of tic tac toe, command : $game1')
    await message.channel.send('To get inspired, command : $inspire')
    await message.channel.send(
        'To clear chat history, command : $clear (clears last 10')
    await message.channel.send(
        'To clear chat history, command :$clear_all (clears whole history)')

  global game_active
  global board
  global current_player

  if message.author == client.user:  # Ignore messages from the bot itself
    return

  if message.content.startswith('$game1'):
    if game_active:
      await message.channel.send('A game is already in progress.')
      return

    game_active = True
    board = [' '] * 9
    current_player = 'X'
    await display_board(message.channel)

  if game_active and message.content.isdigit() and 1 <= int(
      message.content) <= 9:
    move = int(message.content) - 1

    if board[move] == ' ':
      board[move] = current_player
      await display_board(message.channel)
      if await check_winner(current_player):
        await message.channel.send(f'Player {current_player} wins!')
        game_active = False
      else:
        current_player = 'O' if current_player == 'X' else 'X'

  content = message.content.lower()

  if message.author == client.user:
    return

  greetings = ['hello', 'hi', 'yo', 'wassup', 'hey', 'hoi']

  #Greeting with 10s cooldown
  if any(greeting in content for greeting in greetings):
    user_id = message.author.id
    current_time = time.time()

    # Check if the user's last reply time is available and if the timeout has passed
    if user_id in last_reply_times and current_time - last_reply_times[
        user_id] < 60:
      return

    last_reply_times[user_id] = current_time

    await message.channel.send(f"Hello, {message.author.mention}!")

  #Write a random quote
  if content.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)

  #Clear last 10 messages or all messages
  if content.startswith('$clear'):
    if message.channel.permissions_for(message.author).manage_messages:
      if content == '$clear':
        await clear_last_10_messages(message.channel)
      elif content == '$clear_all':
        await clear_entire_history(message.channel)
    else:
      await message.channel.send(
          "You don't have permission to use this command.")


async def clear_last_10_messages(channel):
  async for msg in channel.history(limit=11):
    await msg.delete()
    await asyncio.sleep(1)  # Add a delay of 1 second between deletions
  await channel.send('Cleared the last 10 messages.')


async def clear_entire_history(channel):
  async for msg in channel.history():
    await msg.delete()
    await asyncio.sleep(1)  # Add a delay of 1 second between deletions
  await channel.send('Cleared the entire message history.')


async def display_board(channel):
  board_text = ""
  for i in range(0, 9, 3):
    row = " | ".join(board[i:i + 3])
    board_text += f"{row}\n{'-'*9}\n"

  message = f"```\n{board_text}\n```"
  await channel.send(message)


async def check_winner(player):
  winning_combinations = [
      [0, 1, 2],
      [3, 4, 5],
      [6, 7, 8],  # Rows
      [0, 3, 6],
      [1, 4, 7],
      [2, 5, 8],  # Columns
      [0, 4, 8],
      [2, 4, 6]  # Diagonals
  ]

  return any(
      all(board[i] == player for i in combo) for combo in winning_combinations)


client.run(os.environ['TOKEN'])
