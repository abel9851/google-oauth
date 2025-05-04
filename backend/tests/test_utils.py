import base64

import pytest
from app.auth.utils import (
    decrypt_refresh_token,
    encrypt_refresh_token,
    generate_nonce,
    generate_state,
)


def test_generate_state():
    # 상태 생성 테스트
    state = generate_state()
    assert isinstance(state, str)
    assert len(state) > 20  # 충분한 엔트로피를 가지는지 확인


def test_generate_nonce():
    # 논스 생성 테스트
    nonce = generate_nonce()
    assert isinstance(nonce, str)
    assert len(nonce) > 16  # 충분한 엔트로피를 가지는지 확인


def test_encrypt_decrypt_refresh_token():
    # 암호화/복호화 테스트
    original_token = "test-refresh-token"

    # 암호화
    encrypted, iv, tag = encrypt_refresh_token(original_token)

    # 결과 확인
    assert encrypted is not None
    assert iv is not None
    assert tag is not None

    # base64로 인코딩되었는지 확인
    try:
        base64.b64decode(encrypted)
        base64.b64decode(iv)
        base64.b64decode(tag)
    except Exception:
        pytest.fail("Invalid base64 encoding")

    # 복호화 및 원본과 일치하는지 확인
    decrypted = decrypt_refresh_token(encrypted, iv, tag)
    assert decrypted == original_token
