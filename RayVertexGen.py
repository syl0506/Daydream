import sys
from direct.task.Task import Task
from pandac.PandaModules import *
from panda3d.core import *

# core alogorithm for this game
# retreiving vertices postion data
class RayVertexGen(object):
	def __init__(self):
		self.parsedVertexResult = []

	# core function ---------------------------------------
	def getGeomVertInfo(self, geom):
		self.parsedVertexResult = []
		self.startStep_1(geom)
		return self.parsedVertexResult

	#Saves the world position of the vertices of the object
	def getAbsoluteVertPos(self, targetNode, originalVerticies):
		vertexResult = []
		for i in range(len(originalVerticies)):
			convertedPos = render.getRelativePoint(targetNode, originalVerticies[i])
			vertexResult.append(convertedPos)
		return vertexResult

	#----------------------------------------------------------------
	# helper for parsing verticies(Modified from Panda3d getGeom Tutorial)
	def startStep_1(self,  geom):
		self.startStep_3(geom)
		
	# saves all the prim in the geometry of the object
	def startStep_3(self, geom):
		vdata = geom.getVertexData()
		
		for i in range(geom.getNumPrimitives()):
			prim = geom.getPrimitive(i)
			self.startStep_4(prim, vdata)

	# parse through all prims and save which vertices are part of each prim
	def startStep_4(self, prim, vdata):
		segment=2
		primVertex=dict()
		self.parsedVertexResult=[]
		vertex = GeomVertexReader(vdata, 'vertex')
		prim = prim.decompose()
		for p in range(prim.getNumPrimitives()):
			s = prim.getPrimitiveStart(p)
			e = prim.getPrimitiveEnd(p)
			for i in range(s, e):
				vi = prim.getVertex(i)
				vertex.setRow(vi)
				v = vertex.getData3f()
				#primVertex[p]=primVertex.get(p,[])+[pos]
				primVertex[p]=primVertex.get(p,[])+[v]

		for prim in primVertex:
			for i in range (len(primVertex[prim])-1):
				for j in range (i+1,len(primVertex[prim])):
					self.startStep_4_1(primVertex, prim, i, j, segment)


	# Get all the edges of the prim and get the vertex position value for 
	# the segments in the edge	
	def startStep_4_1(self, primVertex, prim, i, j, segment):
		(x1, y1, z1) = primVertex[prim][i]
		(x2, y2, z2 )= primVertex[prim][j]

		for i in range (segment+2):
			segX = ((x2 - x1)/(segment+1))*i+x1
			segY = ((y2 - y1)/(segment+1))*i+y1
			segZ = ((z2 - z1)/(segment+1))*i+z1
			newSeg=(LPoint3(segX, segY, segZ))
			if newSeg not in self.parsedVertexResult:
				self.parsedVertexResult.append(newSeg)
				
