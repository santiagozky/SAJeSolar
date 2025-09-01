import logging

import voluptuous as vol

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

from .api import (
    ApiAuthError,
    ApiError,
    EsolarApiClient,
    EsolarProvider,
    SAJeSolarMeterData,
)
from .const import (
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_PROVIDER_DOMAIN,
    CONF_PROVIDER_PATH,
    CONF_PROVIDER_SSL,
    CONF_USERNAME,
    DOMAIN,
)

# Default values from your YAML
DEFAULT_PROVIDER_DOMAIN = "inversores-style.greenheiss.com"
DEFAULT_PROVIDER_PATH = "cloud"
DEFAULT_PROVIDER_SSL = False
SENSOR_CHOICES = ["h1", "saj_sec"]

_LOGGER = logging.getLogger(__name__)


class EsolarGreenheissFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for eSolar Greenheiss."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step from the user."""
        errors = {}

        if user_input is not None:
            try:
                provider = EsolarProvider(
                    user_input["provider_domain"],
                    user_input["provider_path"],
                    "https",
                    user_input["provider_ssl"],
                )
                config = SAJeSolarMeterData(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    [],
                    0,
                    provider,
                )
                api = EsolarApiClient(self.hass, config)
                await api.verifyLogin()
            except ApiAuthError:
                _LOGGER.error("Authentication error")
                errors["base"] = "invalid_auth"
            except ApiError:
                _LOGGER.error("API error")
                errors["base"] = "api error"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown problem"

            if len(errors) == 0:
                # all good
                _LOGGER.error("Errors is empty, so all good %s", errors)
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        # Define the form schema
        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(
                    CONF_PROVIDER_DOMAIN, default=DEFAULT_PROVIDER_DOMAIN
                ): str,
                vol.Optional(CONF_PROVIDER_PATH, default=DEFAULT_PROVIDER_PATH): str,
                vol.Optional(CONF_PROVIDER_SSL, default=DEFAULT_PROVIDER_SSL): bool,
                vol.Optional("sensors", default="saj_sec"): vol.In(SENSOR_CHOICES),
                vol.Optional(CONF_PLANT_ID, default=0): cv.positive_int,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, user_input=None):
        """Handle re-authentication of an existing config entry."""
        errors = {}
        entry_id = self.context.get("entry_id")
        entry = self.hass.config_entries.async_get_entry(entry_id)

        if user_input is not None:
            try:
                provider = EsolarProvider(
                    user_input.get("provider_domain", DEFAULT_PROVIDER_DOMAIN),
                    user_input.get("provider_path", DEFAULT_PROVIDER_PATH),
                    "https",
                    user_input.get("provider_ssl", DEFAULT_PROVIDER_SSL),
                )
                config = SAJeSolarMeterData(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    [],
                    0,
                    provider,
                )
                api = EsolarApiClient(self.hass, config)
                await api.verifyLogin()
            except ApiAuthError:
                _LOGGER.error("Authentication error")
                errors["base"] = "invalid_auth"
            except ApiError:
                _LOGGER.error("API error")
                errors["base"] = "api_error"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown_problem"

            if not errors:
                # Update the existing config entry
                entry.data.update(user_input)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        # Show the form pre-filled with current entry data
        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME, default=entry.data.get(CONF_USERNAME)): str,
                vol.Required(CONF_PASSWORD, default=entry.data.get(CONF_PASSWORD)): str,
                vol.Optional(
                    CONF_PROVIDER_DOMAIN,
                    default=entry.data.get(
                        CONF_PROVIDER_DOMAIN, DEFAULT_PROVIDER_DOMAIN
                    ),
                ): str,
                vol.Optional(
                    CONF_PROVIDER_PATH,
                    default=entry.data.get(CONF_PROVIDER_PATH, DEFAULT_PROVIDER_PATH),
                ): str,
                vol.Optional(
                    CONF_PROVIDER_SSL,
                    default=entry.data.get(CONF_PROVIDER_SSL, DEFAULT_PROVIDER_SSL),
                ): bool,
                vol.Optional(
                    "sensors", default=entry.data.get("sensors", "saj_sec")
                ): vol.In(SENSOR_CHOICES),
                vol.Optional(
                    CONF_PLANT_ID, default=entry.data.get(CONF_PLANT_ID, 0)
                ): cv.positive_int,
            }
        )

        return self.async_show_form(step_id="reauth", data_schema=schema, errors=errors)

    async def async_step_import(self, import_data):
        """Import configuration from YAML."""
        return self.async_create_entry(
            title=import_data[CONF_USERNAME],
            data=import_data,
        )
