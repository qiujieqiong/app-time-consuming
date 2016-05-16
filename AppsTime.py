#!/usr/bin/env python
#encoding:utf-8

import os
from time import sleep
from datetime import datetime
import pyautogui
from Xlib import X,display
import subprocess
import sys
import wnck
import gtk
import json




AppNames = ("CrossOver","fcitx-configtool","google-chrome","deepin-qq","chmsee","gdebi-gtk","gparted","wps-office-et","wps-office-wpp",\
			"wps-office-wps","eog","evince","archive manager","calculator","deepin-boot-maker","deepin-movie","deepin-music-player","deepin-appstore",\
			"deepin-terminal","deepin-feedback","driver-manager","nautilus","font-viewer","system-config-printer","remote-viewer","simple-scan",\
			"system-monitor","youdao-dict")

class Log:
	def info(self,message):
		f = open("log.txt",'a')
		f.write("[%s]: %s \n" % (datetime.now(),message))
		print(message)
		f.close()

log = Log()



class Window:
	def __init__(self, display):
		self.d = display
		self.root = self.d.screen().root
		self.root.change_attributes(event_mask = X.SubstructureNotifyMask)

	def loop(self):
		window_changed = False
		while True:
			event = self.d.next_event()
			if event.type == X.MapNotify:
				window_changed = True
				break

		return window_changed


def get_active_window_name():
	winName = subprocess.check_output(["xdotool getactivewindow getwindowname"],shell=True).decode().split("\n")
	winName = [ n for n in winName if len(n.strip()) > 0]
	winName = ''.join(winName)
	return winName

def get_window_infos():
	xid_name = []
	screen = wnck.screen_get_default()
	while gtk.events_pending():
		gtk.main_iteration()

	for window in screen.get_windows():
		xid = window.get_xid()
		name = window.get_name()
		x_n = "%d %s" % (xid,name)
		xid_name.append(x_n)
	return xid_name

class App:

	def __init__(self):
		self.apps = []
		self.password = "a"
		screen = wnck.screen_get_default()
		while gtk.events_pending():
			gtk.main_iteration()
		for app in screen.get_windows():
			xid = app.get_xid()
			name = app.get_name()
			log.info("init window %s" % name)
			if name in ("深度终端", "Deepin Terminal"):
				name = "running script" 
			AppAction(xid,name,self)

	def input_passwd(self):
		sleep(2)
		pyautogui.typewrite(self.password)
		sleep(2)
		pyautogui.press('enter')
		

	def get_new_app(self):

		new_apps = get_window_infos()
		new_app = list(set(new_apps).difference(set(old_apps)))
		new_app = new_app[0].split(" ")
		new_app_xid = new_app[0]
		new_app_name = new_app[1]
		newApp = AppAction(new_app_xid,name,self)

		return newApp


	def openApp(self,name):
		sleep(1)
		old_apps = get_window_infos()
		print("old_apps:%s" % old_apps)
		#打开launcher，输入appName
		pyautogui.press('winleft')

		sleep(1)
	
		if get_active_window_name() == "dde-launcher":
			pyautogui.typewrite(name,interval=0.1)
		else:
			log.info("launcher does not opened!")
			sys.exit(1)
		sleep(1)
		pyautogui.press('enter')

		if name in ("driver-manager", "gparted","deepin-boot-maker"):
			self.input_passwd()
			start = datetime.now()
			if Window(display.Display()).loop():
				end = datetime.now()
				sleep(2)
				new_apps = get_window_infos()
				if (len(new_apps) > len(old_apps)):
					new_app = list(set(new_apps).difference(set(old_apps)))					
					new_app = new_app[0].split(" ")
					new_app_xid = new_app[0]
					new_app_name = new_app[1]
					newApp = AppAction(new_app_xid,name,self)
			else:
				log.info("app does not opened!")
				sys.exit(1)
		else:
			start = datetime.now()
			if Window(display.Display()).loop():
				end = datetime.now()
				sleep(2)
				new_apps = get_window_infos()
				if (len(new_apps) > len(old_apps)):
					new_apps = get_window_infos()
					new_app = list(set(new_apps).difference(set(old_apps)))
					new_app = new_app[0].split(" ")
					new_app_xid = new_app[0]
					new_app_name = new_app[1]
					newApp = AppAction(new_app_xid,name,self)
			else:
				log.info("app does not opened!")
				sys.exit(1)
		end = datetime.now()	
		openedTime = (end-start).seconds+(end-start).microseconds/1000000.0

		log.info("openWindow %s in %f seconds"% (name,openedTime))
				
		return newApp

class AppAction:
	def __init__(self,xid,name,app):
		self.xid = xid
		self.name = name
		self.app = app
		app.apps.append(self)

	def closeApp(self):
		if self.name in ("dde-desktop","Dock","running script"):
			return
		screen = wnck.screen_get_default()
		while gtk.events_pending():
			gtk.main_iteration()

		wrapped_window = gtk.gdk.window_foreign_new(int(self.xid))
		wrapped_window.destroy()


if __name__ == '__main__':
	app = App()
	for app_name in  AppNames:
		app.openApp(app_name).closeApp()


