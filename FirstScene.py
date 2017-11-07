from panda3d.core import Vec3, LVector3, BitMask32
from panda3d.core import *
from direct.actor.Actor import Actor

from Scene import Scene
from Object import Object
from Player import Player
from ODoor import ODoor

#This is where every object for the first level is loaded
class firstLevel(Scene):
	def __init__(self, name, gameSys, window):
		Scene.__init__(self,name, gameSys, window)
		self.map = None
		
		
		
	def load(self):
		Scene.load(self)
		# set player postion
		self.gameSys.player.setPos(Vec3(71, 1, 3))
		self.gameSys.player.heading = 90
		self.gameSys.player.pitch = 50
		
		# spawn objects 
		self.map = Object(self.gameSys, self, 'map', "model/sWall_1.egg", Vec3(0,0,0), 1)

		self.map.loadTexture('model/walltex.png')
		self.map.addTriPollider('map_p', "collider", 0, self.gameSys.floorMask | self.gameSys.collisionMask)

		self.map.setScale(1)

		self.text = Object(self.gameSys, self, 'text', 'model/enter_text.egg', Vec3(0,0,0), 1)
		self.text.setScale(8)
		self.text.setPos((-70, 1, 35))
		self.text.setHpr((90, 0, 0))

		self.barrel1 = Object(self.gameSys, self, 'barrrel1', 'model/barrel.egg', Vec3( 0, 0, 0), 1)
		self.barrel1.generateVertexSet("collider")
		self.barrel1.addConvexCollider('barrel1', "collider", 0.1, self.gameSys.boxMask | self.gameSys.collisionMask)
		self.barrel1.setScale(3)
		self.barrel1.setMass(100)
		self.barrel1.setPos((-15, 25, 0))

		self.barrel2 = Object(self.gameSys, self, 'barrrel2', 'model/barrel.egg', Vec3( 0, 0, 0), 1)
		self.barrel2.generateVertexSet("collider")
		self.barrel2.addConvexCollider('barrel2', "collider", 0.1, self.gameSys.boxMask | self.gameSys.collisionMask)
		self.barrel2.setScale(1.5)
		self.barrel2.setMass(70)
		self.barrel2.setPos((15, 20, 0))

		self.barrel3 = Object(self.gameSys, self, 'barrrel3', 'model/barrel.egg', Vec3( 0, 0, 0), 1)
		self.barrel3.generateVertexSet("collider")
		self.barrel3.addConvexCollider('barrel3', "collider", 0.1, self.gameSys.boxMask | self.gameSys.collisionMask)
		self.barrel3.setScale(2)
		self.barrel3.setMass(50)
		self.barrel3.setPos((-25, -35, 1))

		self.barrel4 = Object(self.gameSys, self, 'barrrel4', 'model/barrel_broken.egg', Vec3( 0, 0, 0), 1)
		self.barrel4.generateVertexSet("collider")
		self.barrel4.addConvexCollider('barrel4', "collider", 0.1, self.gameSys.boxMask | self.gameSys.collisionMask)
		self.barrel4.setScale(1)
		self.barrel4.setMass(100)
		self.barrel4.setHpr((180,0,0))
		self.barrel4.setPos((-15, -20, 1))
		
		self.door = ODoor(self.gameSys, self, 'door', "model/door_outer.egg", 
			        Vec3(0,0,0), 1,   {"open": "model/door_innter-open", "close" : "model/door_innter-close"}, "model/door_innter.egg")

		
		stone = loader.loadTexture('Stone_diffuse.png')
		door = loader.loadTexture('Door_b_diffuse.png')
		self.door.getModel().setTexture(stone,1)
		self.door.aModel.setTexture(door,1)

		#Generate a set of vertices in the collider mesh.
		self.door.generateVertexSet("collider")
		#Add convex collider to the door
		self.door.addConvexCollider('door_p', "collider", 0.1, self.gameSys.boxMask | self.gameSys.collisionMask)
		self.door.getModel().find("**/" + "pCube1").setColor(0,0,0,1)
		self.door.setScale(0.5)
		self.door.setPos((-70, 1, 0))
		self.door.setHpr((90, 0, 0))


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

		render.setShaderAuto()
		
		# Add an ambient light
		alight = AmbientLight('alight')
		alight.setColor((0.2, 0.2, 0.2, 1))
		alnp = render.attachNewNode(alight)
		render.setLight(alnp)
	
	#When called, remove everything to load the next scene. 	
	def unload(self):
		self.map.remove()
		self.door.remove()
		self.text.remove()
		self.barrel1.remove()
		self.barrel2.remove()
		self.barrel3.remove()
		self.barrel4.remove()
		self.lightpivot.remove()
		Scene.unload(self)


