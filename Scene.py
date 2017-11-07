from direct.task.Task import Task

from panda3d.bullet import BulletGhostNode
from panda3d.bullet import BulletBoxShape

#Superclass of all the scenes in the game. 
class Scene(object):
	def __init__(self, name, gameSys, window):
		self.gameSys = gameSys
		self.win = window
		self.name = name
		#Object dictionary for finding through name
		self.objectTable = {}
		#Ghost (collision checking to go to other level)
		self.ghostclassTable = {}
		self.ghostNodeCollTable = {}
		self.ghostTable = {}

	#Rememeber what is being detected as collision, the ghost itself and the class of the ghost. 
	def registerGhost(self, name, collNode, ghost, gClass):
		self.ghostNodeCollTable[name] = collNode
		self.ghostTable[name] = ghost
		self.ghostclassTable[name] = gClass

	# register the scene itself in the scene dictionary. 	
	def registerScene(self):
		self.gameSys.sceneTable[self.name] = self 

	def update(self):
		self.updateGhostCollider()
		self.updateObject()

	#For all the collision eetected in the ghost collider, do appropriate action for the collision. 
	def updateGhostCollider(self):
		for key in self.ghostNodeCollTable:
			ghostColl = self.ghostNodeCollTable[key]
			if(ghostColl != None):
				if (ghostColl.node().getNumOverlappingNodes() > 0 ):
					self.ghostclassTable[key].onGhostOverlapped(ghostColl.node().getOverlappingNodes())
	
	# update objects in the scene 
	def updateObject(self):
		for key in self.objectTable:
			res = self.objectTable[key].update()
			if(res == False):
				break
	
	#load the scene element, this method is inherited by child method
	def load(self):
		pass
	
	def unload(self):
		self.objectTable = {}
		
		#ghost
		self.ghostclassTable = {}
		self.ghostNodeCollTable = {}
		self.ghostTable = {}
		pass
	
	#retrieve Object by key
	def getObject(self, key):
		return self.objectTable.get(key,None)