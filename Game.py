from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "Daydream")
loadPrcFileData("", "win-size 1280 860")

import sys
from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import Vec3, LVector3, BitMask32
from pandac.PandaModules import *
from panda3d.core import LineSegs
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletDebugNode
from panda3d.core import TextNode

from Object import Object
from Player import Player

#scene 
from FirstScene import firstLevel
from SecondScene import secondLevel

#Background Music from Homesick OST
#Reference for the overall structure was Pillow Castle game algorithm


class System(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
				
		#debug variables
		self.debugMode = False
		self.debugLines = []
		self.debugObjects = []

		#system 
		base.disableMouse() 
		#base.oobeCull()
		self.accept('escape', sys.exit)
		self.accept('b', self.toggleDebugMode)
		self.accept('r', self.resetScene)
		
		
		#mask variables
		self.boxMask = BitMask32(0x1)
		self.floorMask = BitMask32(0x2)
		self.collisionMask = BitMask32(0x8)
		self.triggerMask = BitMask32(0X4)
		self.keyMask = BitMask32.bit(4)
		

		self.bgMusic =None
		self.pWorld = None
		self.hotKey = "WASD : Move\nSpace : Jump\nR : Reset\nB : Debug Mode\nESC : Exit "
		

		#init scene
		self.registerScene()
		self.currentScene = None
		self.winWidth = base.win.getXSize()
		self.winHeight = base.win.getYSize() 
		self.showSplashScreen()

	# start with splashScreen
	def showSplashScreen(self):
		self.bgMusic = base.loader.loadSfx("sound/bg_music.wav")
		self.bgMusic.play()
		
		self.startImage = OnscreenImage("splashscreen.png")
		self.startImage.setScale(1.7,1,1)
			
		self.startButton = DirectButton(text = ("Start"), pos = (0, 0, -0.5), scale=0.08, command=self.startGame, relief = None, text_fg = (1, 1, 1, 1))
		self.startButton.setTransparency(1)

	def removeSplashScreen(self):
		self.startButton.remove_node()
		self.startImage.remove_node()

	#reset current level that the player is on.
	def resetScene(self):
		self.unloadScene(self.currentSceneName)
		self.loadScene(self.currentSceneName)

	def displayHotkey(self):
		self.textObject = OnscreenText(text = self.hotKey, pos =(-1.4, 0.9),  scale = 0.05, fg = (0,0,0,1), align = TextNode.ALeft, mayChange=0)

	#start main game   
	def startGame(self):
		self.removeSplashScreen()
		self.displayHotkey()

		#Setup our world with physics. 
		self.pWorld = BulletWorld()
		self.setGravity(-9.81)
		self.setupBulletEngine()
		taskMgr.add(self.update, 'physics-update')

		#Load Player
		self.player = Player( self.win, self, base.camera, (0,0,5))
		self.player.addPlayerCollider('player', 6, 0.5, self.floorMask | self.collisionMask | self.triggerMask)
		self.currentScene = self.loadScene("first")


	# Register each scene in a dictionary with itself saved as the value.
	# This is done to access easily between diffrent scenes. 
	def registerScene(self):
		self.sceneTable = {}
		scene0 = firstLevel("first", self, self.win)
		scene0.registerScene()
		scene1 = secondLevel("second", self, self.win)
		scene1.registerScene()

	#As we are loading the scene, update the player as well, in order to be able to access the objects in the 
	#right scene. 
	def loadScene(self, name):
		self.sceneTable[name].load()
		self.player.setScene(self.sceneTable[name])
		self.currentSceneName = name
		
		return self.sceneTable[name]
	
	def unloadScene(self, name):
		self.sceneTable[name].unload()


	#Update physics and everything in the current scene that is being played. 		
	def update(self, task):
		dt = globalClock.getDt()
		self.pWorld.doPhysics(dt,2)
		
		if(self.currentScene != None):
			self.currentScene.update()
		return task.cont
	
	#Debug Setup
	def setupBulletEngine(self):
		self.worldNP = render.attachNewNode('World')
		self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
		
		#self.debugNP.show()
		self.debugNP.node().showWireframe(True)
		#self.debugNP.node().showConstraints(True)
		#self.debugNP.node().showBoundingBoxes(False)
		#self.debugNP.node().showNormals(True)
		
		self.pWorld.setDebugNode(self.debugNP.node())
		
	def setGravity(self, gravity):
		self.pWorld.setGravity(Vec3(0, 0, gravity))
		print(self.pWorld.getGravity())
	
	#Turning On/Off Debug mode
	def toggleDebugMode(self):
		if self.debugMode == True:
			self.debugMode = False

		elif self.debugMode == False:
			self.debugMode = True

	#Drawing lines for debugging
	def drawDebugLine(self, startPoint, endPoint, color):
		if self.debugMode == True:

			ls = LineSegs()
			ls.setColor(color)
			ls.drawTo(startPoint)
			ls.drawTo(endPoint)
			node = ls.create()
			NodePath(node).reparentTo(render)
			self.debugLines.append(node)

		elif self.debugMode == False:
			return
			
	def clearDebugLines(self):	
		for i in range(len(self.debugLines)):
			self.debugLines[i].removeAllGeoms()

		
		
	#Drawing objects for debugging (mostly for ray hittin the wall. )
	def spwanDebugObject(self, objectName, position, scale):
		if self.debugMode == True:
			model = loader.loadModel(objectName)
			model.reparentTo(render)
			model.setScale(scale)
			model.setPos(position)
			self.debugObjects.append(model)

		elif self.debugMode == False:
			return
		
	def clearDebugObject(self):
		for i in range(len(self.debugObjects)):
			self.debugObjects[i].removeNode()
		
game = System()
game.run()