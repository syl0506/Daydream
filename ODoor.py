from Object import Object
from panda3d.core import *
from panda3d.bullet import *

# first scene's door object
# if its scale is over than the limit that we've set, it will open and send the player to next level
class ODoor(Object):
	def __init__(self, game, scene, name, modelName, position, scale, animationList = None, animName = None):
		Object.__init__(self, game, scene, name, modelName, position, scale, animationList, animName)
		self.isDoorOpened = False
		# checks for player contact
		self.ghostModel = self.model.find("**/trigger")
		self.model.find("**/trigger").removeNode()
		# flag for next level
		self.isPlayerTouch = False
	
	#(inherited method) generate saved model' (named trigger) ghost collider
	def getGhostShape_internal(self, polyName):
		geomNode = self.ghostModel.node()
		geom = geomNode.getGeom(0)
		shape = BulletConvexHullShape()
		shape.addGeom(geom)
		return shape
	
	#(inherited method) if the scale gets smaller again, the door closes and the 
	#system is not going to detect player's contact
	# and vice versa
	def onAdjusted(self):
		Object.onAdjusted(self)
		# thereshold
		if (self.getScale())>LVector3f(4, 4, 4):
			self.isDoorOpened = True
			self.playAnimation(self.isDoorOpened)
			self.addGhostCollider('trigger', "trigger", self.gameSys.triggerMask )

		elif  (self.getScale())<=LVector3f(4.5, 4.5, 4.5) and self.isDoorOpened==True:
			self.removeGhost('trigger')
			self.isDoorOpened = False
			self.playAnimation(self.isDoorOpened)
	
	#(inherited method) - trigger when objects are overlapped with this object 
	def onGhostOverlapped(self, overlappedNodes):
		Object.onGhostOverlapped(self, overlappedNodes)
		#change flag for going to next scene
		self.isPlayerTouch = True

	#(inherited method) update every frame	
	def update(self):
		if(self.isPlayerTouch == True):
			#move next scene
			self.scene.unload()
			self.gameSys.currentScene = self.gameSys.loadScene("second")
			return False
		
		return True

	#(inherited method) remove ghost
	def remove(self):
		Object.remove(self)
		self.removeGhost('trigger')
	
	def playAnimation(self, doorTriggered):
		if doorTriggered == False:
			self.aModel.play("close")
		elif doorTriggered == True:
			self.aModel.play("open")