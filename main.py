#!/usr/bin/env python3
import logging
import time
import json

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Request
from starlette.responses import RedirectResponse

import models
from tortoise.contrib.fastapi import register_tortoise

from nicegui import app, ui

register_tortoise(app, db_url='sqlite://db.sqlite3', modules={'models': ['models']}, generate_schemas=True)

# Get the credentials from the Google Cloud Console.
# See https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid#get_your_google_api_client_id.
# For local development, you should add http://localhost:8080 to the authorized JavaScript origins.
# In production, you should add the domain of your website to the authorized JavaScript origins.
# Make sure you include <origin>/auth in "Authorized redirect URIs".
with open('credentials.json', 'r') as f:
    creds = json.load(f)
    GOOGLE_CLIENT_ID = creds["installed"]["client_id"]
    GOOGLE_CLIENT_SECRET = creds["installed"]["client_secret"]
    GOOGLE_PROJECT_ID = creds["installed"]["project_id"]
    GOOGLE_API_KEY = creds["installed"]["api_key"]
    GOOGLE_PROJECT_NUMBER = creds["installed"]["project_number"]

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/drive'},
)

DEFAULT_PFP = 'https://i.imgur.com/tdi3NGa.png'


@ui.page('/')
async def main(request: Request) -> RedirectResponse | None:
    access_token = app.storage.user.get('access_token', {})
    user_info = access_token.get('userinfo', {})
    if not _is_valid(user_info):
        app.storage.user.pop('access_token', None)
        app.storage.user.pop('user_info', None)
        return await oauth.google.authorize_redirect(request, request.url_for('google_oauth'))
    
    user_db_info = {"email":user_info.get("email", ""),
                    "discord":'',
                    "name":user_info.get("name") or user_info.get("email", ""),
                    "pfp":DEFAULT_PFP,
                    "dorl":False}
    user_db_info = await models.User.get_or_create(defaults=user_db_info, email=user_info.get("email", ""))
    
    with ui.header().classes(replace='row items-center') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        with ui.tabs() as tabs:
            ui.tab('A')
            ui.tab('B')
            ui.tab('C')
        with ui.button(on_click=lambda: right_drawer.toggle()).props('no-caps').classes('ml-auto'):
            unlabel = ui.label(f'Hi {user_db_info[0].name}!')
            pfp = ui.image(user_db_info[0].pfp).classes('rounded-full size-8 ml-4')

    with ui.footer(value=False) as footer:
        ui.label('Footer')

    with ui.left_drawer().classes('bg-blue-100 dark:bg-gray-800').set_value(False) as left_drawer:
        ui.label('Left menu')

    with ui.right_drawer().classes('bg-blue-100 dark:bg-gray-800').set_value(False) as right_drawer:
        with ui.grid(columns=1).classes('items-start'):
            untextbox = ui.input(label='Update Username', placeholder='Start typing...',
                validation={'Username must be between 3 and 40 characters': lambda value: len(value) < 41 and len(value) > 2})
            async def update_username():
                if untextbox.validate():
                    user_db_info[0].name = untextbox.value
                    await user_db_info[0].save()
                    unlabel.set_text(f'Hi {user_db_info[0].name}!')
            untextbox.on('keydown.enter',update_username)

            ui.label('Select Profile Picture')
            async def reset_pfp():
                user_db_info[0].pfp = DEFAULT_PFP
                await user_db_info[0].save()
                pfp.set_source(user_db_info[0].pfp)
                pfp.force_reload()
            ui.button('Use Default Picture',on_click=reset_pfp)
            async def gmail_pfp():
                user_db_info[0].pfp = user_info.get("picture")
                await user_db_info[0].save()
                pfp.set_source(user_db_info[0].pfp)
                pfp.force_reload()
            ui.button('Use Gmail Picture',on_click=gmail_pfp)
            async def select_pfp():
                print("select_pfp")
                jstxt = """
                    const picker = new google.picker.PickerBuilder()
                        .addView(google.picker.ViewId.DOCS)
                        .setOAuthToken('ACCESS_TOKEN')
                        .setDeveloperKey('API_KEY')
                        .setAppId('APP_ID')
                        .build();
                    picker.setVisible(true);
                """
                jstxt = jstxt.replace("API_KEY",GOOGLE_API_KEY)
                print(f"API_KEY: {GOOGLE_API_KEY}")
                jstxt = jstxt.replace("APP_ID",access_token["id_token"])
                print(f"APP_ID: {access_token["id_token"]}")
                jstxt = jstxt.replace("ACCESS_TOKEN",access_token["access_token"])
                print(f"ACCESS_TOKEN: {access_token["access_token"]}")
                ui.run_javascript(jstxt, timeout=5.0)
            sgdp = ui.button('Select Google Drive Picture',on_click=select_pfp).disable()

            ui.separator()

            dark = ui.dark_mode()
            async def update_dorl():
                user_db_info[0].dorl = dorlswtich.value
                await user_db_info[0].save()
            dorlswtich = ui.switch('Dark Mode',on_change=update_dorl).bind_value(dark)
            dorlswtich.set_value(user_db_info[0].dorl)

            ui.separator()

            ui.button('Logout', on_click=logout)

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

    with ui.tab_panels(tabs, value='A').classes('w-full'):
        with ui.tab_panel('A'):
            ui.label('Content of A')
        with ui.tab_panel('B'):
            ui.label('Content of B')
        with ui.tab_panel('C'):
            ui.label('Content of C')


    ui.add_head_html('<script src="https://www.google.com/jsapi?key=AIzaSyACPMfArVk69ADHwCpNdCT-pVkru9aiJ2U"></script>')
    ui.add_head_html('<script src="https://apis.google.com/js/client.js?onload=SetPicker"></script>')
    await ui.run_javascript(f"gapi.client.setApiKey('{GOOGLE_API_KEY}');\ngapi.client.load('drive', 'v2');\ngapi.load('picker',null);", timeout=5.0)
    print('Picker API loaded')
    sgdp.enable()
    
    return None


def logout() -> None:
    del app.storage.user['access_token']
    del app.storage.user['user_info']
    ui.navigate.to('/')


@app.get('/auth')
async def google_oauth(request: Request) -> RedirectResponse:
    try:
        access_token = await oauth.google.authorize_access_token(request)
        user_info = access_token.get('userinfo', {})
        if _is_valid(user_info):
            app.storage.user['access_token'] = access_token
            app.storage.user['user_info'] = user_info
    except (OAuthError, Exception):
        logging.exception('could not authorize access token')
    return RedirectResponse('/')


def _is_valid(user_info: dict) -> bool:
    try:
        return all([
            int(user_info.get('exp', 0)) > int(time.time()),
            user_info.get('aud') == GOOGLE_CLIENT_ID,
            user_info.get('iss') in {'https://accounts.google.com', 'accounts.google.com'},
            str(user_info.get('email_verified')).lower() == 'true',
        ])
    except Exception:
        return False


ui.run(
    host='localhost',  # this ensures that you can run the app locally, accessing via http://127.0.0.1:8080 is not supported by Google OAuth2
    storage_secret='random secret goes here',
)