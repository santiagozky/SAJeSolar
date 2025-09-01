from homeassistant import config_entries
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import logging


from .const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    DOMAIN,
    CONF_PROVIDER_DOMAIN,
    CONF_PROVIDER_PATH,
    CONF_PROVIDER_SSL,
    CONF_PLANT_ID,
)

from .api import (
    EsolarApiClient,
    EsolarProvider,
    SAJeSolarMeterData,
    ApiAuthError,
    ApiError,
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

    async def async_step_import(self, import_data):
        """Import configuration from YAML."""
        return self.async_create_entry(
            title=import_data[CONF_USERNAME],
            data=import_data,
        )
