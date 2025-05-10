import json
from unittest.mock import patch

from fastapi import status


# Google 응답 모킹
class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)

    def json(self):
        return self.json_data


def test_authorize_endpoint(client, test_env):
    # /oauth/authorize 엔드포인트 테스트
    response = client.get("/oauth/authorize")

    # 상태 코드 확인
    assert response.status_code == status.HTTP_302_FOUND

    # 리디렉션 URL 확인
    location = response.headers["Location"]
    assert "accounts.google.com" in location
    assert "response_type=code" in location
    assert "state=" in location
    assert "nonce=" in location

    # 쿠키 설정 확인
    cookies = response.cookies
    assert "oauth_state" in cookies
    assert "oauth_nonce" in cookies


@patch("requests.post")
@patch("app.auth.oauth.verify_id_token")
def test_oauth_callback(mock_verify_id_token, mock_post, client, test_env, db):
    # verify_id_token 모킹
    mock_verify_id_token.return_value = {
        "sub": "12345",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg",
        "nonce": "test-nonce",
    }

    # Google 토큰 응답 모킹
    mock_post.return_value = MockResponse(
        {
            "access_token": "test-access-token",
            "id_token": "test-id-token",
            "refresh_token": "test-refresh-token",
        },
        200,
    )

    # state 쿠키 설정
    client.cookies.set("oauth_state", "test-state")
    client.cookies.set("oauth_nonce", "test-nonce")

    # 콜백 호출
    response = client.get("/oauth2/callback?code=test-code&state=test-state")

    # 응답 확인
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["Location"] == "http://localhost:5173/"

    # 세션 쿠키 확인
    assert "session_token" in response.cookies
