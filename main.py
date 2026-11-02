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

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={'scope': 'openid email profile'},
)


@ui.page('/')
async def main(request: Request) -> RedirectResponse | None:
    user_info = app.storage.user.get('user_info', {})
    if not _is_valid(user_info):
        app.storage.user.pop('user_info', None)
        return await oauth.google.authorize_redirect(request, request.url_for('google_oauth'))
    
    user_db_info = {"email":user_info.get("email", ""),
                    "discord":'',
                    "name":user_info.get("name") or user_info.get("email", ""),
                    "pfp":user_info.get("picture"),
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
            ui.image(user_db_info[0].pfp) \
                .classes('rounded-full size-8 ml-4')

    with ui.footer(value=False) as footer:
        ui.label('Footer')

    with ui.left_drawer().classes('bg-blue-100') as left_drawer:
        ui.label('Left menu')

    with ui.right_drawer().classes('bg-blue-100') as right_drawer:
        untextbox = ui.input(label='Update Username', placeholder='Start typing...',
            validation={'Username must be between 3 and 40 characters': lambda value: len(value) < 41 and len(value) > 2})
        async def update_username():
            if untextbox.validate():
                user_db_info[0].name = untextbox.value
                await user_db_info[0].save()
                unlabel.set_text(f'Hi {user_db_info[0].name}!')
        untextbox.on('keydown.enter',update_username)
        dark = ui.dark_mode()
        async def update_dorl():
            user_db_info[0].dorl = dorlswtich.value
            await user_db_info[0].save()
        dorlswtich = ui.switch('Dark Mode',on_change=update_dorl).bind_value(dark)
        dorlswtich.set_value(user_db_info[0].dorl)
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
    return None


def logout() -> None:
    del app.storage.user['user_info']
    ui.navigate.to('/')


@app.get('/auth')
async def google_oauth(request: Request) -> RedirectResponse:
    try:
        user_info = (await oauth.google.authorize_access_token(request)).get('userinfo', {})
        if _is_valid(user_info):
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