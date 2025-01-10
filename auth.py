import requests
from fastapi import HTTPException

KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

def verify_kakao_token(access_token: str):
    """
    카카오 API를 통해 액세스 토큰의 유효성을 검증하고 사용자 정보를 가져옵니다.
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(KAKAO_USER_INFO_URL, headers=headers)
        response.raise_for_status()  # HTTP 오류를 자동으로 감지하여 예외 처리
    except requests.RequestException as exc:
        raise HTTPException(status_code=400, detail=f"Kakao API error: {str(exc)}")

    return response.json()
