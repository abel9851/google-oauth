import time
from datetime import timedelta

import jwt
import pytest
from app.auth.jwt import create_access_token, verify_token
from app.config import settings
from fastapi import HTTPException


def test_create_access_token():
    # 테스트 데이터
    user_data = {"sub": "123", "email": "test@example.com", "role": "user"}

    # 토큰 생성
    token = create_access_token(user_data)

    # 토큰 형식 확인
    assert isinstance(token, str)

    # 토큰 디코딩 확인
    payload = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )

    # 필수 필드 확인
    assert payload["sub"] == "123"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "user"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload
    assert "kid" in payload


def test_token_expiry():
    # 테스트 데이터
    user_data = {"sub": "123"}

    # 짧은 만료 시간으로 토큰 생성
    token = create_access_token(user_data, expires_delta=timedelta(seconds=1))

    # 토큰이 유효한지 확인
    payload = verify_token(token)
    assert payload["sub"] == "123"

    # 만료를 기다린 후 예외가 발생하는지 확인
    time.sleep(2)
    with pytest.raises(HTTPException) as excinfo:
        verify_token(token)

    # 오류 상태 코드 확인
    assert excinfo.value.status_code == 401
    assert "Token expired" in excinfo.value.detail
