#bmp_processor
#Por Luis Diego Fernandez
#V_A
import sys
import math
import struct
import random
import numpy as np

class bmpImage:

	# Define init(). Attributes Initializer
	def __init__(self, new_width, new_height):
		# image data
		self.image_data = bytes()

		# image attributes
		self.width = 0
		self.height = 0
		self.bits_per_pixel = 0
		self.row_bytes = 0
		self.row_padding = 0

		# viewport
		self.vp_x = 0
		self.vp_y = 0
		self.vp_width = 0
		self.vp_height = 0

		# clear colors
		self.clearRgbRed = 0
		self.clearRgbGreen = 0
		self.clearRgbBlue = 0

		# paint colors
		self.paintRgbRed = 0
		self.paintRgbGreen = 0
		self.paintRgbBlue = 0

		# texture image
		self.textureImg = []
		self.texture_width = 0
		self.texture_height = 0
		self.texture_width_ratio = 0
		self.texture_height_ratio = 0

		# add values
		self.constructImage(new_width, new_height)

	# Define constructImage(int, int). Creates the header for the BMP image
	# returns: 0 on success
	def constructImage(self, new_width, new_height):

		self.width = new_width
		self.height = new_height
		self.row_bytes = new_width * 4
		self.row_padding = int(math.ceil(int(self.row_bytes / 4.0))) * 4 - self.row_bytes

		data =  bytes('BM', 'utf-8')
		data += struct.pack('i', 26 + 4 * self.width * self.height)
		data += struct.pack('h', 0)
		data += struct.pack('h', 0)
		data += struct.pack('i', 26)
		data += struct.pack('i', 12)
		data += struct.pack('h', self.width)
		data += struct.pack('h', self.height)
		data += struct.pack('h', 1)
		data += struct.pack('h', 32)

		self.image_data = data

		self.z_buffer = [
	      [-float('inf') for x in range(self.width)]
		  for y in range(self.height)
	    ]

		return 0

	# Define glAbsolutePointPaint(int, int). Paints an individual pixel
	# returns: 0 on success
	def glAbsolutePoint(self,x, y):

		# changes the data of an individual pixel
		data = self.image_data[:26 + ((y - 1) * (self.width + self.row_padding) + (x - 1)) * 4]
		data += self.rgbToByte(self.paintRgbRed, self.paintRgbGreen, self.paintRgbBlue)
		data += self.image_data[30 + ((y - 1) * (self.width + self.row_padding) + (x - 1)) * 4:]

		self.image_data = data

		return 0

	# Define glAbsolutePointPaint(int, int). Paints an individual pixel
	# returns: 0 on success
	def glAbsolutePointWithColor(self,x, y,color):

		# changes the data of an individual pixel
		data = self.image_data[:26 + ((y - 1) * (self.width + self.row_padding) + (x - 1)) * 4]
		data += color
		data += self.image_data[30 + ((y - 1) * (self.width + self.row_padding) + (x - 1)) * 4:]

		self.image_data = data

		return 0

	# Define glLine(). Paints a line from point (xi,yi) to (xf,yf)
	# returns: 0 on success
	def glAbsoluteLine(self,xi,yi,xf,yf):

		dy = yf - yi
		dx = xf - xi

		if (dx == 0):
			for y in range(dy + 1):
				self.glAbsolutePoint(xi,y + yi)

			return 0

		m = dy/dx
		grad = m <= 1 and m >= 0

		if grad and xi > xf:
			xi, xf = xf, xi
			yi, yf = yf, yi
			dy = yf - yi
			dx = xf - xi
			m = dy/dx
			grad = m <= 1 and m >= 0

		elif yi > yf:
			xi, xf = xf, xi
			yi, yf = yf, yi
			dy = yf - yi
			dx = xf - xi
			m = dy/dx
			grad = m <= 1 and m >= 0

		if (grad):
			for x in range(dx + 1):
				y = round(m*x + yi)
				self.glAbsolutePoint(x+xi,y)
		else:
			m = 1/m
			for y in range(dy + 1):
				x = round(m*y + xi)
				self.glAbsolutePoint(x,y + yi)

		return 0

	# Define glClear(). It paints the whole image in a specific rgb color.
	# returns: 0 on success
	def glClear(self):

		first = True
		pixel = self.rgbToByte(self.clearRgbRed, self.clearRgbGreen, self.clearRgbBlue)

		for y in range(self.height):

			if (first):
				data = pixel * self.width
				first = False
			else:
				data += pixel * self.width

			# padding for each line
			for x in range(self.row_padding):
				data += bytes('\x00', 'utf-8')

		self.image_data = self.image_data[:27] + data

		return 0

	#Define glClearColor(float, float, float). It change the colors used for the glClear
	# returns: 0 on success
	def glClearColor(self,r,g,b):

		# the rgb data for glClear is store after converting the rgb numbers from float to integers
		# on a scale from 0 to 255
		self.clearRgbRed = int(math.ceil(float(r/1)*255))
		self.clearRgbGreen = int(math.ceil(float(g/1)*255))
		self.clearRgbBlue = int(math.ceil(float(b/1)*255))

		return 0


	# Define glColor(float, float, float). It change the colors used for painting a specific pixel
	# returns: 0 on success
	def glColor(self,r,g,b):

		# the rgb data for the pixel painting is store after converting the rgb numbers from float
		# to integers on a scale from 0 to 255
		self.paintRgbRed = int(math.ceil(float(r/1)*255))
		self.paintRgbGreen = int(math.ceil(float(g/1)*255))
		self.paintRgbBlue = int(math.ceil(float(b/1)*255))

		return 0

	def glLoadTextureImage(self, texture, scale_X, scale_Y):
		image = open(texture + '.bmp', "rb")

		image.seek(10)
		header_size = struct.unpack("=l", image.read(4))[0]
		image.seek(18)

		self.texture_width = struct.unpack("=l", image.read(4))[0]
		self.texture_height = struct.unpack("=l", image.read(4))[0]
		self.texture_width_ratio = (self.texture_width/self.width)/scale_X
		self.texture_height_ratio = (self.texture_height/self.height)/scale_Y
		self.textureImg = []
		image.seek(header_size)
		for y in range(self.texture_height):
			self.textureImg.append([])
			for x in range(self.texture_width):
				b = ord(image.read(1))
				g = ord(image.read(1))
				r = ord(image.read(1))
				self.textureImg[y].append(self.rgbToByte(r,g,b))

		image.close()

		return 0

	def glObjMover(self, vertices, scale, translateX, translateY):

		new_vertices = []

		# transform np
		scale_it = np.matrix([
		    [scale,0,0],
		    [0,scale,0],
		    [0,0,1]
		])

		for vertice in vertices:
			vertice = np.matmul(scale_it,vertice)
			vertice = np.sum([vertice,[translateX,translateY,0]],axis=0)

			new_vertices.append([vertice.item(0),vertice.item(1),vertice.item(2)])

		return new_vertices

	def glObjRotate(self,vertices,angle):

		new_vertices = []

		# transform np
		rotate_it = np.matrix([
		  [np.cos(angle),  -np.sin(angle), 0],
		  [np.sin(angle),  np.cos(angle), 0],
		  [0.01, 0.001, 1]
		])

		for vertice in vertices:

			vertice = np.matmul(rotate_it,vertice)
			new_vertices.append([vertice.item(0),vertice.item(1),vertice.item(2)])

		return new_vertices


	def glObjReader(self, objectName):

		# opens obj file
		file = open(objectName + '.obj')
		lines = file.read().splitlines()

		# vertices and faces
		vertices = []
		textures = []
		faces = []

		# reads each line and stores each vertice and face
		for line in lines:

			# gets the prefix and the values of either a vertice or a face
			try:
				prefix, value = line.split(' ',1)
			except ValueError:
				continue

			# reads and store vertices
			if prefix == 'v':
				try:
					vertices.append(list(map(float, value.split(' '))))
				except ValueError:
					break

			# reads and store vertices
			if prefix == 'vt':
				try:
					textures.append(list(map(float, value.split(' '))))
				except ValueError:
					break

			# reads and store faces
			elif prefix == 'f':
				section = []
				for face in value.split(' '):
					try:
						section.append(list(map(int, face.split('/'))))
					except ValueError:
						try:
							section.append(list(map(int, face.split('//'))))
						except ValueError:
							break
				faces.append(section)

		# 2D list to return with the vertices and faces
		object_skeleton = [vertices,faces,textures]

		return object_skeleton


	# Define glObjWriter(). Makes BMP out of a flat .obj
	# Return 0 on success
	def glObjWriter(self,object_skeleton,scale,translate_x, translate_y,angle = 0):

		# vertices and faces
		vertices = self.glObjMover(object_skeleton[0],1/scale,translate_x,translate_y)
		if angle != 0:
			vertices = self.glObjRotate(vertices,angle)

		faces = object_skeleton[1]
		textures = object_skeleton[2]

		# counter
		counter = 0

		# draws each face of the object
		for face in faces:

			counter += 1
			if counter%50 == 0:
				sys.stdout.write('\r' + str(counter/len(faces)*100)[0:4] + "% complete")

			pollygon = []
			texturesToPaint = []
			z_avg = 0
			paint_pol = True

			# gets all the vertices in a face
			for i in range(len(face)):
				x = int((vertices[face[i][0]-1][0])*self.width)
				y = int((vertices[face[i][0]-1][1])*self.height)
				z = int(vertices[face[i][0]-1][2])

				tex_X = textures[face[i][1]-1][0]
				tex_Y = textures[face[i][1]-1][1]

				z_avg += z

				texturesToPaint.append([tex_X,tex_Y])
				pollygon.append([x,y])

				if x >= self.width or y >= self.height:
					paint_pol = False

				if x < 0 or y < 0:
					paint_pol = False

			# avarage  cooordinate
			z_avg = z_avg/len(face)

			# paints the face
			if paint_pol:
				self.glPolygonMaker(pollygon,texturesToPaint,z_avg)

		sys.stdout.write('\r' + "100% complete   ")

		return 0

	# Define glPolygonMaker(). Paints a figure given the vertices in a list.
	# returns: 0 on success
	def glPolygonMaker(self, vertices, textures, z_coordinate):

		# lista para guardar los puntos de la figura
		figurePoints = []

		# se reutiliza el codigo para hacer lineas solo que se guarda cada punto
		# que se pinta en figurePoints
		for i in range(len(vertices)):

			xi = vertices[i][0]
			yi = vertices[i][1]

			if i == len(vertices)-1:
				xf = vertices[0][0]
				yf = vertices[0][1]

			else:
				xf = vertices[i+1][0]
				yf = vertices[i+1][1]

			dy = yf - yi
			dx = xf - xi

			if (dx == 0):
				if dy > 0:
					for y in range(dy + 1):
						figurePoints.append([xi,y + yi])
						if z_coordinate >= self.z_buffer[xi][y+yi]:
							self.z_buffer[xi][y+yi] = z_coordinate
				else:
					for y in range(abs(dy) + 1):
						figurePoints.append([xi,y + yf])
						if z_coordinate >= self.z_buffer[xi][y+yf]:
							self.z_buffer[xi][y+yf] = z_coordinate
			else:
				m = dy/dx
				grad = m <= 1 and m >= 0

				if grad and xi > xf:
					xi, xf = xf, xi
					yi, yf = yf, yi
					dy = yf - yi
					dx = xf - xi
					m = dy/dx
					grad = m <= 1 and m >= 0

				elif yi > yf:
					xi, xf = xf, xi
					yi, yf = yf, yi
					dy = yf - yi
					dx = xf - xi
					m = dy/dx
					grad = m <= 1 and m >= 0

				if (grad):
					for x in range(dx + 1):
						y = round(m*x + yi)
						figurePoints.append([x+xi,y])
						if z_coordinate >= self.z_buffer[x+xi][y]:
							self.z_buffer[x+xi][y] = z_coordinate
				else:
					m = 1/m
					for y in range(dy + 1):
						x = round(m*y + xi)
						figurePoints.append([x,y + yi])
						if z_coordinate >= self.z_buffer[x][y+yi]:
							self.z_buffer[x][y+yi] = z_coordinate


		# avoids processing the same point twice.
		avoidPoints = []
		counter_for_tex_Y = 0

		for point in figurePoints:

			if (int(textures[0][1]*self.texture_height)-1 + counter_for_tex_Y) > self.texture_height:
				counter_for_tex_Y -= self.texture_height_ratio

			if point[1] not in avoidPoints:

				# finds which points are in the same y coordinate in the figure.
				pointsToPaint = []
				for i in range(len(figurePoints)):
					if figurePoints[i][1] == point[1]:
						pointsToPaint.append(figurePoints[i][0])


				# order the points
				pointsToPaint.sort()
				pointsLen = len(pointsToPaint)

				counter_for_tex_X = 0

				if pointsLen != 0:
					for xToDraw in range(pointsToPaint[0],pointsToPaint[pointsLen-1]+1):
						if z_coordinate >= self.z_buffer[xToDraw][point[1]]:

							if (int(textures[0][1]*self.texture_width)-1 + counter_for_tex_X) > self.texture_width:
								counter_for_tex_X -= self.texture_width_ratio

							self.glAbsolutePointWithColor(xToDraw,point[1], \
							self.textureImg[int(textures[0][1]*self.texture_height + counter_for_tex_Y)-1][int(textures[0][0]*self.texture_width + counter_for_tex_X)])
							self.z_buffer[xToDraw][point[1]] = z_coordinate
						counter_for_tex_X += self.texture_width_ratio

				avoidPoints.append(point[1])

			counter_for_tex_Y += self.texture_height_ratio

		return 0

	# Define glVertex(int, int). Paints an individual pixel
	# returns: 0 on success
	def glVertex(self,x, y):

		# painting cordinates
		pcx = self.vp_x + x
		pcy = self.vp_y + y

		# changes the data of an individual pixel
		data = self.image_data[:26 + ((pcy - 1) * (self.width + self.row_padding) + (pcx - 1)) * 4]
		data += self.rgbToByte(self.paintRgbRed, self.paintRgbGreen, self.paintRgbBlue)
		data += self.image_data[30 + ((pcy - 1) * (self.width + self.row_padding) + (pcx - 1)) * 4:]

		self.image_data = data

		return 0

	# Define glColor(). Paint the whole viewport
	# returns: 0 on success
	def glVertexPaintVp(self):

		for y in range(self.vp_height):
			for x in range(self.vp_width):
				self.glVertex(x,y)

		return 0

	# Define glViewPort(int, int, int, int). Establish an area of work for the painting process
	# returns: 0 on success
	def glViewPort(self, viewport_x, viewport_y, viewport_width, viewport_height):

		self.vp_x = viewport_x
		self.vp_y = viewport_y
		self.vp_width = viewport_width
		self.vp_height = viewport_height

		return 0

	# Define rgbToByte(int, int, int). Converts RGB to bytes
	# returns: 4 bytes indicating the RGB of a pixel
	def rgbToByte(self, r,g,b):
		data = struct.pack('B', b)
		data += struct.pack('B', g)
		data += struct.pack('B', r)
		data += struct.pack('B', 0)

		return data

	# Define finish(). Takes the image_data and makes a file out of it with
	# a specif name
	# returns: 0 on success
	def writeImage(self, fileName):

		# Makes the image file
		img = open(fileName + ".bmp", 'wb')
		img.write(self.image_data)

		return 0

	def get_bmp_processor_info(self):
		return "bmp_processor Version B"

	def get_header_info(self):
		return [self.width, self.height,self.bits_per_pixel, self.row_bytes, self.row_padding]

	def get_viewport_info(self):
		return [slef.viewport_x, self.viewport_y, self.viewport_width, self.viewport_height]

	def get_clearColors_info(self):
		return [self.clearRgbRed, self.clearRgbGreen, self.clearRgbBlue]

	def get_paintColors_info(self):
		return [self.paintRgbRed, self.paintRgbGreen, self.paintRgbBlue]
