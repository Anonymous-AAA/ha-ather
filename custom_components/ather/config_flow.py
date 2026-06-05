import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .api import AtherAPI

class AtherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self.email = None
        self.api = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.email = user_input["Email"]
            self.api = AtherAPI(async_get_clientsession(self.hass))
            await self.api.generate_otp(self.email)
            return await self.async_step_otp()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("Email"): str})
        )

    async def async_step_otp(self, user_input=None):
        if user_input is not None:
            otp = user_input["OTP"]
            response = await self.api.verify_otp(self.email, otp)

            if response.get("status") == "success":
                return self.async_create_entry(
                    title=f"Ather ({self.email})",
                    data={"email": self.email, "token": response["token"]}
                )
            else:
                return self.async_show_form(
                    step_id="otp",
                    data_schema=vol.Schema({vol.Required("OTP"): str}),
                    errors={"base": "invalid_auth"}
                )

        return self.async_show_form(
            step_id="otp",
            data_schema=vol.Schema({vol.Required("OTP"): str})
        )