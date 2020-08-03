# coding=utf-8
from __future__ import absolute_import

from enum import Enum

import flask
from octoprint.events import Events
from octoprint.plugin import SettingsPlugin, AssetPlugin, EventHandlerPlugin, TemplatePlugin, SimpleApiPlugin, \
	ReloadNeedingPlugin


# TODO display file and user of print job in preflight checklist
# TODO persist checklist checkmarks through client refresh
# TODO actually set up the ALLOW_PREFLIGHT_BYPASS permission
# TODO actually implement timeout
class PreflightPlugin(SettingsPlugin,
					  AssetPlugin,
					  TemplatePlugin,
					  EventHandlerPlugin,
					  SimpleApiPlugin,
					  ReloadNeedingPlugin):
	class State(Enum):
		WAITING = "waiting"
		STARTED = "started"
		COMPLETE = "complete"

	def __init__(self):
		SettingsPlugin.__init__(self)
		AssetPlugin.__init__(self)
		TemplatePlugin.__init__(self)
		EventHandlerPlugin.__init__(self)
		self._preflight_state = self.State.WAITING

	@property
	def preflight_state(self) -> State:
		return self._preflight_state

	def _enter_state_waiting(self):
		self._preflight_state = self.State.WAITING
		self._logger.info("Preflight awaiting next print job")

	def _enter_state_started(self):
		self._preflight_state = self.State.STARTED
		self._logger.info("Preflight started, holding print job")

	def _enter_state_complete(self):
		self._preflight_state = self.State.COMPLETE
		self._logger.info("Preflight complete, releasing print job")

	# ~~ Hooks

	# noinspection PyMethodMayBeStatic
	def register_custom_events(self):
		return ["started", "completed"]

	# ~~ EventHandlerPlugin mixin

	def on_event(self, event, payload):
		if Events.PLUGIN_PREFLIGHT_STARTED == event:
			self._enter_state_started()
			self._printer.pause_print(self._identifier)
		elif Events.PLUGIN_PREFLIGHT_COMPLETED == event and self.preflight_state == self.State.STARTED:
			self._enter_state_complete()
			self._printer.resume_print(self._identifier)
		elif event in [Events.PRINT_CANCELLING, Events.PRINT_DONE, Events.PRINT_FAILED]:
			self._enter_state_waiting()

	# ~~ SimpleApiPlugin mixin

	def get_api_commands(self):
		return dict(
			start=[],
			complete=[]
		)

	def on_api_get(self, request):
		return flask.jsonify(state=self.preflight_state.value)

	def on_api_command(self, command, data):
		if "start" == command:
			self._event_bus.fire(Events.PLUGIN_PREFLIGHT_STARTED)
		elif "complete" == command:
			self._event_bus.fire(Events.PLUGIN_PREFLIGHT_COMPLETED)

	# ~~ SettingsPlugin mixin

	def get_settings_version(self):
		return 1

	def get_settings_defaults(self):
		return dict(
			title="Preflight",
			checklist=[
				dict(
					item="Print bed is empty",
					directions="Examine the print bed to make sure that prior prints have been removed and the bed is clean",
				),
				dict(
					item="Filament is loaded",
					directions="Is there sufficient filament loaded to complete the print?",
				)
			],
			timeout=300,  # seconds
			unchecked="&#9744;",
			checked="&#128505;",
			allow_bypass=False
		)

	# ~~ AssetPlugin mixin

	def get_assets(self):
		return dict(
			js=["js/preflight.js"],
			css=["css/preflight.css"]
		)

	# ~~ TemplatePlugin mixin

	def get_template_configs(self):
		return [
			dict(type="generic"),
			dict(type="settings", custom_bindings=False)
		]

	# ~~ Softwareupdate hook

	def get_update_information(self):
		return dict(
			preflight=dict(
				displayName="Preflight Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="battis",
				repo="OctoPrint-Preflight",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/battis/OctoPrint-Preflight/archive/{target_version}.zip"
			)
		)
