import traceback
import sys

class Guard(object):
	'''
	Class of exception catching and printing objects.

	>>> with Guard():
	...     print "This code is okay"
	This code is okay
	>>> with Guard(print_traceback=False):
	... 	print "This code is bad"[""] # doctest: +ELLIPSIS
	Traceback <traceback object at ...> caught by <ejtp.util.crashnicely.Guard object at ...>
	>>> with Guard(print_catch=False):
	... 	print "This code is bad"[""] # doctest: +IGNORE_EXCEPTION_DETAIL
	Traceback (most recent call last):
	TypeError: string indices must be integers, not str
	'''
	def __init__(self, print_catch=True, print_traceback=True):
		# Workaround for doctest being dumb, will fix better later
		self.print_catch = print_catch 
		self.print_traceback = print_traceback

	def __enter__(self):
		pass

	def __exit__(self, exc_type, exc_value, exc_traceback):
		if not exc_traceback:
			return True
		if self.print_catch:
			print "Traceback",exc_traceback,"caught by", self
		if self.print_traceback:
			traceback.print_exception(exc_type, exc_value, exc_traceback)
		return True
