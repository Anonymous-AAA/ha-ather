import aiohttp
import asyncio
import json
import logging
from yarl import URL
from .const import BASE_URL, WS_URL, HEADERS

_LOGGER = logging.getLogger(__name__)

class AtherAPI:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.token = None

    async def generate_otp(self, email):
        url = f"{BASE_URL}/auth/v2/generate-login-otp"
        payload = {"email": email, "contact_no": "", "country_code": "", "notification_medium": {"whatsapp": False, "sms": False}}
        headers = {**HEADERS, "authorization": "Bearer"}
        async with self.session.post(url, json=payload, headers=headers) as resp:
            return await resp.json()

    async def verify_otp(self, email, otp):
        url = f"{BASE_URL}/auth/v2/verify-login-otp"
        payload = {"email": email, "contact_no": "", "userOtp": otp, "is_mobile_login": True, "country_code": "IN"}
        headers = {**HEADERS, "authorization": "Bearer"}
        async with self.session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            if "token" in data:
                self.token = data["token"]
            return data

    async def get_scooters(self, token):
        url = f"{BASE_URL}/api/v2/auth/user/scooters/firebase-dbs"
        headers = {"authorization": f"Bearer {token}", "user-agent": "okhttp/5.2.1"}
        async with self.session.get(url, headers=headers) as resp:
            return await resp.json()

    async def get_scooter_properties(self, token, uuid):
        url = f"{BASE_URL}/api/v1/devices/shadows/scooters/properties?uuid={uuid}&state=reported"
        headers = {
            "accept": "application/json",
            "accept-charset": "UTF-8",
            "authorization": f"Bearer {token}",
            "user-agent": "ktor-client"
        }
        async with self.session.get(url, headers=headers) as resp:
            return await resp.json()

    async def start_websocket(self, token, uuid, callback):
        url_str = WS_URL.format(uuid=uuid)
        url_obj = URL(url_str)

        base_headers = {
            "Authorization": f"Bearer {token}",
            "Connection": "Upgrade",
            "Host": "cerberus.ather.io",
            "Sec-WebSocket-Extensions": "permessage-deflate",
            "Sec-WebSocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": "ktor-client"
        }

        while True:
            try:
                # Dynamic copy of base headers for this connection attempt
                headers = base_headers.copy()

                # Check the session cookie jar for any cookies saved from previous handshakes
                cookies = self.session.cookie_jar.filter_cookies(url_obj)
                if cookies:
                    cookie_header = "; ".join([f"{k}={v.value}" for k, v in cookies.items()])
                    headers["Cookie"] = cookie_header
                    _LOGGER.debug(f"Sending saved cookies for {uuid}: {cookie_header}")

                _LOGGER.info(f"Connecting to Ather WebSocket for scooter {uuid}...")
                async with self.session.ws_connect(url_str, headers=headers,heartbeat=30) as ws:
                    await ws.send_json({"paths": ["telemetry.bike"]})

                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            if "telemetry.bike" in data:
                                callback(data["telemetry.bike"])
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
            except Exception as e:
                _LOGGER.error(f"WebSocket error for {uuid}: {e}")

            # Reconnect delay
            await asyncio.sleep(10)