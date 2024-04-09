import pytest
from tests.conftest import async_client, redis_session
from httpx import AsyncClient
from app.utils.token_helper import TokenHelper

class TestUser:

    @classmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "username, email, password, status_code", 
        [
            ("test", "test@test.com", "TestPass123", 200),
            ("test_client", "test_client@gmail.com", "TestPass123", 200),
            ("test", "sga@test.com", "TestPass123", 409),
            ("sga", "test@test.com", "TestPass123", 409),
            ("sergey", "sergey@test.com", "test", 422),
            ("il", "il@test.com", "TestPass123", 422),
            ("roman", "romantest.com", "TestPass123", 422),
        ]
    )
    async def test_create_user(
        self, 
        username,
        email,
        password,
        status_code,
        async_client: AsyncClient
    ):
        response = await async_client.post(
            "/auth/signup",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        assert response.status_code == status_code

    @classmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "username, password, status_code", 
        [
            ("test_client", "TestPass123", 200),
            ("sergey", "Levrone44!", 401),
        ]
    )
    async def test_login_user(
        self, 
        username,
        password,
        status_code,
        async_client: AsyncClient
    ):
        response = await async_client.post(
            "/auth/login",
            json={
                "username": username,
                "password": password
            }
        )

        assert response.status_code == status_code
        return response.json()["access_token"] if status_code == 200 else None
    

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "username, password, status_code",
        [
            ("test_client", "TestPass123", 200),
            ("sergey", "Levrone44!", 401),
        ]
    )
    async def test_refresh_token(
        self, 
        username,
        password,
        status_code,
        redis_session, 
        async_client: AsyncClient
    ):
        access_token = await self.test_login_user(username, password, status_code, async_client)

        response = await async_client.post(
            "/auth/token/refresh",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status_code

        if access_token:
            user_id = TokenHelper.decode(access_token)['sub']
            refresh_token = await redis_session.get(f"refresh_token:{user_id}")

            assert refresh_token != None