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
ctype = "web"
with open(f'credentials_{ctype}.json', 'r') as f:
    creds = json.load(f)
    GOOGLE_CLIENT_ID = creds[ctype]["client_id"]
    GOOGLE_CLIENT_SECRET = creds[ctype]["client_secret"]
    GOOGLE_PROJECT_ID = creds[ctype]["project_id"]
    GOOGLE_API_KEY = creds[ctype]["api_key"]
    GOOGLE_PROJECT_NUMBER = creds[ctype]["project_number"]

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/drive', 'prompt': 'consent'},
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
            ui.tab('Rulebooks')
            ui.tab('My Characters')
            ui.tab('My Games')
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
                jstxt = """
                    function pickerCallback(data) {
                        let url = 'nothing';
                        if (data[google.picker.Response.ACTION] == google.picker.Action.PICKED) {
                            const doc = data[google.picker.Response.DOCUMENTS][0];
                            url = doc[google.picker.Document.URL];
                        }
                        getHtmlElement(LABEL_ID).innerText = url;
                    }

                    const view = new google.picker.View(google.picker.ViewId.DOCS);
                    view.setMimeTypes('image/png,image/jpeg,image/jpg');
                    const picker = new google.picker.PickerBuilder()
                        .addView(google.picker.ViewId.DOCS)
                        .setOAuthToken('ACCESS_TOKEN')
                        .setDeveloperKey('API_KEY')
                        .setCallback(pickerCallback)
                        .setAppId('APP_ID')
                        .addView(view)
                        .build();
                    picker.setVisible(true);
                """
                jstxt = jstxt.replace("LABEL_ID",str(label.id))
                jstxt = jstxt.replace("API_KEY",GOOGLE_API_KEY)
                jstxt = jstxt.replace("APP_ID",GOOGLE_PROJECT_NUMBER)
                jstxt = jstxt.replace("ACCESS_TOKEN",access_token["access_token"])
                print(json.dumps(access_token))
                ui.run_javascript(jstxt, timeout=5.0)
            sgdp = ui.button('Select Google Drive Picture',on_click=select_pfp).disable()
            label = ui.label()

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

    with ui.tab_panels(tabs, value='Rulebooks').classes('w-full'):
        with ui.tab_panel('Rulebooks'):
            with ui.link(target='https://www.worldanvil.com/w/planescape-orenji/c/player-s-handbook-category'):
                ui.image('https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/254fe151-4fe6-4bcc-aa04-5d4d1174c22b/uploads/images/2d76932ee1e50c4f7853721662dbadf7.png').classes('w-64')
        with ui.tab_panel('My Characters'):
            with ui.card().tight():
                with ui.image('https://wa-cdn.nyc3.cdn.digitaloceanspaces.com/assets/prod/prodromos-client/images/WorldCover_Default.jpg').classes('w-128 h-32'):
                    ui.image(DEFAULT_PFP).classes('rounded-full size-26 ml-4 mt-4')
                    ui.label('Unnamed Character').classes('ml-40 mr-4 mt-16 text-lg w-full')
                with ui.card_section():
                    with ui.grid(columns=2).classes('items-start'):
                        ui.button('Edit')
                        ui.button('Delete')
            ui.button('Create New Character').classes('w-full')
        with ui.tab_panel('My Games'):
            ui.label('Content of My Games')
            


    ui.add_head_html(f'<script src="https://apis.google.com/js/api.js"></script>')
    ui.add_head_html('<script src="https://accounts.google.com/gsi/client"></script>')
    await ui.run_javascript("gapi.load('picker',null);", timeout=5.0)
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
    title='Primus App',
    favicon='data:image/png;base64,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',
)