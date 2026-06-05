from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinators = hass.data[DOMAIN][entry.entry_id]
    binary_sensors = []

    for uuid, coordinator in coordinators.items():
        binary_sensors.append(AtherBinarySensor(coordinator, "incognito", "Incognito Status"))

    async_add_entities(binary_sensors)


class AtherBinarySensor(BinarySensorEntity):
    def __init__(self, coordinator, key, name):
        self.coordinator = coordinator
        self._key = key
        self._attr_name = f"{coordinator.name} {name}"
        self._attr_unique_id = f"ather_{key}_{coordinator.uuid}"

        # Link to the shared scooter device block
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.uuid)},
            name=coordinator.name,
            manufacturer="Ather Energy",
            model=coordinator.model,
        )

    @property
    def is_on(self) -> bool:
        # Returns True if incognito is active, False otherwise
        return bool(self.coordinator.data.get(self._key, False))

    async def async_added_to_hass(self):
        self.coordinator._listeners.append(self.async_write_ha_state)
