"""The eSolar Greenheiss component."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import EsolarApiClient, EsolarProvider, SAJeSolarMeterData
from .const import CONF_PASSWORD, CONF_PLANT_ID, CONF_SENSORS, CONF_USERNAME, DOMAIN
from .coordinator import EsolarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities=None
) -> bool:
    """Setup entities."""
    _LOGGER.debug("Setting up eSolar entry: %s", entry.entry_id)
    config = entry.data

    provider = EsolarProvider(
        config.get("provider_domain"),
        config.get("provider_path"),
        config.get("https"),
        config.get("provider_ssl"),
    )
    config = SAJeSolarMeterData(
        config.get(CONF_USERNAME),
        config.get(CONF_PASSWORD),
        config.get(CONF_SENSORS),
        config.get(CONF_PLANT_ID),
        provider,
    )

    api = EsolarApiClient(hass, config)
    coordinator = EsolarDataUpdateCoordinator(hass, api)

    # Perform the first refresh
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator for platforms to access
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
