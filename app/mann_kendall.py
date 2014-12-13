'''
__author__ 	= Ryan Stephany
__date__ 	= 31Oct2014
__description__
	Mann-Kendall test for increasing or decreasing trends in timeseries

The code is written from the article at the following url
http://vsp.pnnl.gov/help/Vsample/Design_Trend_Mann_Kendall.htm
'''


from __future__ import division
import math
import numpy as np
from scipy.stats import norm


class MannKendall (object):
	'''
	Class for testing timeseries data for temporal trends
	'''
	def __init__ (self, timeseries, alpha=0.5):
		self.timeseries = timeseries
		self.alpha		= alpha
		self.n 			= len(self.timeseries)
		self.S 			= 0
		self.var_S 		= 0
		self.unique		= np.unique(timeseries)
		self.un			= len(np.unique(timeseries)) 


	def _set_S (self):
		for k in xrange(self.n-1):
			for j in xrange(k+1,self.n):
				self.S += np.sign(self.timeseries[j] - self.timeseries[k])

	def _computer_var_S (self):
		var_s = (self.n*(self.n-1)*(2*self.n+5))
		if self.n ==  self.un:
			self.var_S = (var_s)/18.0
		else:
			tp = np.zeros(self.un)
			for t in xrange(self.un):
				tp[t] = np.sum(self.unique[t] == self.timeseries)

			self.var_S = (var_s - np.sum(tp*(tp-1)*(2*tp+5)))/18.0



	def test (self):
		if self.n > 10:
			self._set_S()
			self._computer_var_S()

			if self.S > 0:
				z = (self.S - 1)/np.sqrt(self.var_S)
			elif self.S == 0:
				z = 0
			elif self.S < 0:
				z = (self.S + 1)/np.sqrt(self.var_S)
		    
		    # calculate the p_value
			p = 2*(1-norm.cdf(abs(z)))
			h = abs(z) > norm.ppf(1-self.alpha/2)
			if h:
				if z >= norm.ppf(1-self.alpha):
					m='+'
				elif z <= norm.ppf(1-self.alpha):
					m='-'
			else:
				m=None
			return h,m,p
		else:
			print 'Test can only be run on a series of more than 10'
			return None,None,None





if __name__ == '__main__':
	import matplotlib.pyplot as plt
	ts = np.random.randint(1,10,size=12)
	print ts
	mk = MannKendall(ts, alpha=0.5)
	h,m,p =mk.test()
	print h,m,p
	plt.plot(ts)
	plt.show()

