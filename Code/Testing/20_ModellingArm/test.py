# https://www.hackster.io/Samuel_Jasmer/robotic-arm-and-3d-modeling-cb0e05

import serial
import time
import sys
import math
import pygame
import numpy
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

RobotAttached = 0


#Initialize Serial Port (On uart0)
if RobotAttached:
  port = serial.Serial("/dev/ttyS0",baudrate=9600,timeout=1)

#Map function variables
in_min=0
in_max=1024
out_min=0
out_max=90








def axes():
	axesVerticies=(
		(0,0,0),
		(50,0,0),
		(0,50,0),
		(0,0,50),
		(50,50,0),
		(0,50,50),
		(50,0,50)	
		)
	axesEdges= (
		(0,1),
		(0,2),
		(0,3),
		(1,4),
		(1,6),
		(2,4),
		(2,5),
		(3,5),
		(3,6)
		)
	axesSurfaces= (
		(0,1,6,3),
		(0,1,4,2),
		(0,2,5,3)
		)
	axesColors = (
		(1,.5,.5),#red
		(.5,1,.5),#green
		(.5,.5,1),#blue
		(1,.5,.5),
		(.5,1,.5),
		(.5,.5,1),
		(1,.5,.5),
		(.5,1,.5),
		(.5,.5,1),
		(1,.5,.5),
		(.5,1,.5),
		(.5,.5,1)
		)

	glBegin(GL_QUADS)
	
	i=0
	for surface in axesSurfaces:
		i+=1
		glColor3fv(axesColors[i])
		#Color the different surfaces red, blue, and green
		for vertex in surface:
			glVertex3fv(axesVerticies[vertex])
				
	glEnd()


	#Build Axes
	glBegin(GL_LINES)
	for edge in axesEdges:
		for vertex in edge:
			glVertex3fv(axesVerticies[vertex])	
	glEnd()








	
def radius(a):
	radiusVerticies= (
		(0,0,0),
		(0,3,0),
		(20,0,0),
		(20,5,0),
		(0,0,.5),
		(0,3,.5),
		(20,0,.5),
		(20,5,.5)
		)
	radiusEdges= (
		(0,1),
		(0,2),
		(0,4),
		(1,3),
		(1,5),
		(2,3),
		(2,6),
		(3,7),
		(4,5),
		(4,6),
		(5,7),
		(6,7)
		)
	radiusSurfaces= (
		(0,1,2,3),
		(4,5,6,7),
		(0,1,4,5),
		(2,3,6,7),
		(0,2,4,6),
		(1,3,5,7)
		)
	
	glRotatef(90,0,0,1)#Position the Radius Vertically
	glRotatef(90,1,0,0)
	glTranslatef(25,25,25)#Move to center
	
	glRotate(-a,0,0,-1)#Rotate Radius by a, a is changed on keypress
	glTranslatef(-20,0,0)#Keep the Radius the same distance away after rotation


	glBegin(GL_QUADS)

	for surface in radiusSurfaces:
		glColor3fv((1,1,1))#Color the Radius White

	glEnd()

	#Build the Radius
	glBegin(GL_LINES)
	for edge in radiusEdges:
		for vertex in edge:
			glVertex3fv(radiusVerticies[vertex])
	glEnd()






def humerus(a,b,c):
	humerusVerticies= (
		(0,0,0),
		(0,5,0),
		(25,-1,0),
		(25,6,0),
		(0,0,.5),
		(0,5,.5),
		(25,-1,.5),
		(25,6,.5)
		)
	humerusEdges= (
		(0,1),
		(0,2),
		(0,4),
		(1,3),
		(1,5),
		(2,3),
		(2,6),	
		(3,7),
		(4,5),
		(4,6),
		(5,7),
		(6,7)
		)
	humerusSurfaces= (
		(0,1,2,3),
		(4,5,6,7),
		(0,1,4,5),
		(2,3,6,7),
		(0,2,4,6),
		(1,3,5,7)
	  )
	
	#Position the Humerus Vertically
	glRotatef(90,0,0,1)
	glRotatef(90,1,0,0)
	glTranslatef(0,-2.5,-0.25)
	glRotatef(b,0,0,1)
	#glTranslatef(25,25,25)
	
	
	glBegin(GL_QUADS)

	for surface in humerusSurfaces:
		glColor3fv((1,1,1))#Color the Humerus White

	glEnd()

	#Build the Humerus
	glBegin(GL_LINES)

	for edge in humerusEdges:
		for vertex in edge:
			glVertex3fv(humerusVerticies[vertex])
	glEnd()
	
	radius(a)







def map(rcv,in_min,in_max,out_min,out_max):
	#This function is from the arduino. It maps the values
	#of one input, onto a different range, creating the output
	return(rcv-in_min*(out_max-out_min)/(in_max-in_min)+out_min)







def serialInput():
	#This function reads the serial port, uart0
	#It then processes the data into a usable variable
	#by the radius function
	
	#This Function is broken and does not work currently
	rcv = port.readline()
	int(rcv)
	a = map(rcv,in_min,in_max,out_min,out_max)
	return(a)

	
	
	
	
	
def text(x,y,z):
	#Print out the position of the camera
	#Rotation isn't implemented, so it won't be accurate
	print("Position:",x,y,z)
	sys.stdout.write("\033[F")






def updateViewport(event):
	#TRANSLATE
	if event.key == pygame.K_LEFT:
		glTranslatef(5,0,0)
		x+=5
	if event.key == pygame.K_RIGHT:
		glTranslatef(-5,0,0)
		x-=5
	if event.key == pygame.K_UP:
		glTranslatef(0,-5,0)
		y+=5
	if event.key == pygame.K_DOWN:
		glTranslatef(0,5,0)
		y-=5
	if event.key == pygame.K_j:
		glTranslatef(0,0,-5)
		z+=5
	if event.key == pygame.K_l:
		glTranslatef(0,0,5)
		z-=5
	#ROTATE
	if event.key == pygame.K_a:
		glRotate(5,0,1,0)
	if event.key == pygame.K_d:
		glRotate(5,0,-1,0)
	if event.key == pygame.K_w:
		glRotate(5,-1,0,0)
	if event.key == pygame.K_s:
		glRotate(5,1,0,0)
	if event.key == pygame.K_i:
		glRotate(5,0,0,-1)
	if event.key == pygame.K_k:
		glRotate(5,0,0,1)






def main():
	#Build Pygame Window
	pygame.init()
	display = (800,800)
	pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
	
	gluPerspective(45, (display[0]/display[1]), 0.1, 300.0)
	
	#Set Camera Position
	glRotatef(-45,-1,0,0)#Rotate Camera down
	glRotatef(45,0,-1,0)#Rotate Camera turn
	glTranslatef(-100,-150,-100)#Translate the camera to the corner


#I had problems figuring out how to properly arrange these functions
#There order will effect their outcomes; Changing one value can
#have drastically different results.
#Rotating the camera first is important, because if you
#translate it first, the rotation after it is then multiplied
#with the translation, causing it to do things you wouldn't 
#expect.
	
	#Variables

	#Radius Angle
	a=0
	b=0
	c=0

	
	#Infinite while loop
	while True:
		#Event Handling loop
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
				#Kill Window
		
			#updateViewport(event)
		
			#KEYEVENT KEYDOWN HANDLING
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_g:
					a+=5
				if event.key == pygame.K_h:
					a-=5
					
				if event.key == pygame.K_c:
					b+=5
				if event.key == pygame.K_t:
					b-=5
					
				if event.key == pygame.K_r:
					c+=5
				if event.key == pygame.K_n:
					c-=5
		
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

		#Get joystick input
		#serialInput()
	
		#Draw shapes
		axes()

		#glPushMatrix()
		#radius(a)
		#glPopMatrix()

		glPushMatrix()
		humerus(a,b,c)
		glPopMatrix()

		
		#text(x,y,z)

		pygame.display.flip()
		pygame.time.wait(10)
	

main()
