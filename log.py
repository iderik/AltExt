#!/usr/bin/env python

import fileio

#
# Name: Logmanager
# Description: Logging
# This is a part of AltExt project.
#

# Write to different pipes. Do not use this alone, use the methods below instead.
def Write(msg, pipe, filePath="Data/altext.log"):
	if ('c' in pipe):	# Write to console
		print msg
	if ('f' in pipe):	# Write to file
		pass
	if ('g' in pipe):	# Write as serverMessage
		pass

# Write a raw (no pre-defined structure) message.
def Raw(logType, msg, pipe='c'):
	Write("[%s] %s" % (logType, msg), pipe)
