import sys,os
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import *
from panda3d.core import Filename
from panda3d.core import Vec3, LVector3, BitMask32
from direct.actor.Actor import Actor

from RayVertexGen import RayVertexGen

#Class for all the game objects in the game. 
class Object(object):
	def __init__(self, game, scene, name, modelName, position, scale, animationList = None, animName = None):
		self.gameSys = game
		self.scene = scene
		self.model = None
		self.pModel = None
		self.aModel = None
		self.loadModel(modelName, animationList, animName)
		self.model.setPos(position)
		self.model.setScale(scale)
		self.pMass = None
		#set of the vertices where we are casting the ray to get the ratio
		self.raycastableVertexSet = None
		#register object to the object table of each scene to access easily
		self.registerToSystemTable(name)


	# genereate raycastable points as relative position
	def generateVertexSet(self, polyName):
		geom =None
		if(polyName == None):
			geom = self.model.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
		else:
			geomNode = self.model.find("**/" + polyName).node()
			geom = geomNode.getGeom(0)

		rayVertexGen = RayVertexGen()
		self.raycastableVertexSet = rayVertexGen.getGeomVertInfo(geom) 

	# convert generated points's relative to absolute
	def getAbsoluteRayVertPos(self):
		if(self.raycastableVertexSet == None):
			return

		rayVertexGen = RayVertexGen()
		return rayVertexGen.getAbsoluteVertPos(self.getModel(), self.raycastableVertexSet)
	
	# Trigger when object is adjusted by player
	def onAdjusted(self):
		pass
	
	######################Methods for changing the values of the objects ##########################

	def loadTexture(self, name):
		self.tex=loader.loadTexture(name)
		self.model.setTexture(self.tex)
		
	def loadModel(self, name, animationList, animName):
		self.model=loader.loadModel(name)
		self.model.reparentTo(render)
		
		if(animationList != None):
			self.aModel = Actor(animName, animationList)
			self.aModel.reparentTo(self.model)
	
	def update(self):
		return True
	
	def getModel(self):
		if(self.pModel == None):
			return self.model
		else:
			return self.pModel

	def setPos(self, position):
		if(self.pModel == None):
			self.model.setPos(position)
		else:
			self.pModel.setPos(position)

	def getPos(self):
		if(self.pModel == None):
			return (self.model.getPos())
		else:
			return (self.pModel.getPos())

	def setMass(self, mass):
		if(self.pModel == None):
			self.model.node().setMass(mass)
		else:
			self.pModel.node().setMass(mass)

	def getScale(self):
		if(self.pModel == None):
			return (self.model.getScale())

		else:
			return (self.pModel.getScale())
			
	def setScale(self, scale):
		if(self.pModel == None):
			self.model.setScale(scale)
		else:
			self.pModel.setScale(scale)

	def setHpr(self, Hpr):
		if(self.pModel == None):
			self.model.setHpr(Hpr)
		else:
			self.pModel.setHpr(Hpr)
	
	#register to the scene's object table
	def registerToSystemTable(self, name):
		self.scene.objectTable[name] = self
	
	#turn on off physics by setting mass
	def setPhysicsEnable(self, bool):
		if(self.pModel == None): 
			return
		else:
			if(bool == False):
				self.pModel.node().setMass(0)
			else:
				self.pModel.node().setMass(self.pMass)
			#self.pModel.node().setActive(bool,bool)
	
	def remove(self):
		if(self.pModel != None):
			self.gameSys.pWorld.removeRigidBody(self.pModel.node())
			
		if(self.model != None):
			self.model.removeNode()
			
	# remove a ghost collider set which contains ghost nodepath, class.ghostObject
	def removeGhost(self, rigidName):
		ghost = self.scene.ghostTable.get(rigidName,None)
		if(ghost == None):
			return
		
		self.gameSys.pWorld.removeGhost(ghost)
		#remove ghost nodePath
		self.scene.ghostNodeCollTable.pop(rigidName)
		self.scene.ghostTable.pop(rigidName)
		#remove ghost class
		self.scene.ghostclassTable.pop(rigidName)
		
	# trigger when ghost overlapped by other object
	def onGhostOverlapped(self, overlappedNodes):
		pass
	
	###Collider functions modified from Panda3d Bullet collision sample file
	
	# Bullet box collider 
	def addBoxCollider(self, rigidName, boundary, mass, mask):
		shape = BulletBoxShape(boundary)
		self.pModel = self.gameSys.worldNP.attachNewNode(BulletRigidBodyNode(rigidName))
		self.pModel.node().setMass(mass)
		self.pMass = mass
		self.pModel.node().addShape(shape)
		self.pModel.setCollideMask(mask)
		#self.pModel.node().setDeactivationEnabled(False)
		self.gameSys.pWorld.attachRigidBody(self.pModel.node())
		self.model.clearModelNodes()
		self.model.reparentTo(self.pModel)
		self.registerToSystemTable(rigidName)
	
	#static collider
	def addTriPollider(self, rigidName, polyName, mass, mask):
		geomNode = self.model.find("**/" + polyName).node()
		geom = geomNode.getGeom(0)
		mesh = BulletTriangleMesh()
		mesh.addGeom(geom)
		shape = BulletTriangleMeshShape(mesh, dynamic=True)
		self.addShapeCollider_internal(rigidName, mass, shape, mask)
		self.model.find("**/" + polyName).removeNode()
	
	#dynamic collider
	def addConvexCollider(self, rigidName, polyName, mass, mask):
		geomNode = self.model.find("**/" + polyName).node()
		geom = geomNode.getGeom(0)
		shape = BulletConvexHullShape()
		shape.addGeom(geom)
		self.addShapeCollider_internal(rigidName, mass, shape, mask)
		self.model.find("**/" + polyName).removeNode()
	
	# panda3d bullet ghost collider
	def addGhostCollider(self, rigidName, polyName, mask):
		shape = self.getGhostShape_internal(polyName)
	
		ghost = BulletGhostNode(rigidName)
		ghost.addShape(shape)
		
		np = render.attachNewNode(ghost)
		np.setCollideMask(mask)

		self.gameSys.pWorld.attachGhost(np.node())
		np.reparentTo(self.model)
		self.scene.registerGhost(rigidName, np, ghost, self)
		self.registerToSystemTable(rigidName)


	#Find the mesh for ghost collider and get the shape
	def getGhostShape_internal(self, polyName):
		geomNode = self.model.find("**/" + polyName).node()
		geom = geomNode.getGeom(0)
		shape = BulletConvexHullShape()
		shape.addGeom(geom)
		return shape
	
	def addShapeCollider_internal(self, rigidName, mass, shape, mask):
		self.pModel = self.gameSys.worldNP.attachNewNode(BulletRigidBodyNode(rigidName))
		self.pModel.node().setMass(mass)
		self.pModel.node().addShape(shape)
		self.pModel.setCollideMask(mask)
		self.gameSys.pWorld.attachRigidBody(self.pModel.node())
		self.pMass = mass
		self.model.clearModelNodes()
		self.model.reparentTo(self.pModel)
		self.registerToSystemTable(rigidName)
		
	

	