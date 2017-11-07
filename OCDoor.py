from Object import Object
from panda3d.core import *
from panda3d.bullet import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *

# second scene's door object
# if player holds a key and the key's scale is over the limit that we set, it will send the player to next level
class OCDoor(Object):
	def __init__(self, game, scene, name, modelName, position, scale, animationList = None, animName = None):
		Object.__init__(self, game, scene, name, modelName, position, scale, animationList, animName)
		# generate ghost collider 
		self.ghostModel = self.model.find("**/collider")
		self.model.find("**/collider").removeNode()
		self.addGhostCollider('trigger', "trigger", self.gameSys.triggerMask )
		# flag for next level
		self.isPlayerTouch = False

	def onGhostOverlapped(self, overlappedNodes):
		Object.onGhostOverlapped(self, overlappedNodes)
		
		if(self.gameSys.player.pickedObject != None):
			# check the object holded by the player
			name = self.gameSys.player.pickedObject.getName()
			if(name == "key_p"):
				key = self.scene.getObject(name)
				keyScale = key.getScale()
				# check the key scale
				if(keyScale < Vec3(0.5, 0.5, 0.5)):
					# if true, change next level flag
					self.isPlayerTouch = True

	def update(self):
		if(self.isPlayerTouch == True):
			self.gameSys.player.pickedObject = None
			self.scene.unload()
			self.startImage = OnscreenImage("splashscreen.png")
			return False
		
		return True


	#Remove Ghose Collider
	def remove(self):
		Object.remove(self)
		self.removeGhost('trigger')

	#(inherited method)
	def getGhostShape_internal(self, polyName):
		geomNode = self.ghostModel.node()
		geom = geomNode.getGeom(0)
		shape = BulletConvexHullShape()
		shape.addGeom(geom)
		return shape
	