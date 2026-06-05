import asyncio
import collections.abc
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .api import AtherAPI

PLATFORMS = ["binary_sensor","device_tracker","sensor"]

def deep_merge(base, update):
    for key, value in update.items():
        if isinstance(value, collections.abc.Mapping):
            base[key] = deep_merge(base.get(key, {}), value)
        else:
            base[key] = value
    return base

class AtherScooterCoordinator:
    def __init__(self, hass: HomeAssistant, api: AtherAPI, token: str, uuid: str, name: str, model: str) -> None:
        self.hass = hass
        self.api = api
        self.token = token
        self.uuid = uuid
        self.name = name
        self.model = model
        self.data = {}
        self._listeners = []

    def update_data(self, new_data):
        self.data = deep_merge(self.data, new_data)
        for listener in self._listeners:
            listener()

    async def start(self):
        # Pass update_data as callback directly to track specific device streaming threads
        self.hass.loop.create_task(self.api.start_websocket(self.token, self.uuid, self.update_data))

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    api = AtherAPI(session)
    token = entry.data["token"]

    scooters_response = await api.get_scooters(token)
    shard_details = scooters_response.get("shardDetails", [])

    if not shard_details:
        return False

    coordinators = {}

    # Iterate through all available scooters linked to the profile
    for shard in shard_details:
        uuid = shard["scooter_uuid"]

        # Pull registration and model metadata per scooter
        prop_response = await api.get_scooter_properties(token, uuid)
        prop_data = prop_response.get("data", {})

        # Fallback to UUID if registration metadata is unavailable
        scooter_name = prop_data.get("registration") or f"Ather {uuid[:6]}"
        scooter_model = prop_data.get("model_type") or "Scooter"

        coordinator = AtherScooterCoordinator(hass, api, token, uuid, scooter_name, scooter_model)
        await coordinator.start()
        coordinators[uuid] = coordinator

    # Store dictionary mapping UUIDs -> Coordinators
    hass.data[DOMAIN][entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True