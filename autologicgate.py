#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 13:46:34 2019

@author: aviallon
"""

DEFAULT_WIDTH = 4

NULL = [0]*DEFAULT_WIDTH

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
	return [int(x) for x in toBin(a, width)]

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
			raise Exception(f"Expected {self.width}-bit input (got {len(a)} and {len(b)} bits)")
			
			
		i = len(a)
		c = [0]*self.width
		cout = 0
		while i > 0:
			i -= 1
			c[i], cout = fulladder(a[i], b[i], cout)
			
		if cout and self.warning:
			OverflowWarning(f"The sum of {toBin(a)} and {toBin(b)} is greater than {toBin(2**self.width-1)}")
			
		return tuple(c), cout
	
ADD = RippleCarryAdder(DEFAULT_WIDTH)

class Invert(Logic):
	
	def __init__(self, width=DEFAULT_WIDTH, warning=True):
		self.warning = warning
		self.width = width
		self.ADD = RippleCarryAdder(width, False)
	
	def __call__(self, a) -> (bool, ):
		c = [not(x) for x in a]
		sign = c[0]
		c, cout = self.ADD(c, toBinTuple(1, self.width))
		overflow = OR(XOR(sign, c[0]), cout)
		
		if overflow and self.warning:
			OverflowWarning(f"signed integer {toBin(a)} overflowed while inverting !")
		return c, overflow
	
INVERT = Invert()

class Substract(Logic):
	def __init__(self, width=DEFAULT_WIDTH, warning=True):
		self.width = width
		self.ADD = RippleCarryAdder(width, False)
		self.INVERT = Invert(width, False)
		self.warning = warning
	
	def __call__(self, a, b):
		
		check_underflow = AND(a[0], NOT(b[0]))
		minus_b, overflow = self.INVERT(b)
		add_a_minus_b, overflow2 = self.ADD(a, minus_b)
		underflow = AND(check_underflow, NOT(add_a_minus_b[0]))
		if underflow and self.warning:
			OverflowWarning(f"substraction of {toBin(a)} and {toBin(b)} underflowed")
		return add_a_minus_b, underflow
	
SUB = Substract(DEFAULT_WIDTH)

class LesserThan(Logic):
	def __init__(self, signed=False, width=DEFAULT_WIDTH):
		self.width = width
		self.SUB = Substract(width, False)
		#self.INVERT = Invert(width, False)
		
	def __call__(self, a, b):
		#print(a, b)
		a_minus_b, underflow = self.SUB(a, b)
		return OR(underflow, a_minus_b[0])
	
LESSER = LesserThan()
	
class Equal(Logic):
	def __init__(self, width=DEFAULT_WIDTH):
		self.width = width
		
	def __call__(self, a, b):
		for i in range(self.width):
			if XOR(a[i], b[i]):
				return 0
		return 1
	
EQUAL = Equal()

class LesserNotEqual(Logic):
	def __init__(self, width=DEFAULT_WIDTH):
		self.width = width
		self.SUB = Substract(width, False)
		
	def __call__(self, a, b):
		a_minus_b, underflow = self.SUB(a, b)
		return OR(underflow, AND(a_minus_b[0], NOT(EQUAL(a_minus_b, NULL))))
	
LESSNEQ = LesserNotEqual()

class ShiftLeft(Logic):
	def __init__(self, width=DEFAULT_WIDTH):
		self.width = width
		self.LESSER = LesserThan(width)
		
	def __call__(self, a, n):
		"""
		a : number to shift
		n : shift by how much. Should be int(log2(a)) bit long
		"""
		c = list(a)
		
		while NOT(self.LESSER(n, [0]*self.width)):
			i = 0
			while i < self.width-1:
				c[i] = c[i+1]
				i += 1
				
			n = SUB(n, toBinTuple(1, self.width))[0]
			print("N = ", n)
				
		if a[0]:
			OverflowWarning(f"Bit shift to the left overflowed")
				
		return c, a[0]
	
SHIFTL = ShiftLeft()

class TruthTable:
	def __init__(self, inputs=[(1,), (0, )], outputs=[(0,), (1, )]):
		self.inputs = inputs
		self.outputs = outputs
		
	def __call__(self, inputs):
		if inputs in self.inputs:
			return self.outputs[self.inputs.index(inputs)]
		else:
			raise ValueError('Input not in truth table !')
			
