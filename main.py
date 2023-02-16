import os
from random import randint
from pathlib import Path
from urllib import parse

import requests
from dotenv import load_dotenv


def load_image(url, name, dir='', params=None):
    if dir:
        os.makedirs(dir, exist_ok=True)
    filename = Path.cwd()/ dir / name
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(filename, "wb") as file:
        file.write(response.content)


def get_file_extension(file_url):
    url_parts = parse.urlsplit(file_url, scheme="", allow_fragments=True)
    path = parse.unquote(url_parts[2], encoding="utf-8", errors="replace")
    return os.path.splitext(path)[1]


def get_photo_upload_server(group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    headers = {'Authorization': f'Bearer {TOKEN}'}
    params = {
        'group_id': group_id,
        'v': '5.131'
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    server_params = response.json()
    return server_params['response']['upload_url']


def upload_photo(uri, file_name):
    with open(file_name, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(uri, files=files)
        response.raise_for_status()
    return response.json()


def save_photo_to_group(photo_params, group_id):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    headers = {'Authorization': f'Bearer {TOKEN}'}
    photo_params['v'] = '5.131'
    photo_params['group_id'] = group_id
    response = requests.post(url, params=photo_params, headers=headers)
    response.raise_for_status()
    return response.json()['response']


def puplic_photo(message, save_result, group_id):
    url = 'https://api.vk.com/method/wall.post'
    headers = {'Authorization': f'Bearer {TOKEN}'}
    owner_id, media_id = save_result[0]['owner_id'], save_result[0]['id']
    params = {
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'message': message,
        'attachments': f'photo{owner_id}_{media_id}',
        'v': '5.131'
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_comics(comics_id, file_name):
    url = f'https://xkcd.com/{comics_id}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()
    img_url = comics['img']
    ext = get_file_extension(img_url)
    file_name_ext = f'{file_name}{ext}'
    load_image(img_url, file_name_ext)
    return comics['alt'], file_name_ext


def get_rand_comics(file_name):
    url = f'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    max_num = response.json()['num']
    comics_id = randint(1, max_num)
    return get_comics(comics_id, file_name)


if __name__=='__main__':
    load_dotenv()
    TOKEN = os.getenv('VK_APP_TOKEN')
    GROUP_ID = os.getenv('GROUP_ID')
    comment, file_name = get_rand_comics('image')
    uri = get_photo_upload_server(GROUP_ID)
    photo = upload_photo(uri, file_name=file_name)
    save_result = save_photo_to_group(photo_params=photo, group_id=GROUP_ID)
    puplic_photo(message=comment,
                       save_result=save_result, group_id=GROUP_ID)
    os.remove(file_name)
