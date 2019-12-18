#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 13:46:34 2019

@author: aviallon
"""
import math

DEFAULT_WIDTH = 4

NULL = [0]*DEFAULT_WIDTH

BIAS = 1e-8

class Warning:
	def __init__(self, message):
		import sys
		print(f"\033[1;33m{self.__class__.__name__}:\033[0m {message}", file=sys.stderr)
		
class OverflowWarning(Warning):
	pass

class UnderflowWarning(Warning):
	pass

class WrongInputNumber(Exception):
	"""
	Raised when there is not enough inputs for a block/logic gate
	"""
	pass

class Byte:
	def copy(self):
		b = Byte(NULL)
		b.__dict__ = self.__dict__.copy()
		b.bin = self.bin[:]
		return b
	
	def __init__(self, a, width=DEFAULT_WIDTH, signed=False):
		self.bin = [0]*width
		self.width = width
		self.signed = signed
		self.setByte(a)
		
	def setByte(self, a):
		if type(a) == Byte:
			#print("Got called !")
			self.__dict__ = a.__dict__.copy()
			self.bin = a.bin[:]
		elif type(a) == tuple or type(a) == list:
			self.bin = [0]*(self.width-len(a))+list(a)
		elif type(a) == str:
			self.bin = [0]*(self.width-len(a))+[int(x) for x in a]
		elif type(a) == int:
			negative = a < 0
			if negative:
				self.signed = True
			if a >= 2**self.width:
				OverflowWarning(f"converting {a} to uint{self.width} overflowed (max is {2**self.width-1}) !")
			if self.signed:
				if a > 2**(self.width-1)-1:
					OverflowWarning(f"converting {a} to signed int{self.width} overflowed (max is {2**(self.width-1)-1}) !")
				if a < -2**(self.width-1):
					UnderflowWarning(f"converting {a} to signed int{self.width} underflowed (min is -{2**(self.width-1)}) !")
			abin = bin(a)[2+negative:].zfill(self.width)[:self.width]
			abin = [int(x) for x in abin]
			if negative:
				index_last_1 = -(list(reversed(abin)).index(1))-1
				self.bin = ([(int(not(int(x)))) for x in abin[:index_last_1]] + abin[index_last_1:])
				#self.bin = (-Byte(abin)).bin
				#index_last_1 = -("".join(reversed(abin))).index("1")-1
				#abin_invert = [(int(not(int(x)))) for x in abin[:index_last_1]] + abin[index_last_1:]
				#print(abin, abin_invert)
				#self.bin = abin_invert
			else:
				self.bin = abin
		elif type(a) == float:
			if math.isnan(a):
				self.bin =  [0, 1, 1, 1, 1, 1, 0, 0]
				return
			negative = int(a < 0)
			a = abs(a)
			if not(math.isfinite(a)) or a > 15360:
				self.bin = [negative, 1, 1, 1, 1, 0, 0, 0]
				return
			if a == 0:
				self.bin = [0]*8
				return
			exponent = [0, 0, 0, 0]
			mantissa = [0, 0, 0]
			
			exp = math.floor(math.log2(a))
			if exp < 0:
				
				if exp == -1:
					mantissa[0] = 1
					exp = math.floor(math.log2(a - 2**exp + BIAS))
				if exp == -2:
					mantissa[1] = 1
					#print(exp, a - 2**exp)
					exp = math.floor(math.log2(a - 2**exp + BIAS))
				if exp == -3:
					mantissa[2] = 1
					
				self.bin = [negative] + exponent + mantissa
			else:
				exponent = Byte(exp + 1, width=4)
				mant = (a % 2**(exp)) / 2**exp
				exp = math.floor(math.log2(mant + BIAS))
				reste = mant - 2**exp
				if exp == -1:
					mantissa[0] = 1
					exp = math.floor(math.log2(reste + BIAS))
					reste = reste - 2**exp
				#print((mant - 2**exp))
				if exp == -2:
					mantissa[1] = 1
					
					#print(exp, a - 2**exp)
					#print(reste + BIAS)
					if reste > 0:
						exp = math.floor(math.log2(reste + BIAS))
						reste = reste - 2**exp
				if exp == -3:
					mantissa[2] = 1
				
				self.bin = [negative] + exponent.bin + mantissa
				
		else:
			raise NotImplementedError(f"Can't convert {str(type(a))} to Byte !")
			
	def __len__(self):
		return len(self.bin)
			
	def __getitem__(self, key):
		return self.bin[key]
	
	def __setitem__(self, key, val):
		self.bin[key] = val
		
	def __contains__(self, item):
		for i in range(len(self.bin)-len(item)+1):
			extract = self.bin[i:len(item)+i]
			#print(extract)
			if extract == item:
				return True
		return False
	
	def __neg__(self):
		b = self.copy()
		index_last_1 = -(list(reversed(b.bin)).index(1))-1
		b.bin = ([(int(not(int(x)))) for x in b.bin[:index_last_1]] + b.bin[index_last_1:])
		return b
			
	def __int__(self):
		if not(self.signed) or self.bin[0] == 0:
			return int(self.__str__(), 2)
		else:
			index_last_1 = -(list(reversed(self.bin)).index(1))-1
			absval = ([(int(not(int(x)))) for x in self.bin[:index_last_1]] + self.bin[index_last_1:])
			#if self.bin[0] == absval[0]:
			#	OverflowWarning(f"Overflow while converting {self.__str__()} to int !")
			return -int(Byte(absval).__str__(), 2)
		
	def __float__(self):
		if len(self.bin) == 8:
#		if len(a) != 8:
#			raise ValueError(f"a float8 (minifloat) must be 8-bit long (got {len(a)} bits !)")
			sign = self.bin[0]
			exponent = self.bin[1:1+4]
			mantra = self.bin[1+4:1+4+3]
			exponent_entier = int(Byte(exponent, 4))
			if sum(exponent) == 4:
				print(sum(exponent), sum(mantra))
				if sum(mantra) == 0:
					return (-1)**sign * math.inf
				else:
					return math.nan
			elif exponent_entier > 0:
				return float((-1)**sign * 2**(exponent_entier - 1) * (1 + mantra[0]*2**(-1) + mantra[1]*2**(-2) + mantra[2] * 2**(-3)))
			else:
				return float((-1)**sign * (mantra[0]*2**(-1) + mantra[1]*2**(-2) + mantra[2] * 2**(-3)))
			
		else:
			raise NotImplementedError(f"couldn't determine float type of {str(self)} automatically !")
			
	def __list__(self):
		return self.bin
	
	def __str__(self):
		return "".join([str(int(x)) for x in self.bin])
	
	def __repr__(self):
		return "Byte(["+",".join([str(int(x)) for x in self.bin])+f"], width={self.width}, signed={self.signed})"

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
	
	def __call__(self, a: int, b: int, carry = 0) -> bool:
		
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
		
	def __call__(self, a: Byte, b: Byte) -> (Byte, int):
		#a, b = list(a), list(b)
		if len(a) != len(b) or len(a) != self.width:
			raise Exception(f"Expected {self.width}-bit input (got {len(a)} and {len(b)} bits)")
			
			
		i = len(a)
		c = Byte(NULL, signed=OR(a.signed, b.signed))
		cout = 0
		while i > 0:
			i -= 1
			c[i], cout = fulladder(a[i], b[i], cout)
			
		if cout and self.warning:
			OverflowWarning(f"The sum of {str(Byte(a))} and {str(Byte(b))} is greater than {str(Byte(2**self.width-1))}")
			
		return c, cout
	
ADD = RippleCarryAdder(DEFAULT_WIDTH)

class Invert(Logic):
	
	def __init__(self, width=DEFAULT_WIDTH, warning=True):
		self.warning = warning
		self.width = width
		self.ADD = RippleCarryAdder(width, False)
	
	def __call__(self, a) -> (bool, ):
		c = Byte([NOT(x) for x in a], signed=a.signed)
		sign = c[0]
		c, cout = self.ADD(c, Byte(1, width=self.width))
		overflow = OR(XOR(sign, c[0]), cout)
		
		if overflow and self.warning:
			OverflowWarning(f"signed integer {str(Byte(a))} overflowed while inverting !")
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
			UnderflowWarning(f"substraction of {str(Byte(a))} and {str(Byte(b))} underflowed")
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
		#print("underflow ? ", underflow, "; A-B = ", a_minus_b)
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

class LesserOrEqual(Logic):
	def __init__(self, width=DEFAULT_WIDTH):
		self.width = width
		self.SUB = Substract(width, False)
		
	def __call__(self, a, b):
		a_minus_b, underflow = self.SUB(a, b)
		return OR(underflow, OR(a_minus_b[0], (EQUAL(a_minus_b, NULL))))
	
LESSEQ = LesserOrEqual()

class ShiftLeft(Logic):
	def __init__(self, width=DEFAULT_WIDTH):
		self.width = width
		self.LESSER = LesserThan(width)
		
	def __call__(self, a, n):
		"""
		a : number to shift
		n : shift by how much. Should be int(log2(a)) bit long
		"""
		c = a.copy()
		
		overflow = False
		
		while AND(
					NOT(self.LESSER(n, Byte(NULL))),
					NOT(EQUAL(n, Byte(NULL)))
				):
			i = 0
			
			if c[0]:
				overflow = True
			while i < self.width-1:
				c[i] = c[i+1]
				i += 1
			
			c[-1] = 0
			n = SUB(n, Byte(1, width=self.width))[0]
			#print("N = ", n)
			
		if overflow:
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
			
def plotFloat(bits=8):
	import numpy as np
	import matplotlib.pyplot as plt
	X = np.linspace(-1000, 1000, 100000)
	def _conv(x):
		return float(Byte(float(x), width=bits))
	conv = np.vectorize(_conv)
	Y = conv(X)
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(X, Y)
	ax.grid(True)
