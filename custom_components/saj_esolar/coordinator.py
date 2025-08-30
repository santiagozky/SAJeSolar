"""Coordinator for eSolar integration."""

from datetime import timedelta
import logging

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import EsolarApiClient  # Replace with your actual API client import


_LOGGER = logging.getLogger(__name__)


class EsolarDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching eSolar data from the API."""

    def __init__(self, hass: HomeAssistant, api_client: EsolarApiClient) -> None:
        """Initialize the esolar coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="eSolar Data Update Coordinator",
            update_interval=timedelta(minutes=5),
            always_update=True,
        )
        self.api_client = api_client

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                # Grab active context variables to limit data required to be fetched from API
                # Note: using context is not required if there is no need or ability to limit
                # data retrieved from API.
                listening_idx = set(self.async_contexts())
                return await self.my_api.fetch_data(listening_idx)
        except ApiAuthError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
