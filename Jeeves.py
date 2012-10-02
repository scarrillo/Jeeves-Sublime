'''
# Author: shawn.carrillo+sublime@gmail.com
# Source: https://github.com/scarrillo/Jeeves-Sublime
# Version 1.0
# Date: 2012.10.01
''' 
import sublime, sublime_plugin,os

class Jeeves(sublime_plugin.EventListener):
	def __init__(self):
		sublime_plugin.EventListener.__init__(self)
		self.loadSettings()

	def loadSettings(self):
		#print "Jeeves: load settings"
		self.settings = sublime.load_settings("jeeves.sublime-settings")
		self.enabled = self.settings.get("enabled")

		# Neat, but called whenever the file is saved, not just the key specified
		self.settings.clear_on_change("enabled") # Ensure we've cleared all post listeners
		self.settings.add_on_change("enabled", self.loadSettings)

		# Lazy load other build settings
		if self.enabled:
			print "Jeeves: enabled"
			self.build = self.settings.get("build")

	def on_post_save(self, view):
		if not self.enabled:
			print "Jeeves: disabled"
			return

		build = self.getBuildSystem(view)
		if build is None: return

		# Check to see if we should be monitoring this folder
		folder = self.getValidFolder(view)
		if folder is None:
			#print "Jeeves: Not monitored"
			return

		type = build.get("type")
		cmd = build.get(type)
		cmd["working_dir"] = folder
		view.window().run_command(type, cmd)

	def getBuildSystem(self, view):
		fileName = view.file_name()
		fileExt = fileName[fileName.rfind('.')+1:]

		build = self.build.get(fileExt)
		if build is None:
			#print "Jeeves: no build for: "+fileExt
			return None
		elif not build.get("enabled"):
			#print "Jeeves: build disabled for: "+fileExt
			return None
		else:
			print "Jeeves: build: "+fileExt

		return build

	# Compare the open project folders of the current Sublime Window to the folders specified in the jeeves config
	# We assume that a valid file type open in this window's project list, even if not located within a valid folder, is ok trigger a build
	# Need to research a cleaner wait to check the current file's project folder. Aside from string indexes.
	def getValidFolder(self, view):
		# Get all open project folders 
		folders = view.window().folders()
		# Handles a sublime window that contains just files.
		if len(folders) == 0:
			return None

		# First folder in Open Projects
		folder = folders[0]

		# Compare against folders specified in settings
		validFolders = self.settings.get("folders")
		for f in validFolders:
			if folder.endswith(f):
				return folder

		return None