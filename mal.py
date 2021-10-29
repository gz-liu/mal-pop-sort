import json
import requests
import secrets
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv() # create .env file and load your client id and secret there

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


# oath2 Code Verifier / Code Challenge.
def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]


# authentication url.
def print_new_authorisation_url(code_challenge: str):
    global CLIENT_ID

    url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&code_challenge={code_challenge}'
    print(f'Authorise your application by clicking here: {url}\n')


# access token generated in url, copy paste in console
def generate_new_token(authorisation_code: str, code_verifier: str) -> dict:
    global CLIENT_ID, CLIENT_SECRET

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': authorisation_code,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }

    response = requests.post(url, data)
    response.raise_for_status()  # Check whether the requests contains errors

    token = response.json()
    response.close()
    print('Token generated successfully!')

    with open('token.json', 'w') as file:
        json.dump(token, file, indent = 4)
        print('Token saved in "token.json"')

    return token


# API and auth check for user info
def print_user_info(access_token: str):
    url = 'https://api.myanimelist.net/v2/users/@me'
    response = requests.get(url, headers = {
        'Authorization': f'Bearer {access_token}'
        })
    
    response.raise_for_status()
    user = response.json()
    response.close()

    print(f"\n>>> Authentication worked for: {user['name']} <<<")
    return user['name']

# fetch user mangalist and cache locally
def get_manga_list(username):
    url = "https://api.jikan.moe/v3/user/{}/mangalist".format(username)
    response = requests.get(url)
    manga_list = response.json()
    df = pd.DataFrame(manga_list['manga'])
    return df

# finds popularity of mangalist and sorts it in order of least popular manga first
def sort_popularity(manga_list, access_token: str):
    popularity_list = list()
    
    for index, row in manga_list.iterrows():
        url = "https://api.myanimelist.net/v2/manga/{id}?fields=popularity".format(id = str(row['mal_id']))
        response = requests.get(url, headers = {
            'Authorization': f'Bearer {access_token}'
            })
        manga_stats = response.json()
        popularity_list.append(manga_stats['popularity'])

    popularity_df = manga_list
    popularity_df['popularity'] = popularity_list
    popularity_df = popularity_df[manga_list.score != 0]    # truncate manga that hasn't been scored
    popularity_df = popularity_df.sort_values(by=['popularity'], ascending=False) 
    cwd = os.getcwd()
    path = cwd + "/population_list.csv"
    popularity_df.to_csv(path)  # writes csv to current directory

if __name__ == '__main__':
    code_verifier = code_challenge = get_new_code_verifier()
    print_new_authorisation_url(code_challenge)

    authorisation_code = input('Copy-paste the Authorisation Code: ').strip()
    token = generate_new_token(authorisation_code, code_verifier)

    username = print_user_info(token['access_token'])
    manga_list = get_manga_list(username)

    sort_popularity(manga_list, token['access_token'])
