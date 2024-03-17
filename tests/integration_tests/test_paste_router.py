from httpx import AsyncClient
import pytest
from tests.conftest import ac, authenticated_ac

class TestPaste:

    @pytest.mark.parametrize("text,title,category,password,exposure,expiration,status_code", [
        ("Hello, world!", None, None, None, "Public", "Never", 200), 
        (None, "Test Paste", None, None, "Private", "Burn after read", 422), 
        ("Hello, world!", None, None, None, "Private", "Never", 200), 
        ("This is a test paste.", None, "Programming", None, "Public", "10 Minutes", 200), 
        ("Optional parameters test:\n- title: None\n- category: Programming\n- password: secret\n- exposure: Private\n- expiration: 1 Day", None, "Programming", "secret", "Private", "1 Day", 200), 
        ("Another test paste.", None, None, None, None, "Nevr", 422), 
        (None, None, None, "testpassword", None, "Never", 422), 
        (None, None, "Miscellaneous", None, "Public", "2 Days", 422), 
        ("All optional parameters test:\n- title: Test Paste\n- category: Programming\n- password: optional\n- exposure: Private\n- expiration: 1 Week", "Test Paste", "Programming", "optional", "Private", "1 Week", 200), 
        (None, None, None, None, "Public", "1 Year", 422),
        ("iouhl", None, None, None, "Publ", "1 Year", 422),
        ]
    )
    async def test_create_paste(
        self,
        text, 
        title, 
        category, 
        password, 
        exposure, 
        expiration,
        status_code, 
        authenticated_ac: AsyncClient
    ):
        response = await authenticated_ac.post(
            "/", 
            json={
                "text": text,
                "title": title, 
                "category": category, 
                "password": password, 
                "exposure": exposure, 
                "expiration": expiration,
            }
        )

        assert response.status_code == status_code

    # @pytest.mark.parametrize("id, password, status_code", [
    #     ("Jf5YXhT2", None, 403),
    #     ("")
    # ])
    # async def test_view_paste(self, id, password, status_code, ac: AsyncClient, ):
    #     response = await ac.post(
    #         f"/{id}",
    #         json={
    #             "id": id,
    #             "password": password
    #         }
    #     )
    #     response.status_code == status_code

    