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

global DEBUG
DEBUG = True

call_stack = []

class Warning:
	def __init__(self, message):
		import sys
		print(f"\033[1;33m{self.__class__.__name__}:\033[0m {message}", file=sys.stderr)
		
class OverflowWarning(Warning):
	pass

class UnderflowWarning(Warning):
	pass

class Debug(Warning):
	def __init__(self, *args):
		if DEBUG:
			super().__init__(" ".join([str(i) for i in args]))

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
	
	def __init__(self, a, width=0, signed=False):
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
			#Debug(f'self.width-len(a) = {self.width-len(a)}')
			self.bin = [0]*(self.width-len(a))+list(a)
		elif type(a) == str:
			self.bin = [0]*(self.width-len(a))+[int(x) for x in a]
		elif type(a) == int:
			if self.width == 0:
				self.width = DEFAULT_WIDTH
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
			
			exp = math.floor(math.log2(a)+0.5)
			if exp < 0:
				
				if exp == -1:
					mantissa[0] = 1
					exp = math.floor(math.log2(a - 2**exp + BIAS)+0.5)
				if exp == -2:
					mantissa[1] = 1
					#print(exp, a - 2**exp)
					exp = math.floor(math.log2(a - 2**exp + BIAS)+0.5)
				if exp == -3:
					mantissa[2] = 1
					
				self.bin = [negative] + exponent + mantissa
			else:
				exponent = Byte(exp + 1, width=4)
				mant = (a % 2**(exp)) / 2**exp
				exp = math.floor(math.log2(mant + BIAS) + 0.5)
				reste = mant - 2**exp
				if exp == -1:
					mantissa[0] = 1
					if reste > 0:
						exp = math.floor(math.log2(reste + BIAS) + 0.5)
						reste = reste - 2**exp
				#print((mant - 2**exp))
				if exp == -2:
					mantissa[1] = 1
					
					#print(exp, a - 2**exp)
					#print(reste + BIAS)
					if reste > 0:
						exp = math.floor(math.log2(reste + BIAS) + 0.5)
						reste = reste - 2**exp
				if exp == -3:
					mantissa[2] = 1
				
				self.bin = [negative] + exponent.bin + mantissa
				
		else:
			raise NotImplementedError(f"Can't convert {str(type(a))} to Byte !")
			
		self.width = len(self.bin)
			
	def isinf(self):
		sign_a, exp_a, mant_a = self.bin[0], self.bin[1:1+4], self.bin[1+4:]
		
		
		if sum(list(exp_a)) == 4:
			if sum(list(mant_a)) == 0:
				return True
				
		return False
	
	def isnan(self):
		sign_a, exp_a, mant_a = self.bin[0], self.bin[1:1+4], self.bin[1+4:]
				
		if sum(list(exp_a)) == 4:
			if sum(list(mant_a)) != 0:
				return True
				
		return False
			
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
		if b.isnan():
			return b
		if b.isinf():
			b[0] = int(not(b[0]))
			return b
		
			
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
			if self.isinf():
				return (-1)**sign * math.inf
			if self.isnan():
				return math.nan
			exponent = self.bin[1:1+4]
			mantra = self.bin[1+4:1+4+3]
			exponent_entier = int(Byte(exponent, 4))

			if exponent_entier > 0:
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
		call_stack.append(repr(self))
		pass
	
	def __repr__(self):
		if hasattr(self, 'name'):
			return f'{self.name}'
		else:
			widthinfo = ""
			if "width" in self.__dir__():
				widthinfo = f"width={self.width}"
			return f'{self.__class__.__name__}({widthinfo})'

class AndGate(Logic):
	
	def __call__(self, *args) -> bool:
		call_stack.append(repr(self))
		if len(args) != 2:
			raise WrongInputNumber(f"Expected 2 inputs, got {len(args)}")
		
		return args[0] & args[1]
	
class OrGate(Logic):
	
	def __call__(self, *args) -> bool:
		call_stack.append(repr(self))
		if len(args) != 2:
			raise WrongInputNumber(f"Expected 2 inputs, got {len(args)}")
		
		return args[0] | args[1]
	
class XorGate(Logic):
	
	def __call__(self, *args) -> bool:
		call_stack.append(repr(self))
		if len(args) != 2:
			raise WrongInputNumber(f"Expected 2 inputs, got {len(args)}")
		
		return args[0] ^ args[1]
	
class NotGate(Logic):
	
	def __call__(self,*args) -> bool:
		call_stack.append(repr(self))
		if len(args) != 1:
			raise WrongInputNumber(f"Expected one input, got {len(args)}")
		
		return not(args[0])
	
class NandGate(Logic):
	
	def __call__(self,*args) -> bool:
		call_stack.append(repr(self))
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
		#call_stack.append(repr(self))
		firstXor = XOR(a, b) 
		s = XOR(firstXor, carry)
		passCarry = AND(firstXor, carry)
		newCarry = AND(a, b)
		cout = OR(passCarry, newCarry)
		
		return s, cout
	
fulladder = FullAdder()

class RippleCarryAdder(Logic):
	def __init__(self, width=DEFAULT_WIDTH, warning=True):
		#call_stack.append(repr(self))
		self.width = width
		self.warning = warning
		
	def __call__(self, a: Byte, b: Byte) -> (Byte, int):
		#a, b = list(a), list(b)
		#print(a, b, a.width, b.width, len(a), len(b), self.width)
		if len(a) != len(b) or len(a) != self.width:
			raise Exception(f"Expected {self.width}-bit input (got {len(a)} and {len(b)} bits)")
			
			
		i = len(a)
		c = Byte(0, width=self.width, signed=OR(a.signed, b.signed))
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
		self.ADD = RippleCarryAdder(width=width, warning=False)
	
	def __call__(self, a) -> (bool, ):
		c = Byte([NOT(x) for x in a.bin], signed=a.signed)
		#Debug(f'c = {repr(c)}, {c}; a = {repr(a)}, {a.bin}')
		sign = c[0]
		#print(self.width, a, a.width)
		c, cout = self.ADD(c, Byte(1, width=self.width))
		overflow = OR(XOR(sign, c[0]), cout)
		
		if overflow and self.warning:
			OverflowWarning(f"signed integer {str(Byte(a))} overflowed while inverting !")
		return c, overflow
	
INVERT = Invert()

class Substract(Logic):
	def __init__(self, width=DEFAULT_WIDTH, warning=True):
		self.width = width
		self.ADD = RippleCarryAdder(width=width, warning=False)
		self.INVERT = Invert(width=width, warning=False)
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
		if signed:
			self.SUB = Substract(width=width, warning=False)
		else:
			self.SUB = Substract(width=width+1, warning=False)
			
		self.signed = signed
		#self.INVERT = Invert(width, False)
		
	def __call__(self, a, b):
		#print(a, b)
		if not(self.signed):
			a = Byte([0]+a.bin)
			b = Byte([0]+b.bin)
			
		a_minus_b, underflow = self.SUB(a, b)
		#print("underflow =", underflow, "; A-B = ", a_minus_b)
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
	def __init__(self, filler=0, width=DEFAULT_WIDTH, warning=True):
		self.width = width
		self.filler = 0
		self.warning = warning
		
	def __call__(self, a, n):
		"""
		a : number to shift
		n : shift by how much. Should be int(log2(a)) bit long
		"""
		c = a.copy()
		LESSER = LesserThan(width=n.width)
		NULL = Byte(0, n.width)
		EQUAL = Equal(width=n.width)
		SUB = Substract(width=n.width)
		
		overflow = False
		
		while AND(
					NOT(LESSER(n, NULL)),
					NOT(EQUAL(n, NULL))
				):
			i = 0
			
			if c[0]:
				overflow = True
			while i < self.width-1:
				c[i] = c[i+1]
				i += 1
			
			c[-1] = self.filler
			n = SUB(n, Byte(1, width=n.width))[0]
			#print("N = ", n)
			
		if overflow and self.warning:
			OverflowWarning(f"Bit shift to the left overflowed")
				
		return c, a[0]
	
SHIFTL = ShiftLeft()

class ShiftRight(Logic):
	def __init__(self, filler=0, width=DEFAULT_WIDTH, warning=True):
		self.width = width
		self.filler = filler
		self.warning = warning
		
	def __call__(self, a, n):
		"""
		a : number to shift
		n : shift by how much. Should be int(log2(a)) bit long
		"""
		#Debug(f'a = {repr(a)}, n = {repr(n)}, self.width={self.width}')
		LESSER = LesserThan(width=n.width)
		NULL = Byte(0, n.width)
		EQUAL = Equal(width=n.width)
		SUB = Substract(width=n.width)
		c = a.copy()
		
		underflow = False
		
		#n_gt_0 = NOT(LESSER(n, NULL))
		#n_not_0 = NOT(EQUAL(n, NULL))
		#print("NOT(EQUAL(n, NULL) =", NOT(EQUAL(n, NULL)), ", NOT(LESSER(n, NULL))", NOT(LESSER(n, NULL)), "int(n) =", int(n))
		#Debug(f"n_gt_0 = {n_gt_0}; n_not_0 = {n_not_0}")
		while AND(
					NOT(LESSER(n, NULL)),
					NOT(EQUAL(n, NULL))
				):
			i = self.width-1
			
			if c[-1]:
				underflow = True
			while i > 0:
				c[i] = c[i-1]
				i -= 1
			
			c[0] = self.filler
			
			n, _ = SUB(n, Byte(1, width=n.width))
			#n_gt_0 = NOT(LESSER(n, NULL))
			#n_not_0 = NOT(EQUAL(n, NULL))
			#print("N = ", n)
			
		if underflow and self.warning:
			UnderflowWarning(f"Bit shift to the right underflowed")
				
		return c, a[0]
	
SHIFTR = ShiftRight()
	
class Increment(Logic):
	def __init__(self, width=DEFAULT_WIDTH):
		self.width = width
		self.ADD = RippleCarryAdder(width=width, warning=False)
		
	def __call__(self, a):
		a.bin = self.ADD(a, Byte(1, self.width))[0].bin
	
class Absolute(Logic):
	def __init__(self, width=DEFAULT_WIDTH):
		self.width = width
		self.INVERT = Invert(width=width, warning=False)
		
	def __call__(self, a):
		if a[0] == 0:
			return a.copy()
		else:
			return self.INVERT(a)[0]
		
ABS = Absolute(DEFAULT_WIDTH)
	
class AddFloat2(Logic):
	
	def __init__(self, exp_len=4, mant_len=3):
		self.rounding_bits = 3
		self.expsize = exp_len
		self.mantsize = mant_len
		self.size = 1+exp_len+mant_len
		self.NULL_exp = Byte(0, exp_len)
		self.ONE_exp = Byte(1, exp_len)
		self.ONE_mant = Byte(1, mant_len+1+self.rounding_bits)
		self.NULL_mant = Byte(0, mant_len+1+self.rounding_bits)
		self.SHIFTR_mant = ShiftRight(width=mant_len+1+self.rounding_bits, warning=False)
		self.SHIFTR_mant_normal = ShiftRight(width=mant_len+1, warning=False)
		#self.SHIFTR_mant_onefill = ShiftRight(width=mant_len, filler=1)
		self.ADD_exp = RippleCarryAdder(width=exp_len, warning=False)
		self.ADD_mant = RippleCarryAdder(width=mant_len+1+self.rounding_bits, warning=False)
		self.ADD_mant_normal = RippleCarryAdder(width=mant_len+1, warning=False)
		self.LESSER_exp = LesserThan(signed=False, width=exp_len)
		self.SUB_exp = Substract(width=exp_len, warning=False)
		self.EQUAL_exp = Equal(width=exp_len)
		self.ABS_exp = Absolute(width=exp_len)
		self.INVERT_exp = Invert(width=exp_len, warning=False)
		self.INCREMENT = Increment(width=exp_len)
		self.LESSER_rounding = LesserThan(signed=False, width=self.rounding_bits)
		
	def __call__(self, a, b):
		call_stack.clear()
		if len(a) != len(b) or len(a) != self.size:
			raise ValueError(f'Expected {self.size} bit float ! Got {len(a)} and {len(b)}')
			
		sign_c = 0
		mant_c = self.NULL_mant.copy()
		exp_c = self.NULL_exp.copy()
		mant_overflow = 0
		
		sign_a, exp_a = a[0], Byte(a[1:1+self.expsize], width=self.expsize)
		mant_a = Byte(a[1+self.expsize:1+self.expsize+self.mantsize], width=self.mantsize)
		
		sign_b, exp_b = b[0], Byte(b[1:1+self.expsize], width=self.expsize)
		mant_b = Byte(b[1+self.expsize:1+self.expsize+self.mantsize], width=self.mantsize)

		if a.isnan() or b.isnan() or (a.isinf() and b.isinf() and XOR(sign_a, sign_b)):
			return Byte(math.nan, width=self.size)
		elif a.isinf() or b.isinf():
			return Byte((-1)**sign_a*math.inf, width=self.size)
				
		add_symbol = 1
		if self.EQUAL_exp(exp_a, self.NULL_exp):
			add_symbol = 0
			exp_a = self.ONE_exp.copy()
			
		mant_a = Byte([add_symbol]+a[1+self.expsize:1+self.expsize+self.mantsize]+[0]*3, width=self.mantsize+1)
		
		add_symbol = 1
		if self.EQUAL_exp(exp_b, self.NULL_exp):
			add_symbol = 0
			exp_b = self.ONE_exp.copy()
			
		mant_b = Byte([add_symbol]+b[1+self.expsize:1+self.expsize+self.mantsize]+[0]*3, width=self.mantsize+1)

		Debug(f"I  ] a = {a}, sign_a = {sign_a}, exp_a = {exp_a}, mant_a = {mant_a}")
		Debug(f"I  ] b = {b}, sign_b = {sign_b}, exp_b = {exp_b}, mant_b = {mant_b}")
		
		delta_exp, sub_underflow = self.SUB_exp(exp_a, exp_b)
		Debug(f'delta_exp = {delta_exp}')
		if delta_exp[0]: # delta_exp < 0
			Debug(f'swapping *_a and *_b because delta_exp < 0')
			sign_a, exp_a, mant_a, sign_b, exp_b, mant_b = sign_b, exp_b, mant_b, sign_a, exp_a, mant_a
			delta_exp, sub_underflow = self.SUB_exp(exp_a, exp_b)
		
		Debug(f"II ] a = {a}, sign_a = {sign_a}, exp_a = {exp_a}, mant_a = {mant_a}")
		Debug(f"II ] b = {b}, sign_b = {sign_b}, exp_b = {exp_b}, mant_b = {mant_b}")
		# Here, exp_a >= exp_b in all cases
		exp_c = exp_a.copy()
		
		shifted_non_zeros = mant_b[self.mantsize-1]
		delta_exp_sup_three = self.LESSER_exp(Byte(4, width=self.expsize), delta_exp)
		if self.LESSER_exp(Byte(self.mantsize+1+self.rounding_bits, width=self.expsize), delta_exp): # delta_exp > 3
			mant_b = self.NULL_mant.copy()
			Debug(f"We are shifting by more than {self.mantsize+1+self.rounding_bits}, set mant_b to NULL")
		elif not(delta_exp_sup_three):
			Debug(f"We are shifting by no more than 3 ({delta_exp}), shift mant_b to the right by delta_exp")
			#[0]*(mant_b.width-delta_exp.width)+
			delta_exp_padded = Byte(delta_exp.bin, width=mant_b.width)
			Debug(f"delta_exp_padded = {repr(delta_exp_padded)}")
			old_mant_b = mant_b.copy()
			mant_b, shift_underflow = self.SHIFTR_mant(mant_b, delta_exp_padded)
			Debug(f"mant_b = {repr(mant_b)}, old_mant_b = {repr(old_mant_b)}")
		elif shifted_non_zeros: # delta_exp > 3
			mant_b[-1] = 1
		
		
		#if AND(XOR(sign_a, sign_b),self.LESSER_exp(mant_a, mant_b)): # we exchange back our guys !
		#		mant_a, mant_b = mant_b, mant_a
				
		# NOOOO Here, mant_a > mant_b
		we_substracted_mantissa = False
		if XOR(sign_a, sign_b):
			# a and b are of different signs
			raise NotImplementedError('signed float are not implemented yet !')
			#mant_c = self.
		else:
			sign_c = sign_a
			mant_c, mant_overflow = self.ADD_mant(mant_a, mant_b)
			
		if mant_overflow:
			Debug(f'a mant_c overflow happend !')
			exp_c, _ = self.ADD_exp(exp_c, self.ONE_exp)
			last_bit = mant_c[-1]
			mant_c, _ = self.SHIFTR_mant(mant_c, self.ONE_mant)
			mant_c[-1] = last_bit
			
		if not(we_substracted_mantissa):
			pass
		
		Debug(f'III] sign_c = {sign_c}, exp_c = {exp_c}, mant_c = {mant_c}')
		# rounding
		#Debug(f'mant_c = {mant_c}')
		last_mantissa_bits = Byte(mant_c[-3:], width=self.rounding_bits)
		#Debug(f"last_mantissa_bits = {last_mantissa_bits}")
		mant_c = Byte(mant_c[0:self.mantsize+1], width=self.mantsize+1)
		carry = 0
		threshold = Byte([1, 0, NOT(mant_c[-1])], width=self.rounding_bits)
		#Debug(f'threshold = {repr(threshold)}, {threshold}')
		#Debug(f'self.LESSER_rounding.width = {self.LESSER_rounding.width}')
		Debug(f'threshold = {int(threshold)} < last_mantissa_bits = {int(last_mantissa_bits)} == {self.LESSER_rounding(threshold, last_mantissa_bits)}')
		if self.LESSER_rounding(threshold, last_mantissa_bits):
			Debug(f'doing the rounding')
			mant_c, carry = self.ADD_mant_normal(mant_c, Byte(1, width=self.mantsize+1))
			if carry:
				mant_c, _ = self.SHIFTR_mant_normal(mant_c, Byte(1, width=self.mantsize+1))
				exp_c, carry = self.ADD_exp(exp_c, self.ONE_exp)
				if carry:
					return Byte((-1)**sign_c*math.inf, width=self.size)
		
		if self.EQUAL_exp(exp_c, self.ONE_exp) and mant_c[0] == 0:
			exp_c = self.ONE_exp.copy()
			
		mant_c = Byte(mant_c[1:self.mantsize+1], width=self.mantsize)
		
		Debug(Byte([sign_c], width=1), Byte(exp_c.bin, width=self.expsize), Byte(mant_c.bin, width=self.mantsize))
		c = Byte([sign_c]+list(exp_c)+list(mant_c), width=self.size)
		return c

#ADDFLOAT8_v2 = AddFloat2(exp_len=4, mant_len=3)
ADDFLOAT8 = AddFloat2(exp_len=4, mant_len=3)

class MultiplyInteger(Logic):
	def __init__(self, width=DEFAULT_WIDTH):
		self.INVERT = Invert(width=width, warning=True)
		self.ADD = RippleCarryAdder(width=width, warning=True)
		self.width = width
		self.SHIFTL = ShiftLeft(width=width, warning=True)
		
	def __call__(self, a, b):
		signed = OR(a.signed, b.signed)
		different_sign = False
		if signed:
			different_sign = XOR(a[0], b[0])
			if a[0]:
				a, _ = self.INVERT(a)
			if b[0]:
				b, _ = self.INVERT(b)
			
		#Debug(f"a={a}, b={b}, signed={signed}, different_sign = {different_sign}")
			
		overflow = False
		c = Byte(0, width=self.width, signed=signed)
		i = self.width
		while i > 0:
			i -= 1
			if b[i]:
				ashift, shift_of = self.SHIFTL(a, Byte(self.width-i-1, width=self.width))
				c, add_of = self.ADD(c, ashift)
				Debug(f"shift_of = {shift_of}, add_of={add_of}")
				overflow = OR(OR(shift_of, add_of), overflow)
		
		if different_sign:
			c, inv_overflow = self.INVERT(c)
			overflow = OR(overflow, inv_overflow)
			Debug(f"We did invert c because signs were opposite...")
			
		if (c[0] != 0 and not(different_sign)) or (c[0] != 1 and different_sign) and signed:
				overflow = 1
			
		if overflow:
			OverflowWarning(f"Overflow during multiplication of {a} ({int(a)}) by {b} ({int(b)})")

			
		return c, overflow
	
MUL = MultiplyInteger(width=DEFAULT_WIDTH)

call_stack.clear()

def add_test(a, b):
	
	abin = Byte(float(a), width=8)
	bbin = Byte(float(b), width=8)
	cbin = ADDFLOAT8(abin, bbin)
	print(f"{float(abin)} + {float(bbin)} = {float(cbin)} ({str(abin)} + {str(bbin)} = {str(cbin)})")
	return cbin

def test_addf(a, b):
	"""
	Tries to add two floating point numbers
	
	>>> test_addf(2, 3)
	5.0
	>>> test_addf(-2, 2)
	0.0
	>>> test_addf(1.25, 0.25)
	1.5
	"""
	abin = Byte(float(a), width=8)
	bbin = Byte(float(b), width=8)
	cbin = ADDFLOAT8(abin, bbin)
	return float(cbin)

def test_addi(a, b):
	"""
	Tries to add two integers:
	
	>>> test_addi(2, 3)
	5
	>>> test_addi(-2, 2)
	0
	>>> test_addi(1, 0)
	1
	"""
	abin = Byte(int(a), width=8)
	bbin = Byte(int(b), width=8)
	cbin, _ = RippleCarryAdder(width=8)(abin, bbin)
	return int(cbin)

def test_muli(a, b):
	"""
	Tries to add two integers:
	
	>>> test_muli(2, 3)
	6
	>>> test_muli(-2, 2)
	-4
	>>> test_muli(1, 0)
	0
	"""
	abin = Byte(int(a), width=8)
	bbin = Byte(int(b), width=8)
	cbin, _ = MultiplyInteger(width=8)(abin, bbin)
	return int(cbin)


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


def plotAdd(bits=8):
	import numpy as np
	import matplotlib.pyplot as plt
	#from mpl_toolkits.mplot3d import Axes3D
	nbs = np.linspace(0, 5, 50)
			
	def _conv(x):
		return Byte(float(x), width=bits)
	#conv = np.vectorize(_conv)
	nbs = [_conv(x) for x in nbs]
	#print(nbs)
	heatmap = np.zeros(shape=(len(nbs), len(nbs)))
#	X = []
#	Y = []
#	Z = []
	for i,x in enumerate(nbs):
		for j,y in enumerate(nbs):
#			X.append(float(x))
#			Y.append(float(y))
#			Z.append( float(ADDFLOAT8(x, y)))
			heatmap[i, j] = float(ADDFLOAT8(x, y))
			
	#Y = conv(X)
#	fig = plt.figure()
#	ax = fig.add_subplot(111)
#	ax.plot(xs=X,ys=Y, zs=Z)
#	ax.grid(True)
	plt.imshow(heatmap)
	
if __name__ == "__main__":
	import sys
	#print(sys.argv)
	if len(sys.argv) > 1:
		if sys.argv[1] == "test":
			DEBUG = False
			import doctest
			test = doctest.testmod()
			exit(test.failed)