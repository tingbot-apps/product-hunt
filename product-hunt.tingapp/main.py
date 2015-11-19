import tingbot
from tingbot import *
import requests

state = {'page': 0}
ph_orange = (243, 90, 45)

def get_session():
    s = requests.Session()
    
    r = s.post(
        'https://api.producthunt.com/v1/oauth/token', 
        data={
            'client_id': '5440c344e8635c7008570c4eb5d21026051911f8950b185c04e67a1c8e99e56f',
            'client_secret': "2f0c45633aec9cc23bc1390e4613485a2f7f8615e903857fe78967a4ef20692e",
            'grant_type': 'client_credentials'
        }
    )
    r.raise_for_status()
    
    access_token = r.json()['access_token']
    s.headers.update({'Authorization': 'Bearer %s' % access_token})
    
    state['session'] = s
    
get_session()
    

def download_images():
    import pygame
    s = state['session']
    
    for product in state['posts']:
        r = s.get(product['thumbnail']['image_url'])
        filename = '/tmp/phimg-%i' % product['id']
        
        with open(filename, 'wb') as f:
            f.write(r.content)
        
        product['image'] = Image.load(filename)


@every(minutes=10)
def refresh_feed():
    s = state['session']
    
    r = s.get('https://api.producthunt.com/v1/posts')
    r.raise_for_status()

    state['posts'] = r.json()['posts']
    
    download_images()
    state['page'] = 0
    
    
@every(seconds=15)
def new_page():
    if 'posts' not in state:
        return

    state['page'] += 1
    
    if state['page'] >= len(state['posts']):
        state['page'] = 0


def loop():
    if 'posts' not in state:
        screen.fill(color=ph_orange)
        screen.text('Loading...', color='white')
        return
    
    page_index = state['page']
    product = state['posts'][page_index]
    image = product['image']
    
    # draw image
    screen.fill(color='white')
    screen.image(image, xy=(160, 105))
    
    # draw top bar
    screen.rectangle(
        size=(320,36),
        color=ph_orange,
        align='top',
    )
    screen.image(
        'Producthunt.png',
        xy=(10,7),
        align='topleft'
    )
    screen.text(
        'Top 10',
        xy=(310,10),
        font_size=15,
        color='white',
        align='topright',
    )
    
    # draw bottom bar
    screen.rectangle(
        color=ph_orange,
        size=(320, 61),
        align='bottom',
    )
    title = '#%i %s' % (page_index+1, product['name'])
    screen.text(
        title,
        color='white',
        xy=(15, 187),
        font_size=18,
        align='topleft',
    )
    screen.text(
        product['tagline'],
        color='white',
        xy=(15, 212),
        font_size=13,
        align='topleft',
    )

tingbot.run(loop)
