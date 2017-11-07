import sys
from direct.task.Task import Task
from pandac.PandaModules import *
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from direct.interval.LerpInterval import LerpPosInterval

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletConeShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import ZUp

from panda3d.core import Vec3, Vec4, LVector3, LVector3f,BitMask32

class Player(object):
	def __init__(self, window, gameSystem, camera, position):

		#model
		self.pModel=None
		self.doorTriggered=False
		
		#system
		self.window = window
		self.gameSys = gameSystem
		self.scene = None
		self.camera = camera
		self.camera.setPos(position)

		#pick variable
		self.pickedObject = None
		self.pickedDistance = 10
		self.oneTime=False

		#sound
		self.pickedSound = base.loader.loadSfx("sound/grab_sound.wav")

		#image
		self.crossHair = 'crosshair.png'	
		self.handGrab = 'hand_grab.png'
		self.handUngrab = 'hand_ungrab.png'
		
		#Input registeration
		self.moveSpeed =  50
		self.keyMap = {"forward" : False, "right" : False, "back" : False, "left" : False, "jump" : False}
		self.isJumping = False
		self.registerInput()
		
		#mouse related variable
		self.pitch = 0
		self.heading = 0
		self.pitchMax = 60
		self.pitchMin = -60
		self.mouseSensitivity = 0.2
		self.initalize = False
		
		self.pickEnabled = True
		
		
		#vertex 
		self.targetVertexPos = []
		
		#register Task
		taskMgr.add(self.update, "player_update")
	
	# set current scene  
	def setScene(self, scene):
		self.scene = scene
	
	def addPlayerCollider(self, rigidName, height, radius, mask):
		shape=BulletCapsuleShape(radius, height - 2*radius, ZUp)

		self.pModel = self.gameSys.worldNP.attachNewNode(BulletCharacterControllerNode(shape, radius, rigidName))
		self.pModel.setCollideMask(mask)
		self.gameSys.pWorld.attachCharacter(self.pModel.node())
		self.camera.reparentTo(self.pModel)
	
	def setPos(self, position):
		if(self.pModel == None):
			self.camera.setPos(position)
		else:
			self.pModel.setPos(position)

	# update loop task
	def update(self, task):	
		#input
		self.updateCamera()
		self.updateKeyboardInput()
		self.updateJump(task)
		
		#update
		self.updatePickedObject()
		self.attachDetectRay(task)
		return task.cont

	def loadImage(self, name, pos = (0,0,0)):
		self.myImage.destroy()
		self.myImage = OnscreenImage(name, pos)
		self.myImage.setTransparency(TransparencyAttrib.MAlpha)

	#Modify the hand UI
	def handIcon(self, task):
		if self.initalize == False:
			self.initalize = True
			self.myImage = OnscreenImage(self.crossHair)
			self.myImage.setTransparency(TransparencyAttrib.MAlpha)

		elif self.pickedObject!=None:
			self.loadImage(self.handGrab)
			self.myImage.setScale(0.1)
			
		elif self.pickedObject==None and self.pickEnabled == True:
			self.loadImage(self.handUngrab)
			self.myImage.setScale(0.1)

		elif self.pickedObject == None and self.pickEnabled == False:
			self.loadImage(self.crossHair)
			self.myImage.setScale(0.5)

		return task.done
			
	# update picked object's scale
	# picked object scale is maintained and the position is hovering in front of the camera
	# while player is moving around	
	def updatePickedObject(self):
		camDir = self.camera.getNetTransform().getQuat().getForward()
		camPos = render.getRelativePoint(self.pModel,self.camera.getPos())

		if(self.pModel != None):
			camPos = render.getRelativePoint(self.pModel,self.camera.getPos())
		else:
			camPos = self.camera.getPos()

		if self.pickedObject != None:
			pickedClass = self.scene.getObject( self.pickedObject.getName())
			# make the picked object not affected by gravity or other physics
			pickedClass.setPhysicsEnable(False)

			# for calculating offset
			
			if self.oneTime == False:
				self.oneTime = True
	
				dist = self.getDistance(camPos, pickedClass.getPos())
				oldPos = camDir * dist + camPos
				self.startObjectPos=pickedClass.getPos()
				self.startObjectScale=pickedClass.getScale()

				self.offset = oldPos - pickedClass.getPos()

				self.startCamH = self.camera.getH()
				self.startObjectH = pickedClass.pModel.getH()

				grabbedPos = camDir*self.pickedDistance+camPos
				ratio=self.getDistance(grabbedPos, camPos)/self.getDistance(oldPos, camPos)

				self.adjustedOffset=self.offset*ratio

				pickedClass.setScale(pickedClass.getScale()*ratio)

				self.grabbedCamDir = camDir 
				self.grabbedCamPos = camPos
			
			pickedClass.setPos(camPos + camDir * self.pickedDistance - self.adjustedOffset)
			
			headingOffset = self.camera.getH() - self.startCamH
			pickedClass.pModel.setH(self.startObjectH + headingOffset)
	
		elif self.oneTime == True and self.pickedObject == None:
			self.oneTime=False

	def onMouseClick(self, event):
		if(self.pickedObject == None):
			self.checkPickerRay()
			if self.pickedObject != None:
				self.pickedSound.play()

		else: #release
			self.shootRays()
			self.pickedSound.play()
			pickedClass = self.scene.getObject( self.pickedObject.getName())
			pickedClass.setPhysicsEnable(True)
			self.pickedObject = None
			
	
	# shoot a forward ray for grabing object
	def checkPickerRay(self):
		rFrom = render.getRelativePoint(self.pModel, self.camera.getPos())
		rTo   = self.camera.getNetTransform().getQuat().getForward() * 9999
		#self.gameSys.drawDebugLine(rFrom, rTo, Vec4(0,0,1,1))
		result= self.gameSys.pWorld.rayTestClosest(rFrom, rTo, self.gameSys.boxMask)
	
		if(result.hasHit() != False):

			self.pickedObject = result.getNode()

	# shoot a forward ray for check grabbable object
	def attachDetectRay(self, task):
		self.handIcon(task)
		if(self.pModel != None):
			rFrom = render.getRelativePoint(self.pModel, self.camera.getPos())
		else:
			rFrom = self.camera.getPos()
		
		rTo   = self.camera.getNetTransform().getQuat().getForward() * 9999
		result= self.gameSys.pWorld.rayTestClosest(rFrom, rTo, self.gameSys.boxMask)

		if result.getNode()!=None:
			self.pickEnabled = True
		else:
			self.pickEnabled = False

		return task.cont
	'''
	-----------------------------------------------------------------------------------------
	Geom related Method
	-----------------------------------------------------------------------------------------
	'''
	# shoot the ray from camera to object's rayvastable points and then calculated a ratio for putting back
	def shootRays(self):
		pickedClass = self.scene.getObject( self.pickedObject.getName())
		# get raycatable points
		targetVertexPos = pickedClass.getAbsoluteRayVertPos()

		self.gameSys.clearDebugLines()
		self.gameSys.clearDebugObject()
		self.smallestRatio=9999999
		#shoot the ray for every vertex and return hitPoint

		for i in range(len(targetVertexPos)):
			rFrom = render.getRelativePoint(self.pModel, self.camera.getPos())
			rTo   = (targetVertexPos[i] -rFrom) 
			rTo.normalize()
			rTo *= 9999
			
			result= self.gameSys.pWorld.rayTestClosest(rFrom, rTo, self.gameSys.floorMask)
			
			if(result.hasHit() != False):
				camPos = render.getRelativePoint(self.pModel, self.camera.getPos())
				cameraToVertexD = self.getDistance(targetVertexPos[i], camPos)
				HitPosToCameraD = self.getDistance(result.getHitPos(), camPos)
				ratio =  HitPosToCameraD / cameraToVertexD
				# find smallest ratio, which means the nearest object from the wall
				if ratio < self.smallestRatio:
					self.smallestRatio = ratio
					
				self.gameSys.drawDebugLine(rFrom, result.getHitPos(), Vec4(0,1,0,1))
				self.gameSys.spwanDebugObject('smiley', result.getHitPos(), 0.5)
		
		if self.smallestRatio==9999999:
			return

		else:
			self.adjustObject(pickedClass)
	
	# adjust object's scale 
	def adjustObject(self, pickedClass):
		camPos = render.getRelativePoint(self.pModel, self.camera.getPos())
		cameraToObjectD = self.getDistance(camPos, pickedClass.getPos())

		vec = pickedClass.getPos() - camPos
		vec.normalize()

		pickedClass.setScale(pickedClass.getScale()*self.smallestRatio)
		offset = self.adjustedOffset*self.smallestRatio

		adjustedDis = self.getDistance(camPos, pickedClass.getPos()) * self.smallestRatio
		pickedClass.setPos(vec * adjustedDis + camPos)
		pickedClass.onAdjusted()

	'''
	-----------------------------------------------------------------------------------------
	Helper Method
	-----------------------------------------------------------------------------------------
	'''
	# get distance from first vector to second vector
	def getDistance(self, firVec, secVec):
		xD =  secVec.getX() - firVec.getX()
		yD = secVec.getY() - firVec.getY()
		zD = secVec.getZ() - firVec.getZ()
		return ( (xD**2) + (yD**2) + (zD**2) )**0.5
	'''
	-----------------------------------------------------------------------------------------
	Input related Method
	-----------------------------------------------------------------------------------------
	'''
	def updateKeyboardInput(self):
		quat = self.camera.getNetTransform().getQuat()
		dt = globalClock.getDt()
		pos = self.pModel.getPos()
		dir = Vec3()  
		speed = Vec3(0, 0, 0)
		v = 10
		
		if(self.keyMap["forward"] == False and self.keyMap["left"] == False and self.keyMap["right"] == False and self.keyMap["back"] == False):


			speed = Vec3(0, 0, 0)

		if self.keyMap["left"]: 
			speed += quat.getRight() * -1
			
            
		if self.keyMap["right"]:
			speed += quat.getRight()
			
            
		if self.keyMap["back"]:
			speed += quat.getForward() * -1
	
            
		if self.keyMap["forward"]:
			speed += quat.getForward()

		dir=Vec3(dir)
		dir.z=0
	
		
		if(self.pModel != None):
			self.pModel.node().setLinearMovement(speed * v, True)

		else:
			self.camera.setPos(pos + speed * v)


	def updateJump(self, task):
		dt = globalClock.getDt()
		
		if (self.keyMap["jump"] == True and self.isJumping == False):
			self.isJumping = True
			self.jumpAccel = 2.5
			self.startJumpPos=self.pModel.getPos()

		if self.isJumping == True: 
			self.jumpAccel = self.jumpAccel - dt * 10 
			accelVector =  Point3(0,0,self.jumpAccel )
			pos = self.pModel.getPos() + accelVector

			if pos.getZ()>self.startJumpPos.getZ():
				self.pModel.setPos(pos)

			else:
				self.isJumping=False
				self.pModel.setZ(self.startJumpPos.getZ())
				return task.done	

	def updateCamera(self):
		mouse= self.window.getPointer(0)
		x = mouse.getX()
		y = mouse.getY()
		if self.window.movePointer(0,self.window.getXSize()/2, self.window.getYSize()/2):
			self.heading=self.heading-(x-self.window.getXSize()/2)*self. mouseSensitivity
			self.pitch=self.pitch-(y-self.window.getYSize()/2)*self.mouseSensitivity
		if self.pitch < self.pitchMin:
			self.pitch=self.pitchMin
		if self.pitch> self.pitchMax:
			self.pitch=self.pitchMax
		self.camera.setHpr(self.heading, self.pitch, 0)
		#self.pModel.setHpr(self.heading,  self.pitch, 0)
	
	def setKey(self, key, value):
		self.keyMap[key]=value
	
	def registerInput(self):
		#mouse
		base.accept("mouse1", self.onMouseClick, ['down'])
		
		#keyboard
		base.accept("w", self.setKey, ["forward", True])
		base.accept("a", self.setKey, ["left", True])
		base.accept("d", self.setKey, ["right", True])
		base.accept("s", self.setKey, ["back", True])
		base.accept("w-up", self.setKey, ["forward", False])
		base.accept("a-up", self.setKey, ["left", False])
		base.accept("s-up", self.setKey, ["back", False])
		base.accept("d-up", self.setKey, ["right", False])

		if self.isJumping==False:
			base.accept("space", self.setKey, ["jump", True])
			
		base.accept("space-up", self.setKey, ["jump", False])