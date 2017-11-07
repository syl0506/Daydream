from panda3d.core import Vec3, LVector3, BitMask32
from panda3d.core import *
from direct.actor.Actor import Actor

from Scene import Scene
from Object import Object
from Player import Player
from OCDoor import OCDoor



#This is where every object for the second level is loaded

class secondLevel(Scene):
	def __init__(self, name, gameSys, window):
		Scene.__init__(self,name, gameSys, window)
		self.map = None
		self.door = None
		
	def load(self):
		Scene.load(self)
		#set the player start position
		self.gameSys.player.setPos(Vec3(0, -16 , 25 ))
		
		# spawn objects	
		self.map = Object(self.gameSys, self, 'map1', "model/pillarcatholic_1.egg", Vec3(0,0,0), 1)
		self.map.loadTexture('model/cWalltex.png')
		self.map.addTriPollider('map1_p', "collider", 0, self.gameSys.floorMask | self.gameSys.collisionMask)
		self.map.setScale(1)
	
		self.door = OCDoor(self.gameSys, self, 'door', "model/catalogicDoor.egg", 
				Vec3(0,140,-10), 3)
		stone = loader.loadTexture('Stone_diffuse.png')
		door = loader.loadTexture('Door_b_diffuse.png')
		self.door.getModel().find("**/" + "Doorway_a").setTexture(stone, 1)
		self.door.getModel().find("**/" + "Door_b.001").setTexture(door, 1)

		self.text = Object(self.gameSys, self, 'text', 'model/key_text.egg', Vec3(0,0,0), 1)
		self.text.setScale(6)
		self.text.setPos((5, 45, 35))
		self.text.setHpr((0, 0, 0))
			

		self.key = Object(self.gameSys, self, 'key', "model/key.egg", Vec3(0,0,0), 1)
		self.key.loadTexture("model/keyTexture.tga")
		#Generate a set of vertices in the collider mesh.
		self.key.generateVertexSet("collider")
		#Add convex Collider to the key
		self.key.addConvexCollider('key_p', "collider", 0.1, self.gameSys.boxMask | self.gameSys.collisionMask)
		self.key.setScale(2)
		self.key.setPos((0, 20, 28))
		self.key.setHpr((0, 0, 0))
		self.key.setPhysicsEnable(False)

		#Light Set (up) Modified from Panda3d Sample Disco Light Tutorial
		self.lightpivot = render.attachNewNode("lightpivot")
		self.lightpivot.setPos(0, 0, 25)
		plight = PointLight('plight')
		plight.setColor((1, 1, 1, 1))
		plight.setAttenuation(LVector3(1.0, 0.05, 0))
		plnp = self.lightpivot.attachNewNode(plight)
		plnp.setPos(45, 0, 0)
		self.map.model.setLight(plnp)

		render.setLight(plnp)
		#self.map.model.setLight(plnp)

		render.setShaderAuto()
		
		# Add an ambient light
		alight = AmbientLight('alight')
		alight.setColor((0.2, 0.2, 0.2, 1))
		self.alnp = render.attachNewNode(alight)
		render.setLight(self.alnp)
		
	#unload everything to load next stage
	def unload(self):
		self.map.remove()
		self.door.remove()
		self.key.remove()
		self.text.remove()
		Scene.unload(self)
		



