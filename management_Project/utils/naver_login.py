import requests
import json

NAVER_CLIENT_ID = 'GqyMZ3FGt0LFkBTjl5KH'
NAVER_CLIENT_SECRET = 'knjbifyZLU'
REDIRECT_URI = 'https://qphcfosgo8apg8euvibmhd.streamlit.app/callback'

def get_naver_login_url():
    return f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={NAVER_CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=naver"

def get_naver_token(code, state):
    token_url = f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={NAVER_CLIENT_ID}&client_secret={NAVER_CLIENT_SECRET}&code={code}&state={state}"
    response = requests.get(token_url)
    token_json = response.json()
    return token_json.get('access_token')

def get_naver_user_info(token):
    header = {'Authorization': f'Bearer {token}'}
    user_info_url = "https://openapi.naver.com/v1/nid/me"
    response = requests.get(user_info_url, headers=header)
    return response.json().get('response')
