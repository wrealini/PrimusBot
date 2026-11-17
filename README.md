# PrimusBot
A web app and Discord bot used for playing D&amp;D 5.6e on the Sigil Adventurer's Guild Discord server.

This project requires four files which are not tracked:
 - credentials_installed.json A file which you can generate following these instructions to create your own Google Cloud project to use the Google Sheets API: https://developers.google.com/workspace/sheets/api/quickstart/python
 - credentials_web.json A file which you can generate following the same instructions but creating a client for a web app instead of a desktop app.
 - googleSheetsToken.json A file which contains the user access token and which is automatically generated when you first sign in to a google account to enable user access.
 - discordBotToken.txt A file which contains the token used to run a Discord bot, which you can generate by creating your own Primus bot as a new application here: https://discord.com/developers/applications/