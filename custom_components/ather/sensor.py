from homeassistant.components.sensor import HomeAssistant, SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfLength, PERCENTAGE
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    coordinators = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    # Dynamically discover and register entities for every found scooter loop context
    for uuid, coordinator in coordinators.items():
        sensors.extend([
            AtherSensor(coordinator, "battery_soc", "Battery Level", SensorDeviceClass.BATTERY, PERCENTAGE, SensorStateClass.MEASUREMENT),
            AtherSensor(coordinator, "odo", "Odometer", SensorDeviceClass.DISTANCE, UnitOfLength.KILOMETERS, SensorStateClass.TOTAL_INCREASING),
            AtherSensor(coordinator, "range", "Current Range", SensorDeviceClass.DISTANCE, UnitOfLength.KILOMETERS, SensorStateClass.MEASUREMENT),
            AtherSensor(coordinator, "mode", "Current Mode", None, None, None),
            AtherSensor(coordinator, "vehicle_state", "Vehicle State", None, None, None),
            AtherSensor(coordinator, "last_synced_time", "Last Sync Time", SensorDeviceClass.TIMESTAMP, None, None),
        ])

        for mode in ["eco", "ride", "sport", "warp", "smart_eco"]:
            sensors.append(AtherModeRangeSensor(coordinator, mode))

    async_add_entities(sensors)


class AtherSensor(SensorEntity):
    def __init__(self, coordinator, key, name, device_class, unit, state_class) -> None:
        self.coordinator = coordinator
        self._key = key
        self._attr_name = f"{coordinator.name} {name}"
        self._attr_unique_id = f"ather_{key}_{coordinator.uuid}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.uuid)},
            name=coordinator.name,
            manufacturer="Ather Energy",
            model=coordinator.model,
        )

    @property
    def native_value(self):
        val = self.coordinator.data.get(self._key)
        if self._key == "last_synced_time" and val:
            from datetime import datetime, timezone
            return datetime.fromtimestamp(val / 1000, tz=timezone.utc)

        # Capitalize the vehicle state string (e.g., "sleep" -> "Sleep")
        if self._key == "vehicle_state" and isinstance(val, str):
            return val.capitalize()

        return val

    async def async_added_to_hass(self):
        self.coordinator._listeners.append(self.async_write_ha_state)


class AtherModeRangeSensor(SensorEntity):
    def __init__(self, coordinator, mode) -> None:
        self.coordinator = coordinator
        self._mode = mode
        formatted_mode = mode.replace("_", " ").title()

        self._attr_name = f"{coordinator.name} Range ({formatted_mode})"
        self._attr_unique_id = f"ather_range_{mode}_{coordinator.uuid}"
        self._attr_device_class = SensorDeviceClass.DISTANCE
        self._attr_native_unit_of_measurement = UnitOfLength.KILOMETERS

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.uuid)},
            name=coordinator.name,
            manufacturer="Ather Energy",
            model=coordinator.model,
        )

    @property
    def native_value(self):
        mode_ranges = self.coordinator.data.get("mode_range", {})
        return mode_ranges.get(self._mode)

    async def async_added_to_hass(self):
        self.coordinator._listeners.append(self.async_write_ha_state)