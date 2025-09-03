"""Config flow for eSolar Greenheiss integration."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import section
import homeassistant.helpers.config_validation as cv

from .api import (
    AUTHENTICATION_FAILED,
    UNKNOWN_AUTH_ERROR,
    ApiAuthError,
    ApiError,
    EsolarApiClient,
    ESolarConfiguration,
    EsolarProvider,
)
from .const import (
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_PROVIDER_DOMAIN,
    CONF_PROVIDER_PATH,
    CONF_PROVIDER_SSL,
    CONF_USE_SSL,
    CONF_USERNAME,
    DOMAIN,
)

DEFAULT_PROVIDER_DOMAIN = "inversores-style.greenheiss.com"
DEFAULT_PROVIDER_PATH = "cloud"
DEFAULT_PROVIDER_SSL = True
SENSOR_CHOICES = ["h1", "saj_sec"]

_LOGGER = logging.getLogger(__name__)


class EsolarGreenheissFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for eSolar Greenheiss."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step from the user."""
        existing_entries = self._async_current_entries()

        if existing_entries:
            # Abort if any entry exists
            return self.async_abort(reason="already_configured")

        errors = {}

        if user_input is not None:
            config = self._flatten_section(user_input)
            try:
                provider = EsolarProvider(
                    config[CONF_PROVIDER_DOMAIN],
                    config[CONF_PROVIDER_PATH],
                    "https",
                    config[CONF_PROVIDER_SSL],
                )
                meterData = ESolarConfiguration(
                    config[CONF_USERNAME],
                    config[CONF_PASSWORD],
                    [],
                    0,
                    provider,
                )
                api = EsolarApiClient(self.hass, meterData)
                await api.verifyLogin()
            except ApiAuthError as err:
                _LOGGER.error("Authentication error")
                errors["base"] = str(err)
            except ApiError as err:
                _LOGGER.error("API error")
                errors["base"] = str(err)
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = api.UNKNOWN_AUTH_ERROR

            if len(errors) == 0:
                # all good
                uuid = self._getId(user_input)
                # TODO:the id is username@provider_domain.
                # this might cause issues if we allow to reconfigure the username or
                # allow multiples configurations or plants
                # maybe using the planyid would be better?
                await self.async_set_unique_id(uuid)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=self._getId(user_input),
                    data=config,
                )

        # Define the form schema
        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(
                    CONF_PROVIDER_DOMAIN, default=DEFAULT_PROVIDER_DOMAIN
                ): str,
                vol.Optional("sensors", default=SENSOR_CHOICES[1]): vol.In(
                    SENSOR_CHOICES
                ),
                vol.Required("advanced"): section(
                    vol.Schema(
                        {
                            vol.Optional(
                                CONF_PROVIDER_PATH, default=DEFAULT_PROVIDER_PATH
                            ): str,
                            vol.Optional(CONF_PLANT_ID, default=0): cv.positive_int,
                            vol.Required(CONF_USE_SSL, default=True): bool,
                            vol.Required(CONF_PROVIDER_SSL, default=True): bool,
                        }
                    ),
                    # Whether or not the section is initially collapsed (default = False)
                    {"collapsed": True},
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, user_input=None):
        """Handle re-authentication of an existing config entry."""
        _LOGGER.debug("Initiating reauth flow")
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
                config = ESolarConfiguration(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    [],
                    0,
                    provider,
                )
                api = EsolarApiClient(self.hass, config)
                await api.verifyLogin()
            except ApiAuthError as err:
                _LOGGER.error("Authentication error")
                errors["base"] = str(err)
            except ApiError as err:
                _LOGGER.error("API error %s", repr(err.__cause__))
                errors["base"] = str(err)
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = api.UNKNOWN_AUTH_ERROR

            if not errors:
                # Update the existing config entry
                new_data = {**entry.data, **user_input}
                self.hass.config_entries.async_update_entry(entry, data=new_data)
                return self.async_abort(reason="reauth_successful")

        # only password. changing username would likely break energy dashboard
        schema = vol.Schema(
            {
                vol.Required(CONF_PASSWORD, default=entry.data.get(CONF_PASSWORD)): str,
            }
        )

        placeholders = {
            "username": self.config_entry.data[CONF_USERNAME],
            "provider_domain": self.config_entry.data.get(CONF_PROVIDER_DOMAIN),
        }

        return self.async_show_form(
            step_id="reauth",
            data_schema=schema,
            description_placeholders=placeholders,
            errors=errors,
        )

    def _getId(self, dictionary) -> str:
        """Generate a unique ID for the config entry."""
        return dictionary[CONF_USERNAME] + "@" + dictionary[CONF_PROVIDER_DOMAIN]

    def _flatten_section(self, user_input: dict) -> dict:
        """Flatten sectioned config flow data into a single dict."""
        flattened = {}
        for key, value in user_input.items():
            if isinstance(value, dict):
                flattened.update(value)
            else:
                flattened[key] = value
        return flattened
