from Components.config import config
from skin import loadSkin
import os


def loadSkinReal(skinPath):
	if os.path.exists(skinPath):
		print "[SKLDR] Loading skin ", skinPath
		loadSkin(skinPath)


def loadPluginSkin(pluginPath):
	loadSkinReal(pluginPath + "/confluence/" + config.skin.primary_skin.value)
	loadSkinReal(pluginPath + "/confluence/skin.xml")


