#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 13:46:34 2019

@author: aviallon
"""

DEFAULT_WIDTH = 4

class Warning:
	def __init__(self, message):
		import sys
		print(f"{self.__class__.__name__} : {message}", file=sys.stderr)
		
class OverflowWarning(Warning):
	pass

class WrongInputNumber(Exception):
	"""
	Raised when there is not enough inputs for a block/logic gate
	"""
	pass

def toBin(a, width=DEFAULT_WIDTH):
	if type(a) == tuple or type(a) == list:
		return ("".join([str(int(x)) for x in a])).zfill(len(a))
	elif type(a) == int:
		negative = a < 0
		abin = bin(a)[2+negative:].zfill(width)
		#print(abin)
		if negative:
			index_last_1 = -("".join(reversed(abin))).index("1")-1
			abin_invert = "".join([str(int(not(int(x)))) for x in abin[:index_last_1]]) + abin[index_last_1:]
			#print(abin, abin_invert)
			return abin_invert
		else:
			return abin
	else:
		raise NotImplementedError(f"Can't convert {str(type(a))} to binary string !")

def toInt(a: (bool, ), signed=False):
	if not(signed) or a[0] == 0:
		return int(toBin(a), 2)
	else:
		return -int(toBin(INVERT(a)[0]), 2)

def toBinTuple(a, width=DEFAULT_WIDTH):
	return [bool(int(x)) for x in toBin(a, width)]

class Logic:
	
	def __call__(self, *args) -> bool:
		pass
	
	def __repr__(self):
		if hasattr(self, 'name'):
			return f'{self.name}'
		else:
			return f'{self.__class__.__name__}()'

class AndGate(Logic):
	
	def __call__(self, *args) -> bool:
		if len(args) != 2:
			raise WrongInputNumber(f"Expected 2 inputs, got {len(args)}")
		
		return args[0] & args[1]
	
class OrGate(Logic):
	
	def __call__(self, *args) -> bool:
		if len(args) != 2:
			raise WrongInputNumber(f"Expected 2 inputs, got {len(args)}")
		
		return args[0] | args[1]
	
class XorGate(Logic):
	
	def __call__(self, *args) -> bool:
		if len(args) != 2:
			raise WrongInputNumber(f"Expected 2 inputs, got {len(args)}")
		
		return args[0] ^ args[1]
	
class NotGate(Logic):
	
	def __call__(self,*args) -> bool:
		if len(args) != 1:
			raise WrongInputNumber(f"Expected one input, got {len(args)}")
		
		return not(args[0])
	
class NandGate(Logic):
	
	def __call__(self,*args) -> bool:
		if len(args) != 2:
			raise WrongInputNumber(f"Expected 2 input, got {len(args)}")
		
		return not(args[0] & args[1])
	

XOR = XorGate()
AND = AndGate()
OR = OrGate()
NAND = NandGate()
NOT = NotGate()
	
class FullAdder(Logic):
	
	def __call__(self, a, b, carry = 0) -> bool:
		
		firstXor = XOR(a, b) 
		s = XOR(firstXor, carry)
		passCarry = AND(firstXor, carry)
		newCarry = AND(a, b)
		cout = OR(passCarry, newCarry)
		
		return s, cout
	
fulladder = FullAdder()

class RippleCarryAdder(Logic):
	def __init__(self, width=DEFAULT_WIDTH, warning=True):
		self.width = width
		self.name = f"RippleCarryAdder({width})"
		self.warning = warning
		
	def __call__(self, a: (bool, ), b: (bool, )) -> (bool, ):
		a, b = list(a), list(b)
		if len(a) != len(b) or len(a) != self.width:
			raise Exception(f"Expected {self.width}-bit input (got {len(a)} bits)")
			
			
		i = len(a)
		c = [0]*self.width
		cout = 0
		while i > 0:
			i -= 1
			c[i], cout = fulladder(a[i], b[i], cout)
			
		if cout and self.warning:
			OverflowWarning(f"The sum of {toBin(a)} and {toBin(b)} is greater than {2**self.width-1}")
			
		return tuple(c), cout
	
ADD = RippleCarryAdder(DEFAULT_WIDTH)

class Invert(Logic):
	
	def __call__(self, a) -> (bool, ):
		c = [not(x) for x in a]
		sign = c[0]
		c, cout = ADD(c, toBinTuple(1, len(a)))
		overflow = OR(XOR(sign, c[0]), cout)
		
		if overflow:
			OverflowWarning(f"signed integer {toBin(a)} overflowed while inverting !")
		return c, overflow
	
INVERT = Invert()

class Substract(Logic):
	def __init__(self, width=DEFAULT_WIDTH):
		self.width = width
		self.ADD = RippleCarryAdder(width, False)
	
	def __call__(self, a, b):

		minus_b, overflow = INVERT(b)
		add_a_minus_b, overflow2 = self.ADD(a, minus_b)
		return add_a_minus_b, overflow
	
SUB = Substract(DEFAULT_WIDTH)