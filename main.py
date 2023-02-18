import os
from random import randint
from pathlib import Path
from urllib import parse

import requests
from dotenv import load_dotenv


def download_image(url, name, params=None):
    filename = Path.cwd() / name
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(filename, "wb") as file:
        file.write(response.content)


def get_file_extension(file_url):
    url_parts = parse.urlsplit(file_url, scheme="", allow_fragments=True)
    path = parse.unquote(url_parts[2], encoding="utf-8", errors="replace")
    return os.path.splitext(path)[1]


def get_photo_upload_server(group_id, token):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    headers = {'Authorization': f'Bearer {token}'}
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


def save_photo_to_group(server, photo, hash_code, group_id, token):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'server': server,
        'photo': photo,
        'hash': hash_code,
        'v': '5.131',
        'group_id': group_id
    }
    response = requests.post(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()['response']


def puplish_photo(message, owner_id, id, group_id, token):
    url = 'https://api.vk.com/method/wall.post'
    headers = {'Authorization': f'Bearer {token}'}
    owner_id, media_id = owner_id, id
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


def get_rand_comic(file_name):
    url = f'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    max_num = response.json()['num']
    url = f'https://xkcd.com/{randint(1, max_num)}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic = response.json()
    img_url = comic['img']
    ext = get_file_extension(img_url)
    file_name_ext = f'{file_name}{ext}'
    download_image(img_url, file_name_ext)
    return comic['alt'], file_name_ext


def main():
    load_dotenv()
    token = os.getenv('VK_APP_TOKEN')
    group_id = os.getenv('VK_GROUP_ID')
    comment, file_name = get_rand_comic('image')
    try:
        uri = get_photo_upload_server(group_id, token)
        upload_result = upload_photo(uri, file_name)
        save_result = save_photo_to_group(
            upload_result['server'],
            upload_result['photo'],
            upload_result['hash'],
            group_id,
            token
        )
        puplish_photo(comment,save_result[0]['owner_id'], save_result[0]['id'], group_id, token)
    finally:
        os.remove(file_name)


if __name__=='__main__':
    main()
