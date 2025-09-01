from homeassistant import config_entries
import voluptuous as vol
import homeassistant.helpers.config_validation as cv


from .const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    DOMAIN,
    CONF_PROVIDER_DOMAIN,
    CONF_PROVIDER_PATH,
    CONF_PROVIDER_SSL,
    CONF_PLANT_ID,
)

# Default values from your YAML
DEFAULT_PROVIDER_DOMAIN = "inversores-style.greenheiss.com"
DEFAULT_PROVIDER_PATH = "cloud"
DEFAULT_PROVIDER_SSL = False
SENSOR_CHOICES = ["h1", "saj_sec"]


class EsolarGreenheissFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for eSolar Greenheiss."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step from the user."""
        errors = {}

        if user_input is not None:
            # Optionally validate credentials here with the API
            # For now, assume valid
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
