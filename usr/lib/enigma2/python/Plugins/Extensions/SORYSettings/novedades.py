from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from SkinLoader import loadPluginSkin
import re, os, urllib2, sys

URL ='http://salvametv.es/servidor/servidor/novedades.txt'

def novedadessorys(url):
    text = ""
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        link = response.read().decode("windows-1252")
        response.close()
        text = link.encode("utf-8")

    except:
        print"ERROR novedades listas %s" %(url)

    return text

def listainstalada():
    lista = ""
    lista = os.popen("opkg list-installed | grep settings").read()
    
    return lista


class novedades_sorys(Screen):

    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.skinName = "novedades_sorys"
        self.setup_title = _("Novedades Lista Canales")
        self.setTitle(self.setup_title)
        
        self["novedades"] = ScrollLabel()
	self["homenovedades"] = StaticText(_("Sorys Settings- Panel Novedades"))
	self["versionlista"] = StaticText(_("%s") % listainstalada())
	self["textolista"] = StaticText(_("Lista instalada en receptor:"))


        self["Actions"] = ActionMap(['OkCancelActions', 'ShortcutActions',"ColorActions","DirectionActions"],
            {
            "cancel" : self.cerrar,
            "ok" : self.cerrar,
            "up": self["novedades"].pageUp,
            "down": self["novedades"].pageDown,
            "left": self["novedades"].pageUp,
            "right": self["novedades"].pageDown,
            })
        self['novedades'].setText(novedadessorys(URL))

    def cerrar(self):
        self.close()

