"""Service for Battery Monitor integration."""
import re
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.template import Template
from homeassistant.util import dt as dt_util
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    ATTR_NAME,
    DEVICE_CLASS_BATTERY,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)

from .const import (
    DOMAIN,
    CONF_BATTERY_THRESHOLD,
    CONF_NOTIFICATION_INTERVAL,
    CONF_FILTER_REGEX,
    CONF_NOTIFICATION_SERVICE,
    CONF_NOTIFICATION_TITLE,
    CONF_NOTIFICATION_MESSAGE,
    DEFAULT_THRESHOLD,
    DEFAULT_INTERVAL,
    DEFAULT_TITLE,
    DEFAULT_MESSAGE,
    ATTR_LAST_NOTIFICATION,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_service(hass: HomeAssistant) -> None:
    """Set up the battery check service."""

    _LOGGER.debug("Inicializuji sližnu.")
    async def handle_check_batteries(call: ServiceCall) -> None:
        """Handle the check_batteries service call."""
        
        _LOGGER.debug("Startuji službu")
        
        battery_threshold = call.data.get(CONF_BATTERY_THRESHOLD, DEFAULT_THRESHOLD)
        notification_interval = call.data.get(CONF_NOTIFICATION_INTERVAL, DEFAULT_INTERVAL)
        filter_regex = call.data.get(CONF_FILTER_REGEX)
        notification_service = call.data.get(CONF_NOTIFICATION_SERVICE)
        notification_title = call.data.get(CONF_NOTIFICATION_TITLE, DEFAULT_TITLE)
        notification_message = call.data.get(CONF_NOTIFICATION_MESSAGE, DEFAULT_MESSAGE)

        low_battery_devices = await get_low_battery_devices(
            hass,
            battery_threshold,
            notification_interval,
            filter_regex
        )

        if not low_battery_devices:
            return

        await send_notification(
            hass,
            low_battery_devices,
            notification_service,
            notification_title,
            notification_message
        )

    # Register service
    hass.services.async_register(
        DOMAIN,
        "check_batteries",
        handle_check_batteries,
    )

async def get_low_battery_devices(
    hass: HomeAssistant,
    battery_threshold: float,
    notification_interval: int,
    filter_regex: str | None
) -> list[dict]:
    """Get list of devices with low battery."""
    battery_entities = []
    
    for state in hass.states.async_all():
        # Skip unavailable or unknown states
        if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            continue

        # Check if entity is battery sensor
        if state.attributes.get("device_class") != DEVICE_CLASS_BATTERY:
            continue
            
        entity_id = state.entity_id
        if filter_regex and not re.search(filter_regex, entity_id):
            _LOGGER.debug("Entity %s filtered out by regex", entity_id)
            continue
            
        try:
            # Try to convert state to float
            battery_level = float(state.state)
        except (ValueError, TypeError):
            _LOGGER.warning(
                "Entity %s has invalid battery level: %s",
                entity_id,
                state.state
            )
            continue
            
        _LOGGER.debug(
            "Found battery sensor %s with level %f%%",
            entity_id,
            battery_level
        )
            
        battery_entities.append({
            "entity_id": entity_id,
            "name": state.attributes.get(ATTR_NAME, entity_id),
            "battery_level": battery_level
        })

    # Filter low battery devices
    now = dt_util.utcnow()
    low_battery_devices = []
    
    for device in battery_entities:
        if device["battery_level"] <= battery_threshold:
            entity_id = device["entity_id"]
            last_notification = hass.data[DOMAIN].get(entity_id, {}).get(ATTR_LAST_NOTIFICATION)
            
            if not last_notification or (
                now - last_notification > timedelta(hours=notification_interval)
            ):
                low_battery_devices.append(device)
                hass.data[DOMAIN][entity_id] = {
                    ATTR_LAST_NOTIFICATION: now
                }
                _LOGGER.debug(
                    "Adding device %s with battery level %f%% to notification list",
                    entity_id,
                    device["battery_level"]
                )
                
    _LOGGER.debug(
        "Found %d devices with battery level <= %f%%",
        len(low_battery_devices),
        battery_threshold
    )

    return low_battery_devices

async def send_notification(
    hass: HomeAssistant,
    devices: list[dict],
    notification_service: str,
    title_template: str,
    message_template: str
) -> None:
    """Send notification about low battery devices."""
    template_data = {"devices": devices}
    
    title = Template(title_template, hass).async_render(template_data)
    message = Template(message_template, hass).async_render(template_data)

    service_domain, service_name = notification_service.split(".", 1)
    
    _LOGGER.debug(
        "Sending notification via %s.%s with title: %s",
        service_domain,
        service_name,
        title
    )
    
    await hass.services.async_call(
        service_domain,
        service_name,
        {
            "title": title,
            "message": message
        }
    )
        
