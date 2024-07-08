import requests

NAVERWORKS_CLIENT_ID = 'GqyMZ3FGt0LFkBTjl5KH'
NAVERWORKS_CLIENT_SECRET = 'knjbifyZLU'
NAVERWORKS_REDIRECT_URI = 'https://qphcfosgo8apg8euvibmhd.streamlit.app/?page=callback'

def get_naverworks_login_url():
    return (
        f"https://auth.worksmobile.com/oauth2/v2.0/authorize"
        f"?response_type=code"
        f"&client_id={NAVERWORKS_CLIENT_ID}"
        f"&redirect_uri={NAVERWORKS_REDIRECT_URI}"
        f"&state=naverworks"
        f"&scope=bot"
    )

def get_naverworks_token(code, state):
    token_url = "https://auth.worksmobile.com/oauth2/v2.0/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'client_id': NAVERWORKS_CLIENT_ID,
        'client_secret': NAVERWORKS_CLIENT_SECRET,
        'code': code,
        'state': state,
        'redirect_uri': NAVERWORKS_REDIRECT_URI
    }
    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()  # 오류가 발생하면 예외를 발생시킵니다.
    token_json = response.json()
    return token_json.get('access_token')

def get_naverworks_user_info(token):
    user_info_url = "https://www.worksapis.com/v1.0/users/me"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(user_info_url, headers=headers)
    response.raise_for_status()  # 오류가 발생하면 예외를 발생시킵니다.
