#!/usr/bin/env python

import os, simplejson, log

#
# Description: Read, write and parsing files.
# This is a part of AltExt project.
#

# Get a file's content
def Read(filePath, startPos=0, procedur='r'):
	if (os.path.exists(filePath)):
		fileobj = open(filePath, procedur)
		if (startPos != 0):
			fileobj.seek(startPos)
		data = fileobj.read()
		fileobj.close()
		return data
	else:
		log.Raw("ERR", "Couldn't read from file, filepath doesn't exists.")
		log.Raw("+++", "Filepath=%s" % filePath)

# Get a file's content and size
def ReadAndSize(filePath, startPos=0, procedur='r'):
	data = Read(filePath, startPos, procedur)
	return (data.splitlines(), len(data))

# Set a file's content from a string
def Write(filePath, data, procedur="w"):
	if (os.path.exists(filePath)):
		fileObj = open(filePath, procedur)
		fileObj.write(data)
		fileObj.close()
	else:
		log.Raw("ERR", "Couldnt write to file, filepath doesn't exists.")
		log.Raw("+++", "Filepath=%s" % filePath)

# Get a file's size (textmode, I think)
def GetSize(filePath):
	if (os.path.exists(filePath)):
		return os.stat(filePath).st_size
	else:
		log.Raw("ERR", "Couldn't get file's size, filepath doesn't exists.")
		log.Raw("+++", "Filepath=%s" % filePath)

# Get a file's endposition
def GetEndPos(filePath):
	if (os.path.exists(filePath)):
		stream = open(filePath, "r")
		stream.seek(0, os.SEEK_END)
		position = stream.tell()
		stream.close()
		return position
	else:
		log.Raw("ERR", "Couldn't get file's endposition, filepath doesn't exists.")
		log.Raw("+++", "Filepath=%s" % filePath)

# Get a JSON- decoded dictionary from a list of raw data
def ParseJSON(rawData):
	parData = []
	for item in rawData:
		try:
			parData.append(simplejson.loads(item))
		except:
			log.Raw("ERR", "Couldn't parse JSON-object, data structure isn't complete (%s)" % item)
			log.Raw("+++", "Data=%s" % item)
	return parData

