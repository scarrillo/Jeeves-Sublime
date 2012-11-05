'''
# Author: shawn.carrillo+sublime@gmail.com
# Source: https://github.com/scarrillo/Jeeves-Sublime
# Version 1.0
# Date: 2012.10.01
''' 
import sublime, sublime_plugin,os

class Jeeves(sublime_plugin.EventListener):
	#ON_KEY, ON_SAVE = range(2)
	ON_KEY = "enabled-key"
	ON_SAVE = "enabled-save"

	def __init__(self):
		sublime_plugin.EventListener.__init__(self)
		self.loadSettings()

	def loadSettings(self):
		#print "Jeeves: load settings"
		self.settings = sublime.load_settings("Jeeves.sublime-settings")
		self.enabled = self.settings.get("enabled")

		# Neat, but called whenever the file is saved, not just the key specified
		self.settings.clear_on_change("enabled") # Ensure we've cleared all post listeners
		self.settings.add_on_change("enabled", self.loadSettings)

		# Lazy load other build settings
		if self.enabled:
			print "Jeeves: enabled"
			self.build = self.settings.get("build")

	def on_query_context(self, view, key, operator, operand, match_all):
		#print "enum: "+str(Jeeves.ON_KEY)+" | "+str(Jeeves.ON_SAVE)
		if key == "jeeves_exec":
			self.execBuild(view, Jeeves.ON_KEY)
			return True

		return None

	def on_post_save(self, view):
		if not self.enabled:
			#print "Jeeves: disabled"
			return

		self.execBuild(view, Jeeves.ON_SAVE)

	def execBuild(self, view, execType):
		build = self.getBuildSystem(view, execType)
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

	def getBuildSystem(self, view, execType):
		fileName = view.file_name()
		if fileName is None:
			#print "Jeeves: invalid file"
			return

		fileExt = fileName[fileName.rfind('.')+1:]

		build = self.build.get(fileExt)
		if build is None:
			#print "Jeeves: no build for: "+fileExt
			return None
		#elif execType == Jeeves.ON_KEY and build.get("enabled-key"):
		elif build.get(execType):
			print "Jeeves: build ["+ execType +"]: "+ fileExt
			return build
		else:
			print "Jeeves: build disabled for: "+fileExt

		return None


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