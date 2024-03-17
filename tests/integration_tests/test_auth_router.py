from httpx import AsyncClient
import pytest


class TestAuth:

    @pytest.mark.parametrize("username, email, password, status_code", [
        ("kari", "kari@example.com", "Password123!@#$", 200),
        ("test", "test@example.com", "Password123!@#$%^", 200),
        (None, "ekwize@example.com", "Password123", 200),
        ("", "sga@example.com", "Password123", 200),
        ("il", "il@example.com", "Password123", 200),
        ("il", "kk@example.com", "Password123", 409),
        ("test_user", "test@example.com", "Password123", 409),
        ("il", "kari@example.com", "Password123", 409),
        ("user", "test@example.com", "password", 422),
        ("ikzik", "ikzik@example.com", "12345678", 422),
        ("test_user", "test@example.com", "123456789012345678901234567890123", 422),
        ("test_user", "test@example.com", "password123", 422),
        ("test_user", "test@example.com", "", 422),
        ("test_user", None, "Password123", 422),
        ("test_user", None, "password123", 422),
        ("test_user", "test@example.com", None, 422),
        ("test_user", "test@example.com", "password123!@#$", 422),
        ("test_user", "test@example.com", "password123!@#$%^", 422),
    ])
    async def test_create_user(self, username, email, password, status_code, ac: AsyncClient):
        response = await ac.post(
            "/auth/sign-up",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )

        assert response.status_code == status_code

    
    # @pytest.mark.parametrize("email, password, status_code", [
    #     ("kari@example.com", "Password123!@#$", 200),
    #     ("test@example.com", "Password123!@#$%^", 200),
    #     ("ekwize@example.com", "Password123", 200),
    #     ("sga@example.com", "Password123", 200),
    #     ("il@example.com", "Password123", 200),
    #     ("lsjkfb@mail.ru", "auvlj@oubkjv", 404)
    # ]

    # )
    # async def test_login_user(self, email, password, status_code, ac: AsyncClient):
    #     response = await ac.post(
    #         "/auth/login",
    #         json={
    #             "email": email,
    #             "password": password
    #         }
    #     )
    #     assert response.status_code == status_code

    # @pytest.mark.parametrize("status_code", argvalues=[200])
    # async def test_refresh_token(self, status_code, authenticated_ac: AsyncClient):
    #     response = await authenticated_ac.post(
    #         "/auth/token/refresh"
    #     )
    #     assert response.status_code == status_code

    # @pytest.mark.parametrize("auth_status_code, not_auth_status_code", [
    #     (200, 401)
    # ])
    # async def test_logout_user(self, auth_status_code, not_auth_status_code, ac: AsyncClient, authenticated_ac: AsyncClient):
    #     auth_response = await authenticated_ac.delete(
    #         "/auth/logout"
    #     )
    #     not_auth_response = await ac.delete(
    #         "/auth/logout"
    #     )
    #     assert auth_response.status_code == auth_status_code
    #     assert not_auth_response.status_code == not_auth_status_code
