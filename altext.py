#!/usr/bin/env python

#
# AltExt (Altitude Extension), an API for Altitude game server.
#
# Altitude Game	Website	= http://altitudegame.com
# AltExt API Website	= http://github.com/iderik/altext
#
# Altitude (in-game)	= {arr}Iderik
# Altitude (forum)		= idk
# IRC					= iderik @ irc.freenode.net
# E-Mail				= idk@hush.com
#

import fileio, event, log

# Read manager
class Reader:
	def __init__(self, filePath):
		self.filePath = filePath
		self.protocol = {}

	# Load protocol (JSON-entries from AltExt's "protocol.cfg").
	def Load(self, filePath="data/protocol.cfg"):
		data = fileio.Read(filePath).splitlines()
		for key in data:
			self.protocol[key] = vars(self)["on%s%s" % (key[:1].upper(), key[1:])] = event.Hook()
		log.Raw("INIT", "Server protocol loaded (%s keys)." % len(data))

	# Route incoming data to trigger events.
	def Route(self):
		dataType = data["type"]
		if (dataType in self.protocol):
			self.protocol.get(dataType, None)(data)
		else:
			log.Raw("ERR", "Couldn't route data to readprotocol, key doesn't exists in list.")
			log.Raw("+++", "Data=%s" % data)



# Write manager
class Writer:
	def __init__(self, filePath):
		self.filePath = filePath

	# Execute a raw command.
	def Raw(self, data):
		fileio.Write("%s\n", 'a')

	# Execute a command with the basic structure.
	def Base(self, port, cmd):
		fileio.Write(self.filePath, "%s,console,%s\n" % (port, cmd), 'a')

	# Send a global message to all connected players.
	def ServerMessage(self, port, msg):
		self.Base(port, "serverMessage %s" % msg)

	# Send a privatemessage to a player.
	def ServerWhisper(self, port, msg, nick):
		self.Base(port, "serverWhisper %s %s" % (nick, msg))

	# Change server's map.
	def ServerMap(self, port, mapName):
		self.Base(port, "changeMap %s" % mapName)

	# Move a player to another team.
	def PlayerTeam(self, port, playerName, teamId):
		self.Base(port, "assignTeam %s %s" % (playerName, teamId))

	# Move a player to another server.
	def PlayerMove(self, port, playerName, serverIp, serverPort, password):
		self.Base(port, "serverRequestPlayerChangeServer %s %s:%s %s" % (playerName, serverIp, serverPort, password))

	# Kick a player from the server.
	def PlayerKick(self, port, playerName):
		self.Base(port, "kick %s" % playerName)

	# Ban a player from the server, using PlayerName.
	def PlayerBanWithName(self, port, playerName, duration, unitTime, reason):
		self.Base(port, "ban %s %s %s %s" % (playerName, duration, unitTime, reason))

	# Ban a player from the server, using VaporId.
	def PlayerBanWithVapor(self, port, vaporId, duration, unitTime, reason):
		self.Base(port, "addBan %s %s %s %s" % (vaporId, duration, unitTime, reason))

	# Unban a player from the server, using VaporId.
	def PlayerUnban(self, port, vaporId):
		self.Base(port, "removeBan %s" % vaporId)

	# Request a a list of all connected player's position.
	def PlayerPositions(self, port):
		self.Base(port, "logPlanePositions")

	# Balance both teams using Altitude's original formula.
	def TeamBalance(self, port):
		self.Base(port, "balanceTeam")

	# Start a vote to execute a specified command.
	def Vote(self, port):
		pass

	# Start a vote about anything.
	def VoteCustom(self, port):
		pass

	# Request a list of all banned players.
	def ListBan(self, port):
		self.Base(port, "listBans")

	# Request a list of all Altitude's original commands.
	def ListCommands(self, port):
		self.Base(port, "listCommands")

	# Request a list of all connected players.
	def ListPlayers(self, port):
		self.Base(port, "listPlayers")

	# Start tournament
	def TourStart(self, port):
		self.Base(port, "startTournament")

	# Stop tournament
	def TourStop(self, port):
		self.Base(port, "stopTournament")



# Command manager
# TODO Fix access list!
class Commander:
	def __init__(self):
		self.commands = {}
		self.access = {}

	# Load protocol (JSON-entries from Altitude's "custom_json_commands.txt").
	def Load(self, filePath)
		data = fileio.ParseJSON(fileio.Read(filePath).splitlines())
		for line in data:
			cKey = ""
			for word in re.split("\.", line["name"]):
				cKey += word.capitalize()
			self.commands[line["name"]] = vars(self)["on%s%s" % (cKey[:1].upper(), cKey[1:])] = event.Hook()
			if ("access" in line):
				self.access[line["name"]] = line["access"]
		log.Raw("INIT", "Server commands loaded (%s keys)" % len(data))

	#
	def Access(self):
		pass

	# Route incoming data to trigger events.
	def Route(self, data):
		cmdType = data["command"]
		if (cmdType in self.cmds):
			self.commands.get(dataType, None)(data)
		else:
			log.Raw("ERR", "Couldn't route data to cmdprotocol, key doesn't exists in list.")
			log.Raw("+++", "Data=%s" % data)



# Database manager
class Databaser:
	def __init__(self, filePath):
		self.filePath = filePath

	# Convert SQL-table to dictionary
	def DictFactory(self, cursor, row):
	    dictionary = {}
	    for idx, column in enumerate(cursor.description):
		dictionary[column[0]] = row[idx]
	    return dictionary

	# Creates a playerobject in the playertable.
	def NewPlayer(self, data):
		connection = sqlite3.connect(self.filePath)
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()
		cursor.execute("INSERT INTO player VALUES (?,?,?,?,?,NULL)", (data["vaporId"], data["ip"], data["nickname"], data["aceRank"], data["level"]))
		connection.commit()
		connection.close()

	# Deletes a playerobject in the playertable.
	def DeletePlayer(self, vapor):
		connection = sqlite3.connect(self.filePath)
		cursor = connection.cursor()
		cursor.execute("DELETE FROM player WHERE vaporId=?", [vapor])
		connection.commit()
		connection.close()

	# Get playerdata from the playertable.
	def GetPlayer(self, vapor):
		connection = sqlite3.connect(self.filePath)
		connection.row_factory = self.DictFactory
		cursor = connection.cursor()
		data = cursor.execute("SELECT * FROM player WHERE vaporId=?", [vapor]).fetchone()
		connection.close()
		return data

	# Set playerdata to the playertable.
	def SetPlayerValue(self, vapor, key, value):
		connection = sqlite3.connect(self.filePath)
		cursor = connection.cursor()
		cmd = "UPDATE player SET %s=? WHERE vaporId=?" % key
		cursor.execute(cmd, (value, vapor))
		connection.commit()
		connection.close()

	#
	def NewAnnouncement(self):
		pass

	#
	def GetAnnouncement(self):
		pass

	#
	def DeleteAnnouncement(self):
		pass

# Player object
class Player:
	def __init__(self, base):
		for key, value in base.iteritems():
			vars(self)[key] = value
		self.alive = False
		self.team = -1
		self.plane = None
		self.perk = {"red":None, "green":None, "blue":None}
		self.skin = None



# Server object (managing player objects)
class Server:
	def __init__(self):
		players = {}

	# Add player to list.
	def AddPlayer(self, data):
		playerId = data["player"]
		if (playerId not in self.players):
			self.players[playerId] = Player(data)
			log.Raw("INFO", "Player added (id=%s name=%s)" % (playerId, data["nickname"]))
		else:
			log.Raw("WARN", "Player added, failed. Object already exists (id=%s name=%s)" % (playerId, data["nickname"]))

	# Delete player from list.
	def DelPlayer(self, data):
		playerId = data["player"]
		if (playerId in self.players):
			del self.players[playerId]
			log.Raw("INFO", "Player deleted (id=%s name=%s)" % (playerId, data["nickname"]))
		else:
			log.Raw("WARN", "Player deleted, failed. Object doesn't exists (id=%s name=%s)" % (playerId, data["nickname"]))


	
# Server manager
class Manager:
	def __init__(self, readFilePath, writeFilePath, dbFilePath):
		self.Read = Reader(readFilePath)
		self.Write = Writer(writeFilePath)
		self.Cmd = Commander()
		self.DB = Databaser(dbFilePath)
		self.servers = {}

	# Add server to list.
	def AddServer(self, port):
		if (port not in self.servers):
			self.servers[port] = Server()
			log.Raw("INFO", "Server added (port=%s)" % port)
			self.Write.ServerMessage(port, "AltExt system has been loaded.")
		else:
			log.Raw("WARN", "Server added, failed. Object already exists (port=%s)" % port)

	# Delete server from list.
	def DelServer(self, port):
		if (port in self.servers):
			del self.servers[port]
			log.Raw("INFO", "Server deleted (port=%s)" % port)
		else:
			log.Raw("WARN", "Server deleted, failed. Object doesn't exists (port=%s)" % port)
