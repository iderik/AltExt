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

import sqlite3, re, fileio, event, log

# Read manager
class Reader:
	def __init__(self, filePath, protocolFilePath):
		self.filePath = filePath
		self.protocol = {}
		self.onUnknown = event.Hook()
		self.prevFileSize = fileio.GetSize(filePath)
		self.prevEndPos = fileio.GetEndPos(filePath)
		self.Load(protocolFilePath)

	# Load protocol (JSON-entries from AltExt's "protocol.cfg").
	def Load(self, filePath):
		data = fileio.Read(filePath).splitlines()
		for key in data:
			self.protocol[key] = vars(self)["on_%s%s" % (key[:1].upper(), key[1:])] = event.Hook()
		log.Raw("INFO", "Server protocol loaded (%s keys)." % len(data))

	# Route incoming data to trigger events.
	def route(self):
		currFileSize = fileio.GetSize(self.filePath)
		if (self.prevFileSize != currFileSize):
			self.prevFileSize = currFileSize

			data, size = fileio.ReadAndSize(self.filePath, startPos=self.prevEndPos, procedur="rb")
			self.prevEndPos += size

			# Debug output
			log.Raw("DEB", "Read %s bytes (pos %s to %s)." % (size, self.prevEndPos - size, self.prevEndPos))
			log.Raw("+++", "Data: %s" % data)

			data = fileio.ParseJSON(data)

			for line in data:
				dataType = line["type"]
				if (dataType in self.protocol):
					self.protocol.get(dataType, None)(line)
				else:
					log.Raw("ERR", "Couldn't route data to readprotocol, key doesn't exists in list.")
					log.Raw("+++", "Data=%s" % line)



# Write manager
class Writer:
	def __init__(self, filePath):
		self.filePath = filePath

	# Execute a raw command.
	def Raw(self, data):
		fileio.Write("%s\n", 'a')

	# Execute a command with the basic structure.
	def Base(self, port, cmd):
		fileio.Write(self.filePath, "%s,console,%s\n" % (port, cmd), "a")

	# Send a global message to all connected players.
	def server_message(self, port, msg):
		self.Base(port, "serverMessage %s" % msg)

	# Send a privatemessage to a player.
	def server_whisper(self, port, playerName, msg):
		self.Base(port, "serverWhisper %s %s" % (playerName, msg))

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
	def list_players(self, port):
		self.Base(port, "listPlayers")

	# Start tournament
	def TourStart(self, port):
		self.Base(port, "startTournament")

	# Stop tournament
	def TourStop(self, port):
		self.Base(port, "stopTournament")

	def server_status(self, port):
		self.Base(port, "logServerStatus")

# Command manager
class Commander:
	def __init__(self, filePath):
		self.commands = {}
		self.access = {}
		self.onUnknown = event.Hook()
		self.Load(filePath)

	# Load protocol (JSON-entries from Altitude's "custom_json_commands.txt").
	# 
	def Load(self, filePath):
		data = fileio.ParseJSON(fileio.Read(filePath).splitlines())
		for line in data:
			cKey = ""
			for word in re.split("\.", line["name"]):
				cKey += word.capitalize()
			self.commands[line["name"]] = vars(self)["on_%s%s" % (cKey[:1].upper(), cKey[1:])] = event.Hook()
			if ("access" in line):
				self.access[line["name"]] = line["access"]
		log.Raw("INFO", "Server commands loaded (%s keys)." % len(data))

	# check_access:		Check if a player has access to a command.
	# player_access:	Player's accessflags.
	# command:			Command to check against.
	# TODO:				Implement this check into the route method.
	# TODO:				There is a new accessflag structure, see if it still works.
	def check_access(self, player_access, command):
		if (command in self.access):
			cmdAccess = self.access[command]
			if (cmdAccess != ""):
				if (playerAccess != None):
					for flag in playerAccess:
						if (flag in cmdAccess):
							return True
				else:
					return False
			else:
				return True
			return False

	# route:		Route data to trigger defined events.
	# data:			Incoming data.
	def route(self, data):
		cmdType = data["command"]
		if (cmdType in self.commands):
			self.commands.get(cmdType, None)(data)
		else:
			log.Raw("ERR", "Couldn't route data to cmdprotocol, key doesn't exists in list.")
			log.Raw("+++", "Data=%s" % data)

# table: highscore
# rank, points, vaporId
#
# table: medals
# type, points, vaporId
#
#




# Database manager
class Database:
	def __init__(self):
		self.filepath = None

	# stream:		Borrow a connection.
	# row_factory:	
	# connection:	Open stream to databasefile (optional).
	# NOTE: 		Do not forget to close the stream (connection)!
	def stream(self, row_factory=None):
		connection = sqlite3.connect(self.filepath)
		connection.row_factory = row_factory
		return connection

	#
	def get_value(self, table, key, value):
		pass

	#
	def set_value(self, table, key, value, ):
		pass

	# get_data:		Get data from SQLITE3 database
	# table:		Name of table
	# key:			Name of key (Retrieves all 
	# key_value:	Value of key
	# data:			Retrieved data as dictionaries within a list (None if failed)
	def get_data(self, table, key, key_value):
		query = "SELECT * FROM %s WHERE %s=%s" % (table, key, key_value)
		connection = self.stream(self.dictify)
		data = None
		try:
			cursor = connection.cursor()
			data = cursor.execute(query).fetchone()
		except sqlite3.Error, error:
			log.Raw("ERR", "Couldn't read from database.")
			log.Raw("+++", "Filepath=%s" % self.filepath)
			log.Raw("+++", "Querystring=%s" % query)
			log.Raw("+++", "Exception=%s" % error.args[0])
		connection.close()
		return data

	def get_datas(self):
		pass

	# set_dict:		Set data to SQLITE3 database
	# table:		Name of table
	# value:		WILL BE CHANGED SOON, SEE BELOW! maybe...
	# value_key:	^?
	# key:			^?
	# key_value:	^?
	# TODO:			Make it possible to add multiple dicts within the same querystring (add all during one connection session).
	def set_data(self, table, value):
		connection = self.stream(sqlite3.Row)
		query = "INSERT INTO %s VALUES (%s)" % (table, value)
		try:
			cursor = connection.cursor()
			cursor.execute(query)
			connection.commit()
		except sqlite3.Error, error:
			log.Raw("ERR", "Couldn't write to database.")
			log.Raw("+++", "Filepath=%s" % self.filepath)
			log.Raw("+++", "Querystring=%s" % query)
			log.Raw("+++", "Exception=%s" % error.args[0])
		connection.close()

	def set_datas(self):
		pass

	def update_data(self, table, key, key_value, data):
		query = "UPDATE %s SET " % table
		for value_key, value in data.iteritems():
			if (isinstance(value, basestring) is True):
				query = query + "%s=\"%s\", " % (value_key, value)
			else:
				if (value is None):
					value = "NULL"
				query = query + "%s=%s, " % (value_key, value)
		query = query.rstrip(", ") + " WHERE %s=%s" % (key, key_value)
		connection = self.stream()
		try:
			cursor = connection.cursor()
			cursor.execute(query)
			connection.commit()
		except sqlite3.Error, error:
			log.Raw("ERR", "Couldn't write to database.")
			log.Raw("+++", "Filepath=%s" % self.filepath)
			log.Raw("+++", "Querystring=%s" % query)
			log.Raw("+++", "Exception=%s" % error.args[0])
		connection.close()

	def update_datas(self):
		pass

	# dictify:		Convert SQLITE3 data structure to dictionary
	# cursor: 		Connection cursor
	# row:			SQLITE3 data
	# dictionary:	Converted data as dictionary type
	def dictify(self, cursor, row):
	    dictionary = {}
	    for idx, column in enumerate(cursor.description):
		dictionary[column[0]] = row[idx]
	    return dictionary
'''

		cmd = "UPDATE player SET %s=? WHERE vaporId=?"
		for key, value in data.iteritems():
			if (key != "vaporId"):
				cursor.execute(cmd % key, (value, data["vaporId"]))


	# Creates a playerobject in the playertable.
	def NewPlayer(self, data):
		connection = sqlite3.connect(self.filePath)
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()
		cursor.execute("INSERT INTO player VALUES (?,?,?,?,?,NULL,0,0,0,0,NULL,NULL,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)", (data["vaporId"], data["ip"], data["nickname"], data["aceRank"], data["level"]))
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

	def GetAllPlayers(self):
		connection = sqlite3.connect(self.filePath)
		connection.row_factory = self.DictFactory
		cursor = connection.cursor()
		data = []
		for player in cursor.execute("SELECT * FROM player", [vapor]).fetchall():
			data.append(player)
		connection.close()
		return data

	def GetTopPlayers(self):
		connection = sqlite3.connect(self.filePath)
		connection.row_factory = self.DictFactory
		cursor = connection.cursor()
		data = []
		for row in cursor.execute("SELECT * FROM player ORDER BY (kill / death) LIMIT 10").fetchall():
			if (row["death"] != 0):
				data.append(row)
		connection.close()
		return data

	def SetPlayer(self, data):
		connection = sqlite3.connect(self.filePath)
		cursor = connection.cursor()
		cmd = "UPDATE player SET %s=? WHERE vaporId=?"
		for key, value in data.iteritems():
			if (key != "vaporId"):
				cursor.execute(cmd % key, (value, data["vaporId"]))
		connection.commit()
		connection.close()

	# Set playerdata to the playertable.
	def SetPlayerValue(self, vapor, key, value):
		connection = sqlite3.connect(self.filePath)
		cursor = connection.cursor()
		cmd = "UPDATE player SET %s=? WHERE vaporId=?" % key
		cursor.execute(cmd, (value, vapor))
		connection.commit()
		connection.close()

	# TODO Need to load whole db before updating with data (only stats from online players). Hark work work...
	def SetHighscore(self, data):
		pass

	#
	def NewAnnouncement(self):
		pass

	#
	def GetAnnouncement(self):
		pass

	#
	def DeleteAnnouncement(self):
		pass
'''




# Player object
class Player:
	def __init__(self, data):
		self.data = data
		self.alive = False
		self.team = -1
		self.plane = None
		self.perks = {"red":None, "green":None, "blue":None}



# Server object (managing player objects)
class Server:
	def __init__(self):
		self.players = {}

	# Add player to list.
	def add_player(self, playerId, data):
		if data is not None:
			if playerId not in self.players:
				self.players[playerId] = Player(data)
				log.Raw("INFO", "Player added to gamelist (Id=%s, Name=%s)" % (playerId, data["nickname"]))
			else:
				log.Raw("WARN", "Player added to gamelist FAILED. Id already exists (Id=%s, Name=%s)" % (playerId, data["nickname"]))
		else:
			log.Raw("ERR", "Player added to gamelist FAILED. Object is None (empty).")

	# Delete player from list.
	def del_player(self, playerId):
		if (playerId in self.players):
			del self.players[playerId]
			log.Raw("INFO", "Player deleted from gamelist (Id=%s)" % playerId)
		else:
			log.Raw("WARN", "Player deleted from gamelist, FAILED. Object doesn't exists (Id=%s)" % playerId)

	def del_player_all(self):
		self.players = {}

	def get_player(self, playerId):
		if (playerId in self.players):
			return self.players[playerId]
		else:
			return None

	def get_player_with_vapor(self, vaporId):
		for key, value in self.players.iteritems():
			if (vaporId == value.base["vaporId"]):
				return value
		return None

	def get_player_with_nickname(self, nickname):
		for key, value in self.players.iteritems():
			if (nickname == value.base["nickname"]):
				return value
		return None
			
	
# Server manager
class Manager:
	def __init__(self, altitude_dirpath, altext_dirpath):
		self.read = Reader("%s%s" % (altitude_dirpath, "/servers/log.txt"), "%s%s" % (altext_dirpath, "/protocol.cfg"))
		self.write = Writer("%s%s" % (altitude_dirpath, "/servers/command.txt"))
		self.cmd = Commander("%s%s" % (altitude_dirpath, "/servers/custom_json_commands.txt"))
		self.db = Database()
		self.debug = False
		self.servers = {}
		log.Raw("INFO", "Manager initialized.")
		log.Raw("+++", "Server input    = %s%s" % (altitude_dirpath, "/servers/log.txt"))
		log.Raw("+++", "Server output   = %s%s" % (altitude_dirpath, "/servers/command.txt"))
		log.Raw("+++", "Server cmds     = %s%s" % (altitude_dirpath, "/servers/custom_json_commands.txt"))
		log.Raw("+++", "Altext protocol = %s%s" % (altext_dirpath, "/protocol.cfg"))

	# Add server to list.
	def add_server(self, port):
		if (port not in self.servers):
			self.servers[port] = Server()
			log.Raw("INFO", "Server added (port=%s)" % port)
			self.write.server_message(port, "AltExt system is now activated.")
			self.write.server_status(port)
		else:
			log.Raw("WARN", "Server added, FAILED. Object already exists (port=%s)" % port)

	# Delete server from list.
	def del_server(self, port):
		if (port in self.servers):
			del self.servers[port]
			log.Raw("INFO", "Server deleted (port=%s)" % port)
		else:
			log.Raw("WARN", "Server deleted, FAILED. Object doesn't exists (port=%s)" % port)
