"""Battery Monitor integration for Home Assistant."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .service import async_setup_service

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Battery Monitor from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    await async_setup_service(hass)
    
    return True

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Battery Monitor component."""
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True

