#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7
# -*- coding: utf-8 -*-
# generated by wxGlade HG on Thu Feb 24 15:04:33 2011

import wx
from MapCreatorMapCreator import *
#import locale
import sys
import os
import time
import Log

class MapCreator(wx.App):
	def __init__(self):
		wx.App.__init__(self, False)
		self.SetAppName("Map Creator 3.0")
		self.SetVendorName("LU")
	
	def OnInit(self):
		creatorFrame = MapCreatorMapCreator(None)
		self.SetTopWindow(creatorFrame)
		creatorFrame.Show()
		return 1

if __name__ == "__main__":
	Log.InitLogger()
	#locale.setlocale(locale.LC_ALL, '')

	mapCreator = MapCreator()
	mapCreator.MainLoop()
	