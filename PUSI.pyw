#  PUSI.py 
#  Python User Servicing Interface
#  Controller script to PENIS and BALLS 
#  AFK away and listen for a ding.  
#
#  Written in python for you Alex.... 
#
# Copyright (c) 2015, QQHeresATissue
#
# All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################

from time import gmtime
import time
from threading import *
import sys
import os
from datetime import datetime, timedelta, date
import re
import platform
import json

# Do initial checks, code taken from Pyfa... cause that shit rocks
if sys.version_info < (2,6) or sys.version_info > (3,0):
	print("PUSI requires python 2.7\nExiting.")
	time.sleep(10)
	sys.exit(1)

	try:
		import wxversion
	except ImportError:
		print("Cannot find wxPython\nYou can download wxPython (2.8) from http://www.wxpython.org/")
		time.sleep(10)
		sys.exit(1)
	try:
		wxversion.select('2.8')
	except wxversion.VersionError:
		try:
			wxversion.ensureMinimal('2.8')
		except wxversion.VersionError:
			print("Installed wxPython version doesn't meet requirements.\nYou can download wxPython (2.8) from http://www.wxpython.org/")
			time.sleep(10)
			sys.exit(1)
		else:
			print("wxPython 2.8 not found; attempting to use newer version, expect errors")

import wx

# suppress nerd speak
sys.tracebacklimit = 0

# set a version
ver = "0.1b"

ID_PENIS_START = wx.NewId()
ID_BALLS_START = wx.NewId()

# Are we on windows or linux?
which_os = platform.system()

# Setup a class for text redirection
class RedirectText(object):
	def __init__(self,aWxTextCtrl):
		self.out=aWxTextCtrl
 	
 	# Write string to wx window
	def write(self,string):
		wx.CallAfter(self.out.AppendText, string)

# Main form for graphical PUSI
class pusi(wx.Frame):

	def __init__(self,parent,id):

		# Create the main window with the title PUSI <version number>
		wx.Frame.__init__(self,parent,id,'PUSI %s' % ver, size=(800,320), style = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
		
		# Create a panel in the windows
		self.panel = wx.Panel(self)

		# Setup logging early so we see it in the panel
		logbox = wx.TextCtrl(self.panel, wx.ID_ANY, size = (780, 250), pos = (10,40), style = wx.TE_MULTILINE| wx.TE_READONLY | wx.HSCROLL)

		# Redirect all printed messages to the panel
		redir=RedirectText(logbox)
		sys.stdout=redir
		sys.stderr=redir
		
		# Create a start and stop button
		self.penis_start = wx.Button(self.panel, ID_PENIS_START, label="Start PENIS", pos=(10,10), size=(90,25))
		self.balls_start = wx.Button(self.panel, ID_BALLS_START, label="Start BALLS", pos=(410, 10), size=(90,25))

		# Define regions we have systems for in a list
		region_list = [ 'DEK', 'BRN', 'FTN', 'PBF' ]
		# Create text "Region" before the dropdown box
		wx.StaticText(self.panel, -1, 'Region', (105,15))

		# Create the dropdown box and use DEK as a default selection
		pusi.region_select = wx.ComboBox(self.panel, -1, pos=(150,10), size=(75,25), choices = region_list, style=wx.CB_DROPDOWN)
		pusi.region_select.SetSelection(0)

		#Create the system input box
		wx.StaticText(self.panel, -1, 'System', (230, 15))
		pusi.system_select = wx.TextCtrl(self.panel, -1, '', (280,10), (120,-1))

		# Bind button clicks to events (start|stop)
		self.Bind(wx.EVT_BUTTON, self.penis_run, id=ID_PENIS_START)
		self.Bind(wx.EVT_BUTTON, self.balls_run, id=ID_BALLS_START)

		# Set a watch variable to check later.  If we want the process to stop, self.watch becomes 1
		self.penis_watcher = None
		self.balls_watcher = None

		# Shameless self adversiting
		print "Python User Servicing Interface v%s by QQHeresATissue" % ver

	# Setup a functions to start the watcher thread
	def penis_run(self, event):
		if not self.penis_watcher:
			self.penis_watcher = StartPENIS(self)

	def balls_run(self, event):
		if not self.balls_watcher:
			self.balls_watcher = StartBALLS(self)

# Define watcher thread
class StartPENIS(Thread):

	def __init__(self, threadID):
		Thread.__init__(self)
		# Kill the thread when the main process is exited
		self.daemon = True
		self.threadID = threadID
		self._want_abort = 0
		self.start()

	# setup our log file watcher, only open it once and update when a new line is written
	def hostile_watch(self, logfile, words):

		fp = open(logfile, 'r')
		while True:
			
			# remove null padding (lol ccp)
			new = re.sub(r'[^\x20-\x7e]', '', fp.readline())

			if new:
				for word in words:
					if word in new:
						yield (word, new)
			else:
				time.sleep(0.01)

	# Start the main thread for alerting
	def run(self):

		# get our current working directory
		penis_dir = os.path.dirname(__file__)

		print "Starting the Potentially Erroneous Nullsec Intelligence System"

		if which_os == "Linux":
			# Wine default path
			hostile_logdir = os.path.join( "/home", os.getenv('USER'), "EVE", "logs", "Chatlogs" )

		elif which_os == "Windows":
			# Win 7 default log path
			hostile_logdir = os.path.join( "C:/", "Users", os.getenv('USERNAME'), "Documents", "EVE", "logs", "Chatlogs" )
			# extra import to play the beep
			import winsound

		elif which_os == "Darwin":
			# os.getenv doesn't seem to work here...
			import getpass
			# OSX default log path
			hostile_logdir = os.path.join( "/Users", getpass.getuser(), "Library", "Application Support", "EVE Online", "p_drive", "User", "My Documents", "EVE", "logs", "Chatlogs" )

		else:

			print "What fucking OS are you running?"

		# get region based on our dropdown box selection
		region = pusi.region_select.GetValue()
		# get the system based on our system input
		system = pusi.system_select.GetValue()

		# select identified logs and sort by date
		hostile_tmp = sorted([ f for f in os.listdir(hostile_logdir) if f.startswith('%s.CFC' % region)])
		# testing line so we shit up Corp chat not intel chans
		# hostile_tmp = sorted([ f for f in os.listdir(hostile_logdir) if f.startswith('Corp')])

		# grab the most recent file for each log
		logfile = os.path.join( hostile_logdir, hostile_tmp[-1] )

		# triggers to look for in the intel channels.  Read from json files for a specified system
		# big thanks to Orestus for getting the branch systems together and suggesting the change!!
		json_data = open(os.path.join( penis_dir, "systems", "%s.json" % system))

		data = json.load(json_data)

		hostile_words = data

		json_data.close()

		# ignore status requests and clr reports
		status_words = [ "status", \
						"Status", \
						"clear", \
						"Clear", \
						"stat", \
						"Stat", \
						"clr", \
						"Clr",
						"EVE System" ]

		# Print some initial info lines
		print "parsing from - Intel:  %s\n" % (hostile_tmp[-1])

		# if the word matches a trigger, move on
		for hostile_hit_word, hostile_hit_sentence in self.hostile_watch(logfile, hostile_words):
		#print "%r | %r | %r | %r" % (hostile_hit_word, hostile_fn, hostile_words, hostile_hit_sentence)
			
			# if someone is just asking for status, ignore the hit
			if not any(status_word in hostile_hit_sentence for status_word in status_words):

				# get the current time for each event
				hit_time = time.strftime('%H:%M:%S')
				# get current date/time in UTC
				utc = time.strftime('[ %Y.%m.%d %H:%M', gmtime())[:17]
	
				# print the alert
				if which_os == "Windows":
					print "PENIS INTEL ALERT!! %r - %r\r\n" % (hit_time, hostile_hit_word)
					print "%r\r\n" % (hostile_hit_sentence)
					wx.Yield()
				else:
					print "PENIS INTEL ALERT!! %r" % (hit_time)
					print "%r\n" % (hostile_hit_sentence)
					wx.Yield()
		
				# play a tone to get attention, only if its recent!
				if utc in hostile_hit_sentence:
				
					if which_os == "Linux":
						os.system("aplay -q ~/Downloads/beep.wav")
		
					elif which_os == "Windows":
						winsound.Beep(500, 500), winsound.Beep(500, 500), winsound.Beep(500, 500)
		
					elif which_os == "Darwin":
						print('\a')
						print('\a')
						print('\a')

# Define BALLS watcher thread
class StartBALLS(Thread):

	def __init__(self, threadID):
		Thread.__init__(self)
		# Kill the thread when the main process is exited
		self.daemon = True
		self.threadID = threadID
		self._want_abort = 0
		self.start()

	# setup our log file watcher, only open it once and update when a new line is written
	def balls_watch(self, fn, words):
		done_count = 0
	
		fp = open(fn, 'r')
		while True:
			new = fp.readline()
		
			if new:
				done_count = 0
				for word in words:
					if word in new:
						yield (word, new)
			else:
				done_count = done_count + 1
				if done_count > 129:
					print "BALLS Notification"
					print "%r - Sites done (or something is wrong)\n" % (time.strftime('%H:%M:%S'))
					
					if which_os == "Linux":
						os.system("aplay -q ~/Downloads/sites_done.wav")
					elif which_os == "Windows":
						winsound.Beep(750, 500), winsound.Beep(750, 500)
					elif which_os == "Darwin":
						print('\a')
						print('\a')
						print('\a')
					
					done_count = 0
		
				time.sleep(0.5)

	def run(self):
		count = 0

		if which_os == "Linux":
			# Wine default path
			logdir = os.path.join( "/home", os.getenv('USER'), "EVE", "logs", "Gamelogs" )
	
		elif which_os == "Windows":
			# Win 7 default log path
			logdir = os.path.join( "C:/", "Users", os.getenv('USERNAME'), "Documents", "EVE", "logs", "Gamelogs" )
			# extra import to play the beep
			import winsound
	
		elif which_os == "Darwin":
			# os.getenv doesn't seem to work here...
			import getpass
			# OSX default log path
			hostile_logdir = os.path.join( "/Users", getpass.getuser(), "Library", "Application Support", "EVE Online", "p_drive", "User", "My Documents", "EVE", "logs", "Chatlogs" )
	
		else:
	
			print "What fucking OS are you running?"
	
		# sort by date
		tmp = sorted([ f for f in os.listdir(logdir) if f.startswith('201')])
	
		# grab the most recent file
		fn = os.path.join( logdir, tmp[-1] )
	
		print "\nStarting the Background Alert for Lucrative Loot Script"
	
		print "parsing from %s\n" % tmp[-1]
	
		# triggers to look for in the log file
		words = [ "Dread Guristas", \
				"Dark Blood", \
				"True Sansha", \
				"Shadow Serpentis", \
				"Sentient", \
				"Domination",\
				"Estamel Tharchon", \
				"Vepas Minimala", \
				"Thon Eney", \
				"Kaikka Peunato", \
				"Gotan Kreiss", \
				"Hakim Stormare",\
				"Mizuro Cybon", \
				"Tobias Kruzhor", \
				"Ahremen Arkah", \
				"Draclira Merlonne", \
				"Raysere Giant",\
				"Tairei Namazoth", \
				"Brokara Ryver", \
				"Chelm Soran", \
				"Selynne Mardakar", \
				"Vizan Ankonin", \
				"Brynn Jerdola",\
				"Cormack Vaaja", \
				"Setele Schellan", \
				"Tuvan Orth", \
				"Warp scramble attempt" ]
	
		# Don't trigger if we are accepting or getting a contract
		false_pos = [ "following items", \
					"question" ]
	
		for hit_word, hit_sentence in self.balls_watch(fn, words):
	
			if not any(false_word in hit_sentence for false_word in false_pos):
	
				if count < 1:
					count = count + 1
					# log the combat lines involving the spawn
					print "BALLS ALERT!!"
					print "%r - %r\n" % (time.strftime('%H:%M:%S'), hit_word)
					wx.Yield()
					# debug statement
					# print "%r" % (hit_sentence)
	     
					# play a tone to get attention
					if which_os == "Linux":
						os.system("aplay -q ~/Downloads/beep.wav")
	      
					elif which_os == "Windows":
						winsound.Beep(500, 500), winsound.Beep(500, 500), winsound.Beep(500, 500)
	
					elif which_os == "Darwin":
						print('\a')
						print('\a')
						print('\a')
	
					else:
						print "What fucking system are you running?"
						break
	
				elif count == 30:
					count = 0
					continue
				else:
					count = count + 1
					continue
	
if __name__ == '__main__':
	app=wx.PySimpleApp()
	frame=pusi(parent=None,id=-1)
	frame.Show()
	app.MainLoop()