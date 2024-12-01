"""Constants for the Battery Monitor integration."""
DOMAIN = "battery_monitor"

CONF_BATTERY_THRESHOLD = "battery_threshold"
CONF_NOTIFICATION_INTERVAL = "notification_interval"
CONF_FILTER_REGEX = "filter_regex"
CONF_NOTIFICATION_SERVICE = "notification_service"
CONF_NOTIFICATION_TITLE = "notification_title"
CONF_NOTIFICATION_MESSAGE = "notification_message"

DEFAULT_THRESHOLD = 20
DEFAULT_INTERVAL = 24  # hours
DEFAULT_TITLE = "Low Battery Alert"
DEFAULT_MESSAGE = """The following devices have low battery levels:
{% for device in devices %}
- {{ device.name }}: {{ device.battery_level }}%
{% endfor %}"""

ATTR_LAST_NOTIFICATION = "last_notification"
ATTR_BATTERY_LEVEL = "battery_level"

