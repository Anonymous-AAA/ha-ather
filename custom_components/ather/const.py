DOMAIN = "ather"

BASE_URL = "https://cerberus.ather.io"
WS_URL = "wss://cerberus.ather.io/api/v1/ws/devices/shadows/onchange?uuid={uuid}"

HEADERS = {
    "accept": "application/json",
    "accept-charset": "UTF-8",
    "content-type": "application/json",
    "source": "ATHER_APP/13.1.0",
    "user-agent": "Android/15 (Google sdk_gphone64_arm64)",
    "x-device-info": "Google sdk_gphone64_arm64",
    "x-platform": "Android",
    "x-platform-version": "15"
}