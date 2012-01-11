import sys, os, time, math
from types import StringType, TupleType, ListType, IntType, ClassType
from os import path
import itertools
from itertools import izip, imap
import dircache

import math
from math import fabs
import Numeric as np
import RandomArray as ra
import LinearAlgebra as la
import scipy

RadPerDeg = math.pi / 180
DegPerRad = 180 / math.pi

class error                          (Exception)    : pass

class QubAlignment3Point(object):

	def __init__(self, eps=1e-3):
		self.__eps = eps

	def __epsEqual(self, x, y):
		return math.fabs(x-y) < self.__eps 

	def __epsGreater(self, x, y, eps=1e-3):
		return (not (math.fabs(x-y) < self.__eps)) and x > y

	def __epsSmaller(self, x, y):
		return (not (math.fabs(x-y) < self.__eps)) and x < y

	def tripleProjectionToFocus(self, z, phi, degflg=False):
		#%
		#% in the following column vectors [x0, x1, x2]' will be
		#% denoted as [xi]
		#% Assuming we want to center a sample mounted on a
		#% horizontal phi axis pointing in y direction.
		#% phi is turning in the mathematical positive sense.
		#% In fact as we look at the projection te sense of phi is
		#% irrelevant - there is a consistent solution for both
		#% possibilities (as long as we are not correcting in x).
		#% We have x y z translations in order to moce the phi-axis
		#% named phix, phiy, phiz. The phi-axis is well aligned with y
		#% The sample is roughly centered and is well aligned along y. 
		#% At three different  phi positions
		#%     phi = [phii]
		#% we had to move z by
		#%     z   = [zi]
		#% let alpha be the angle between the x-axis and aline
		#% through the ssample position r = [ri] and the real
		#% centre of rotation. So an adjustment zi = 0
		#% alpha would be either 0 or pi
		#% If we knew phi = phia for alpha = 0 and the
		#% radius of missalignment R we could compute the
		#% zk adjustments for any angle phi according to
		#% zk(phi) = R*sin(phi-phia)
		#% We could perform a data collection doing a slight
		#% z adjustment for oscillation intervall
		#%

		if degflg:
			phi = RadPerDeg*np.array(phi)

		ph = (ph1, ph2) = (phi[1]-phi[0], phi[2]-phi[0])
		print ph

		s = (s1,s2) = (np.sin(ph1), np.sin(ph2))
		c = (c1,c2) = (np.cos(ph1), np.cos(ph2))
		d = (d1,d2) = (c1-1, c2-1)

		dz = (dz1,dz2) = (z[1]-z[0], z[2]-z[0])
		absdz = (absdz1, absdz2)  = (fabs(dz1), fabs(dz2))
		if absdz1 > absdz2:
			dzIndex = 0
		else:
			dzIndex = 1
		if self.__epsEqual(absdz[dzIndex], 0):
			raise error('at least one z difference has to be significant')

		i = dzIndex
		j = 1-dzIndex

		q = dz[j]/dz[i]

		numerator   = s[j] -q*s[i]
		denominator = q*d[i] - d[j]
		if fabs(numerator) <= fabs(denominator):
			print 'tan'
			alpha0 = np.arctan(numerator/denominator)
		else:
			print 'cot'
			alpha0 = 0.5*math.pi - np.arctan(denominator/numerator)
		R = dz[i]/(np.sin(ph[i]+alpha0) - np.sin(alpha0))
		if R < 0:
			print 'R < 0', R
			alpha0 = alpha0 - math.pi
		else:
			print 'R > 0'
		R = dz[i]/(np.sin(ph[i]+alpha0) - np.sin(alpha0))
 		print 'alpha0 = ', alpha0*DegPerRad, R
		return (R, phi[0] - alpha0)

if __name__ == '__main__':
	x = QubAlignment3Point(eps=1e-4)
	z = np.array([0,6/math.sqrt(2),6])
	phi = np.array([math.pi/2,3*math.pi/4,math.pi])
	
	print x.tripleProjectionToFocus(z, phi)
