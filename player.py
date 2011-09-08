#!/usr/bin/env python

import dbio, log

#########
# Player object
class PlayerObj:
	def __init__(self, baseData):
		self.baseData = baseData
		self.spawnData = {}
		self.statData = {}

	def Spawned(self, data):
		self.spawnData = data



#########
# Player manager
class Manager:
	def __init__(self, DB):
		self.DB = DB
		self.players = {}

	# Add a player object to the list
	def Add(self, data):
		if (data["player"] not in self.players):
			player = self.DB.GetPlayer(data["vaporId"])
			if (player == None):
				self.DB.NewPlayer(data)
				player = self.DB.GetPlayer(data["vaporId"])
			self.players[data["player"]] = player
			log.Raw("INFO", "Added player to list (name=%s)." % data["nickname"])
		else:
			log.Raw("WARN", "Couldn't add player to list, item already exists.")
			log.Raw("+++", "Data=%s" % data)

	# Remove a player object from the list
	def Remove(self, playerId):
		if (playerId in self.players):
			del self.players[playerId]
		else:
			log.Raw("WARN", "Couldn't remove player from list, item doesn't exists.")
			log.Raw("+++", "PlayerId=%s" % vaporId)

