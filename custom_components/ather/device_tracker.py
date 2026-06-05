from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    coordinators = hass.data[DOMAIN][entry.entry_id]
    trackers = []

    for uuid, coordinator in coordinators.items():
        trackers.append(AtherTracker(coordinator))

    async_add_entities(trackers)

class AtherTracker(TrackerEntity):
    def __init__(self, coordinator) -> None:
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Location"
        self._attr_unique_id = f"ather_tracker_{coordinator.uuid}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.uuid)},
            name=coordinator.name,
            manufacturer="Ather Energy",
            model=coordinator.model,
        )

    @property
    def latitude(self):
        gps = self.coordinator.data.get("gps_location", {})
        return gps.get("lat")

    @property
    def longitude(self):
        gps = self.coordinator.data.get("gps_location", {})
        return gps.get("lng")

    @property
    def location_accuracy(self):
        gps = self.coordinator.data.get("gps_location", {})
        return gps.get("Accuracy", 0)

    async def async_added_to_hass(self):
        self.coordinator._listeners.append(self.async_write_ha_state)