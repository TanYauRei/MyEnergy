"""Adds config flow for component."""
import logging
from collections import OrderedDict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import selector
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_RESOURCES,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME
)

from . import DOMAIN, NAME
from .utils import *

_LOGGER = logging.getLogger(__name__)


def create_schema(entry, option=False):
    """Create a default schema based on if a option or if settings
    is already filled out.
    """
    if option:
        # We use .get here incase some of the texts gets changed.
        default_postalcode = entry.data.get("postalcode", "")
        default_day_electricity_consumption = entry.data.get("day_electricity_consumption", "")
        default_night_electricity_consumption = entry.data.get("night_electricity_consumption", "")
        default_excl_night_electricity_consumption = entry.data.get("excl_night_electricity_consumption", "")
        default_gas_consumption = entry.data.get("gas_consumption", "")
        default_directdebit_invoice = entry.data.get("directdebit_invoice", "")
        default_email_invoice = entry.data.get("email_invoice", "")
        default_online_support = entry.data.get("online_support", "")
    else:
        default_postalcode = ""
        default_day_electricity_consumption = ""
        default_night_electricity_consumption = ""
        default_excl_night_electricity_consumption = ""
        default_gas_consumption = ""
        default_directdebit_invoice = True
        default_email_invoice = True
        default_online_support = True

    data_schema = OrderedDict()
    data_schema[
        vol.Required("postalcode", description="postalcode")
    ] = str
    data_schema[
        vol.Required("day_electricity_consumption", description="day_electricity_consumption")
    ] = str
    data_schema[
        vol.Required("night_electricity_consumption", description="night_electricity_consumption")
    ] = str
    data_schema[
        vol.Required("excl_night_electricity_consumption", description="excl_night_electricity_consumption")
    ] = str
    data_schema[
        vol.Required("gas_consumption", description="gas_consumption")
    ] = str
    data_schema[
        vol.Required("directdebit_invoice", description="directdebit_invoice")
    ] = bool
    data_schema[
        vol.Required("email_invoice", description="email_invoice")
    ] = bool
    data_schema[
        vol.Required("online_support", description="online_support")
    ] = bool

    return data_schema


class ComponentFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for component."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}


    async def async_step_user(self, user_input=None):  # pylint: disable=dangerous-default-value
        """Handle a flow initialized by the user."""

        if user_input is not None:
            return self.async_create_entry(title=NAME, data=user_input)

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""
        data_schema = create_schema(user_input)
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_import(self, user_input):  # pylint: disable=unused-argument
        """Import a config entry.
        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        return self.async_create_entry(title="configuration.yaml", data={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):  # TODO
        """Get the options flow for this handler."""
        return ComponentOptionsHandler(config_entry)




class ComponentOptionsHandler(config_entries.ConfigFlow):
    """Now this class isnt like any normal option handlers.. as ha devs option seems think options is
    #  supposed to be EXTRA options, i disagree, a user should be able to edit anything.."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self._errors = {}

    async def async_step_init(self, user_input=None):
        return self.async_show_form(
            step_id="edit",
            data_schema=vol.Schema(create_schema(self.config_entry, option=True)),
            errors=self._errors,
        )

    async def async_step_edit(self, user_input):
        _LOGGER.debug(f"{NAME} async_step_edit user_input: {user_input}")
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input
            )
            return self.async_create_entry(title="", data={})