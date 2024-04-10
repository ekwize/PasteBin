import pytest
from tests.conftest import async_client
from httpx import AsyncClient
from tests.test_user import TestUser


class TestPaste:

    ### Create paste (two functions: for guest and authorized user) ###
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "text, title, category, password, exposure, expiration, status_code", 
        [
            ("text1", "title1", "category1", "password1", "Public", "Never", 200),
            ("text2", "title2", "category2", "password2", "Private", "Burn after read", 200),
            ("", "title3", "category3", "password3", "Public", "10 Minutes", 422),
            ("text10", "title10", "category10", "   ", "Private", "Never", 422),
        ]
    )
    async def test_create_guest_paste(
        self, 
        text,
        title,
        category,
        password,
        exposure,
        expiration,
        status_code,
        async_client: AsyncClient
    ):
        response = await async_client.post(
            "/paste/create",
            json={
                "text": text,
                "title": title,
                "category": category,
                "password": password,
                "exposure": exposure,
                "expiration": expiration,
                "status_code": status_code,
            }
        )

        assert response.status_code == status_code
        return response.json()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "username, email, user_password, text, title, category, password, exposure, expiration, status_code", 
        [
            ("test1", "test1@gmail.com", "PassWord123", "text1", "title1", "category1", "password1", "Public", "Never", 200),
            ("test2", "test2@gmail.com", "PassWord123", "text2", "title2", "category2", "password2", "Private", "Burn after read", 200),
            ("test3", "test3@gmail.com", "PassWord123", "text10", "title10", "category10", "password10", "Private", "Invalid", 422),
            ("test4", "test4@gmail.com", "PassWord123", "text10", "title10", "category10", "   ", "Private", "Never", 422),
        ]
    )
    async def test_create_auth_user_paste(
        self, 
        username,
        email, 
        user_password,
        text,
        title,
        category,
        password,
        exposure,
        expiration,
        status_code,
        async_client: AsyncClient
    ):
        await TestUser.test_create_user(username, email, user_password, 200, async_client)
        access_token = await TestUser.test_login_user(username, user_password, 200, async_client)

        response = await async_client.post(
            "/paste/create",
            json={
                "text": text,
                "title": title,
                "category": category,
                "password": password,
                "exposure": exposure,
                "expiration": expiration,
                "status_code": status_code,
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status_code
        return (response.json(), access_token)
    
    ### View paste (two functions: for guest and authorized user) ###
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "username, email, user_password, entered_password, text, title, category, paste_password, exposure, expiration, view_guest_status, view_auth_user_status",
        [
            ("test5", "test5@gmail.com", "PassWord123", "password1", "text1", "title1", "category1", "password1", "Public", "Never", 200, 200),
            ("test6", "test6@gmail.com", "PassWord123", "password2", "text2", "title2", "category2", "password2", "Private", "Burn after read", 200, 403),
            ("test7", "test7@gmail.com", "PassWord123", "abc", "text2", "title2", "category2", "password2", "Public", "Burn after read", 403, 403),
        ]
    )
    async def test_guest_view_paste(
        self, 
        username,
        email, 
        user_password,
        entered_password,
        text,
        title,
        category,
        paste_password,
        exposure,
        expiration,
        view_guest_status,
        view_auth_user_status,
        async_client: AsyncClient
    ):

        guest_paste = await self.test_create_guest_paste(
            text,
            title,
            category,
            paste_password,
            exposure,
            expiration,
            200,
            async_client
        )
        auth_user_paste = await self.test_create_auth_user_paste(
            username,
            email, 
            user_password,
            text,
            title,
            category,
            paste_password,
            exposure,
            expiration,
            200,
            async_client
        )

        view_guest_paste_response = await async_client.post(
            "/paste/view",
            json={
                "id": guest_paste["id"],
                "password": entered_password,
            }
        )
        view_auth_user_paste_response = await async_client.post(
            "/paste/view",
            json={
                "id": auth_user_paste[0]["id"],
                "password": entered_password,
            }
        )

        assert view_auth_user_paste_response.status_code == view_auth_user_status
        assert view_guest_paste_response.status_code == view_guest_status

    

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "username, email, user_password, entered_password, text, title, category, paste_password, exposure, expiration, view_guest_status, view_auth_user_status",
        [
            ("test8", "test8@gmail.com", "PassWord123", "password1", "text1", "title1", "category1", "password1", "Public", "Never", 200, 200),
            ("test9", "test9@gmail.com", "PassWord123", "", "text2", "title2", "category2", "password2", "Private", "Burn after read", 403, 200),
            ("test10", "test10@gmail.com", "PassWord123", "abc", "text2", "title2", "category2", "password2", "Public", "Burn after read", 403, 200),
        ]
    )
    async def test_auth_user_view_paste(
        self, 
        username, 
        email, 
        user_password,
        entered_password,
        text,
        title,
        category,
        paste_password,
        exposure,
        expiration,
        view_guest_status,
        view_auth_user_status,
        async_client: AsyncClient
    ):
        guest_paste = await self.test_create_guest_paste(
            text,
            title,
            category,
            paste_password,
            exposure,
            expiration,
            200,
            async_client
        )

        auth_user_paste = await self.test_create_auth_user_paste(
            username,
            email, 
            user_password,
            text,
            title,
            category,
            paste_password,
            exposure,
            expiration,
            200,
            async_client
        )

        view_auth_user_paste_response = await async_client.post(
            "/paste/view",
            json={
                "id": auth_user_paste[0]["id"],
                "password": entered_password,
            },
            headers={"Authorization": f"Bearer {auth_user_paste[1]}"}
        )

        view_guest_paste_response = await async_client.post(
            "/paste/view",
            json={
                "id": guest_paste["id"],
                "password": entered_password,
            },
            headers={"Authorization": f"Bearer {auth_user_paste[1]}"}
        )
        
        assert view_guest_paste_response.status_code == view_guest_status
        assert view_auth_user_paste_response.status_code == view_auth_user_status



    