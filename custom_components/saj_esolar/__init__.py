"""The eSolar Greenheiss component."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .api import EsolarApiClient, EsolarProvider, SAJeSolarMeterData
from .const import (
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_SENSORS,
    CONF_USERNAME,
    DOMAIN,
)
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
