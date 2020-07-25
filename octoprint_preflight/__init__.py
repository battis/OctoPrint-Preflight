# coding=utf-8
from __future__ import absolute_import

from octoprint_preflight.plugin import PreflightPlugin

__plugin_name__ = "Preflight"
__plugin_pythoncompat__ = ">=2.7,<4"  # python 2 and 3


# noinspection PyGlobalUndefined
def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PreflightPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.events.register_custom_events": __plugin_implementation__.register_custom_events,
	}
