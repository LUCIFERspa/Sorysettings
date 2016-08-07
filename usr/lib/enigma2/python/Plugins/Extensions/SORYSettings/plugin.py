# -*- coding: utf-8 -*-
# Panel Descarga Listas Sorys
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Console import Console
from Components.Sources.StaticText import StaticText
from Components.config import config
from Components.ConfigList import ConfigListScreen
from Components.Pixmap import Pixmap
from Components.Console import Console as iConsole
from Components.Harddisk import harddiskmanager
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
from xml.dom import Node
from xml.dom import minidom
from twisted.web.client import downloadPage
from twisted.web.client import getPage
import urllib
from enigma import eTimer
from Components.Button import Button
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Components.Language import language
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.config import config, getConfigListEntry, ConfigText, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile
from Components.ConfigList import ConfigListScreen
from SkinLoader import loadPluginSkin
from os import environ
import os
from os import path, system
import gettext
import time
import enigma
currversion = '1.01'

def sorysettingsversion():
	return ("Sorysettings-1.0-r1")
	
	
class sorysettings_menu(Screen):
	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = "sorysettings_menu"
		self.setTitle(_("SORYSettings"))
		self.indexpos = None
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		{
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"blue": self.infopanel,
			"yellow": self.despanel,
			
		})
		self["sorysettings_version"] = StaticText(_("Version Panel: %s") % sorysettingsversion())
		self["key_red"] = StaticText(_("Cerrar"))
		self["key_blue"] = StaticText(_("sorysInfo"))
		self["key_yellow"] = StaticText(_("sorysDescargas"))
		self["home"] = StaticText(_("sorys Settings - Menu Principal"))
		
	def exit(self):
		self.close()

	def infopanel(self):
		self.session.open(sorysinfopanel)

	def despanel(self):
		self.session.open(sorysdescargas)
		
	
	
######################################################################################
class sorysinfopanel(Screen):
	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = "sorysinfopanel"
		self.setTitle(_("SORYSettings"))
		self.iConsole = iConsole()
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		{
			"cancel": self.cancel,
			"back": self.cancel,
			"red": self.cancel,
			"blue": self.sorysippublica,
			"yellow": self.soryslibmemoria,
			"green": self.sorysresetpass,
			"ok": self.cancel,
			})
		self["homeinfo"] = StaticText(_("Sorys Settings- Panel Info"))
		self["key_red"] = StaticText(_("Cerrar"))
		self["key_blue"] = StaticText(_("IP Publica"))
		self["key_yellow"] = StaticText(_("Liberar Memoria"))
		self["key_green"] = StaticText(_("Resetear Password"))
		self["MemoryLabel"] = StaticText(_("Memoria:"))
		self["SwapLabel"] = StaticText(_("Swap:"))
		self["FlashLabel"] = StaticText(_("Flash:"))
		self["memTotal"] = StaticText()
		self["swapTotal"] = StaticText()
		self["flashTotal"] = StaticText()
		self["device"] = StaticText()
		self["Hardware"] = StaticText()
		self["Image"] = StaticText()
		self["CPULabel"] = StaticText(_("Procesador:"))
		self["CPU"] = StaticText()
		self["Kernel"] = StaticText()
		self["nim"] = StaticText()
		self["ipLabel"] = StaticText(_("Interna IP:"))
		self["ipInfo"] = StaticText()
		self["macLabel"] = StaticText(_("MAC (lan/wlan):"))
		self["macInfo"] = StaticText()
		self["EnigmaVersion"] = StaticText()
		self["HardwareLabel"] = StaticText(_("Hardware:"))
		self["ImageLabel"] = StaticText(_("Imagen:"))
		self["KernelLabel"] = StaticText(_("Kernel Version:"))
		self["EnigmaVersionLabel"] = StaticText(_("Last Upgrade:"))
		self["driver"] = StaticText()
		self["driverLabel"] = StaticText(_("Driver Version:"))
		self.memInfo()
		self.FlashMem()
		self.devices()
		self.mainInfo()
		self.cpuinfo()
		self.network_info()

    	def sorysippublica(self):
		os.popen("wget -qO /tmp/.mostrarip http://icanhazip.com/")
		f = open("/tmp/.mostrarip")
		mostrarip = f.readline()
		f.close()
		self.mbox = self.session.open(MessageBox,_("Mi IP Publica: %s") % (mostrarip), MessageBox.TYPE_INFO, timeout = 10 )

	def soryslibmemoria(self):
		os.system("sync ; echo 3 > /proc/sys/vm/drop_caches")
		os.system("free | awk '/Mem:/ {print int(100*$4/$2) ;}' >/tmp/.memory")
		f = open("/tmp/.memory")
		mused = f.readline()
		f.close()
		self.mbox = self.session.open(MessageBox,_("Porcentaje Memoria libre despues de la ejecucion: %s ") % (mused), MessageBox.TYPE_INFO, timeout = 20 )

	def sorysresetpass(self):
		os.system("passwd -d root")
		self.mbox = self.session.open(MessageBox,_("Tu Password ha sido borrada"), MessageBox.TYPE_INFO, timeout = 10 )
		
	def network_info(self):
		self.iConsole.ePopen("ifconfig -a", self.network_result)
		
	def network_result(self, result, retval, extra_args):
		if retval is 0:
			ip = ''
			mac = []
			if len(result) > 0:
				for line in result.splitlines(True):
					if 'HWaddr' in line:
						mac.append('%s' % line.split()[-1].strip('\n'))
					elif 'inet addr:' in line and 'Bcast:' in line:
						ip = line.split()[1].split(':')[-1]
				self["macInfo"].text = '/'.join(mac)
			else:
				self["macInfo"].text =  _("unknown")
		else:
			self["macInfo"].text =  _("unknown")
		if ip is not '':
			self["ipInfo"].text = ip
		else:
			self["ipInfo"].text = _("unknown")


		
	def cpuinfo(self):
		if fileExists("/proc/cpuinfo"):
			cpu_count = 0
			processor = cpu_speed = cpu_family = cpu_variant = temp = ''
			core = _("core")
			cores = _("cores")
			for line in open('/proc/cpuinfo'):
				if "system type" in line:
					processor = line.split(':')[-1].split()[0].strip().strip('\n')
				elif "cpu MHz" in line:
					cpu_speed =  line.split(':')[-1].strip().strip('\n')
					#cpu_count += 1
				elif "cpu type" in line:
					processor = line.split(':')[-1].strip().strip('\n')
				elif "model name" in line:
					processor = line.split(':')[-1].strip().strip('\n').replace('Processor ', '')
				elif "cpu family" in line:
					cpu_family = line.split(':')[-1].strip().strip('\n')
				elif "cpu variant" in line:
					cpu_variant = line.split(':')[-1].strip().strip('\n')
				elif line.startswith('processor'):
					cpu_count += 1
			if not cpu_speed:
				try:
					cpu_speed = int(open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq").read()) / 1000
				except:
					cpu_speed = '-'
			if fileExists("/proc/stb/sensors/temp0/value") and fileExists("/proc/stb/sensors/temp0/unit"):
				temp = "%s%s%s" % (open("/proc/stb/sensors/temp0/value").read().strip('\n'), unichr(176).encode("latin-1"), open("/proc/stb/sensors/temp0/unit").read().strip('\n'))
			elif fileExists("/proc/stb/fp/temp_sensor_avs"):
				temp = "%s%sC" % (open("/proc/stb/fp/temp_sensor_avs").read().strip('\n'), unichr(176).encode("latin-1"))
			if cpu_variant is '':
				#self["CPU"].text = _("%s, %s Mhz (%d %s) %s") % (processor, cpu_speed[:-1], cpu_count, cpu_count > 1 and cores or core, temp)
				self["CPU"].text = _("%s, %s Mhz (%d %s) %s") % (processor, cpu_speed, cpu_count, cpu_count > 1 and cores or core, temp)
			else:
				self["CPU"].text = "%s(%s), %s %s" % (processor, cpu_family, cpu_variant, temp)
		else:
			self["CPU"].text = _("undefined")

	def status(self):
		status = ''
		if fileExists("/usr/lib/opkg/status"):
			status = "/usr/lib/opkg/status"
		elif fileExists("/usr/lib/ipkg/status"):
			status = "/usr/lib/ipkg/status"
		elif fileExists("/var/lib/opkg/status"):
			status = "/var/lib/opkg/status"
		elif fileExists("/var/opkg/status"):
			status = "/var/opkg/status"
		return status
		
			
	def devices(self):
		list = ""
		hddlist = harddiskmanager.HDDList()
		hddinfo = ""
		if hddlist:
			for count in range(len(hddlist)):
				hdd = hddlist[count][1]
				if int(hdd.free()) > 1024:
					list += ((_("%s  %s  (%d.%03d GB free)\n") % (hdd.model(), hdd.capacity(), hdd.free()/1024 , hdd.free()%1024)))
				else:
					list += ((_("%s  %s  (%03d MB free)\n") % (hdd.model(), hdd.capacity(),hdd.free())))
		else:
			hddinfo = _("none")
		self["device"].text = list
		
	def HardWareType(self):
		if os.path.isfile("/proc/stb/info/boxtype"):
			return open("/proc/stb/info/boxtype").read().strip().upper()
		if os.path.isfile("/proc/stb/info/vumodel"):
			return "VU+" + open("/proc/stb/info/vumodel").read().strip().upper()
		if os.path.isfile("/proc/stb/info/model"):
			return open("/proc/stb/info/model").read().strip().upper()
		return _("unavailable")
		
	def getImageTypeString(self):
		try:
			if os.path.isfile("/etc/issue"):
				for line in open("/etc/issue"):
					if not line.startswith('Welcom') and '\l' in line:
						return line.capitalize().replace('\n', ' ').replace('\l', ' ').strip()
		except:
			pass
		return _("undefined")
		
	def getKernelVersionString(self):
		try:
			return open("/proc/version").read().split()[2]
		except:
			return _("unknown")
			
	def getImageVersionString(self):
		try:
			if os.path.isfile('/var/lib/opkg/status'):
				st = os.stat('/var/lib/opkg/status')
			elif os.path.isfile('/usr/lib/ipkg/status'):
				st = os.stat('/usr/lib/ipkg/status')
			elif os.path.isfile('/usr/lib/opkg/status'):
				st = os.stat('/usr/lib/opkg/status')
			elif os.path.isfile('/var/opkg/status'):
				st = os.stat('/var/opkg/status')
			tm = time.localtime(st.st_mtime)
			if tm.tm_year >= 2011:
				return time.strftime("%Y-%m-%d %H:%M:%S", tm)
		except:
			pass
		return _("unavailable")
		
	def listnims(self):
		tuner_name = {'0':'Tuner A:', '1':'Tuner B:', '2':'Tuner C:', '3':'Tuner D:', '4':'Tuner E:', '5':'Tuner F:', '6':'Tuner G:', '7':'Tuner H:', '8':'Tuner I:', '9':'Tuner J:'}
		nimlist = ''
		if fileExists("/proc/bus/nim_sockets"):
			for line in open("/proc/bus/nim_sockets"):
				if 'NIM Socket' in line:
					nimlist += tuner_name[line.split()[-1].replace(':', '')] + ' '
				elif 'Type:' in line:
					nimlist += '(%s)' % line.split()[-1].replace('\n', '').strip() + ' '
				elif 'Name:' in line:
					nimlist += '%s' % line.split(':')[1].replace('\n', '').strip() + '\n'
			return nimlist
		else:
			return _("unavailable")
			
	def mainInfo(self):
		package = 0
		self["Hardware"].text = self.HardWareType()
		self["Image"].text = self.getImageTypeString()
		self["Kernel"].text = self.getKernelVersionString()
		self["EnigmaVersion"].text = self.getImageVersionString()
		self["nim"].text = self.listnims()
		if fileExists(self.status()):
			for line in open(self.status()):
				if "-dvb-modules" in line and "Package:" in line:
					package = 1
				elif "kernel-module-player2" in line and "Package:" in line:
					package = 1
				elif "formuler-dvb-modules" in line and "Package:" in line:
					package = 1
				elif "vuplus-dvb-proxy-vusolo4k" in line and "Package:" in line:
					package = 1
				if "Version:" in line and package == 1:
					package = 0
					self["driver"].text = line.split()[-1]
					break

	def memInfo(self):
		for line in open("/proc/meminfo"):
			if "MemTotal:" in line:
				memtotal = line.split()[1]
			elif "MemFree:" in line:
				memfree = line.split()[1]
			elif "SwapTotal:" in line:
				swaptotal =  line.split()[1]
			elif "SwapFree:" in line:
				swapfree = line.split()[1]
		self["memTotal"].text = _("Total: %s Kb  Free: %s Kb") % (memtotal, memfree)
		self["swapTotal"].text = _("Total: %s Kb  Free: %s Kb") % (swaptotal, swapfree)
		
	def FlashMem(self):
		size = avail = 0
		st = os.statvfs("/")
		avail = st.f_bsize * st.f_bavail / 1024
		size = st.f_bsize * st.f_blocks / 1024
		self["flashTotal"].text = _("Total: %s Kb  Free: %s Kb") % (size , avail)
		
			
	def cancel(self):
		self.close()
####################################################################
class sorysdescargas(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
	self.skinName = "sorysettings_descargas"
	self.setTitle(_("SORYSettings"))
        self["key_red"] = StaticText(_("Cerrar"))
	self["key_blue"] = StaticText(_("Novedades"))
	self["homedescarga"] = StaticText(_("Sorys Settings - Panel Descargas"))
	self["url"] = StaticText(_("http://openspa.info"))
	self["lab1"] = StaticText(_("Seleccione en la parte izquierda para acceder instalacion paquetes"))
	self["lab2"] = StaticText(_("Mantenimiento paquetes: Lucifer, Sorys"))
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['info'].setText('Accediendo Servidor listas sorys, espere por favor')
        self.timer = eTimer()
        self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(100, 1)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close,
	 'blue': self.novedades,
         'red': self.close}, -2)

    def novedades(self):
        import novedades
        self.session.open(novedades.novedades_sorys)

    def updateable(self):
        try:
            selection = str(self.names[0])
            lwords = selection.split('_')
            lv = lwords[1]
            self.lastversion = lv
            if float(lv) == float(currversion):
                return False
            if float(lv) > float(currversion):
                return True
            return False
        except:
            return False

    def downloadxmlpage(self):
        url = 'http://salvametv.es/servidor/servidor/servidor.xml'
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print str(error)
        self['info'].setText('Servidor lista canales caido o fallo conexion internet')
        self.downloading = False

    def _gotPageLoad(self, data):
        self.xml = data
        try:
            if self.xml:
                xmlstr = minidom.parseString(self.xml)
                self.data = []
                self.names = []
                icount = 0
                list = []
                xmlparse = xmlstr
                self.xmlparse = xmlstr
                for plugins in xmlstr.getElementsByTagName('plugins'):
                    self.names.append(plugins.getAttribute('cont').encode('utf8'))

                self.list = list
                self['info'].setText('')
                self['list'].setList(self.names)
                self.downloading = True
            else:
                self.downloading = False
                self['info'].setText('Servidor listas canales caido o fallo conexion internet')
                return
        except:
            self.downloading = False
            self['info'].setText('Error datos servidor')

    def okClicked(self):
        if self.downloading == True:
            try:
                self.downloading = True
                selection = str(self['list'].getCurrent())
                self.session.open(sorysinstall, self.xmlparse, selection)
            except:
                return


class sorysinstall(Screen):

    def __init__(self, session, xmlparse, selection):
        Screen.__init__(self, session)
	self.skinName = "sorysettings_descargas2"
 	self.setTitle(_("SORYSettings"))
        self["key_red"] = StaticText(_("Cerrar"))
	self["homeinstalar"] = StaticText(_("Sorys Settings - Panel Instalar"))
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['info'].setText('')
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.selClicked,
         'cancel': self.close,
         'red': self.close}, -2)

        self.xmlparse = xmlparse
        self.selection = selection
        list = []
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    list.append(plugin.getAttribute('name').encode('utf8'))
                continue

        list.sort()
        self['countrymenu'] = MenuList(list)
    
    def selClicked(self):
        try:
            selection_country = self['countrymenu'].getCurrent()
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname)
                        continue
                    else:
                        continue

                continue

        return

    def prombt(self, com, dom):
        self.com = com
        self.dom = dom
        if self.selection == 'Skins':
            self.session.openWithCallback(self.callMyMsg, MessageBox, _('No tienes instalado skin compatible?'), MessageBox.TYPE_YESNO)
            
        else:
		if os.popen("opkg list-installed | grep settings").read() == '':
            		self.session.open(Console, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com])
		else:
			os.system("opkg remove enigma2-plugin-settings-*")
			self.session.open(Console, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com])
        self.close()

    def callMyMsg(self, result):
        if result:
            dom = self.dom
            com = self.com
            self.session.open(Console, _('downloading-installing: %s') % dom, ['ipkg install -force-overwrite %s' % com])
#################################################################

def main(session, **kwargs):
	session.open(sorysettings_menu)
	
######################################################################################
def sessionstart(reason,session=None, **kwargs):
	if reason == 0:
		pTools.gotSession(session)
######################################################################################

def Plugins(**kwargs):
	loadPluginSkin(kwargs["path"])
	list = [PluginDescriptor(name=_("sorys Settings"), description=_("Descarga lista canales Sorys"), where = [PluginDescriptor.WHERE_PLUGINMENU], icon="sorysettings.png", fnc=main)]
	
	return list
