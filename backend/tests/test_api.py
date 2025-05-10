from app.auth.jwt import create_access_token
from fastapi import status


def test_root_endpoint(client):
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "version" in data
    assert "description" in data


def test_health_endpoint(client):
    """헬스 체크 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_me_endpoint_unauthorized(client):
    """인증 없이 /api/me 엔드포인트 접근 테스트"""
    response = client.get("/api/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_endpoint_authorized(client, test_env):
    """인증과 함께 /api/me 엔드포인트 접근 테스트"""
    # 테스트 JWT 토큰 생성
    token = create_access_token(
        {"sub": "123", "email": "test@example.com", "role": "user", "name": "Test User"}
    )

    # 쿠키에 토큰 설정
    client.cookies.set("session_token", token)

    # 인증된 요청
    response = client.get("/api/me")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "123"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"


def test_protected_endpoint(client, test_env):
    """보호된 엔드포인트 테스트"""
    # 테스트 JWT 토큰 생성
    token = create_access_token({"sub": "123", "email": "test@example.com"})

    # 쿠키에 토큰 설정
    client.cookies.set("session_token", token)

    # 보호된 엔드포인트 요청
    response = client.get("/api/protected")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "user" in data
    assert data["user"]["user_id"] == "123"
