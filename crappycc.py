#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:05:09 2020

@author: aviallon
"""
import re

class CompilerError(Exception):
	pass


class Expression:

	def evaluate_return(self,ops):
		res = ""
		if ops[0] != "res":
			res += f"\tMOV res, {ops[0]}\n"
		res += "\tRET\n"
		return res, []
	
	def evaluate_add(self,ops):
		res = ""
		p1, p2 = ops[0], ops[1]
		if ops[0][0] == "#":
			if ops[1][0] == "#": # if both parameters are numbers, then add them at compile time !
				return "", [f"#{int(ops[0][1:])+int(ops[1][1:])}"]
			p1, p2 = p2, p1 # we can't have a const as first param to ADD
		res += f"\tADD {p1},{p2}\n"
			
		return res, [p1]

	def evaluate_sub(self,ops):
		res = ""
		p1, p2 = ops[0], ops[1]
		if ops[0][0] == "#":
			if ops[1][0] == "#": # if both parameters are numbers, then substract them at compile time !
				return "", [f"#{int(ops[0][1:])-int(ops[1][1:])}"]
		if ops[0][0] == "#" or ops[0][:2] == "+@":
			res += f"\tMOV A,{ops[0]}\n"
			p1 = "A"
		if ops[0][0] == "#" or ops[0][:2] == "+@":
			res += f"\tMOV B, {ops[1]}\n"
			p2 = "B"
		res += f"\tSUB {p1},{p2}\n"
			
		return res, ["A"]

	def evaluate_mul(self,ops):
		return f"""\
	MOV param1,{ops[1]}
	MOV param2,{ops[0]}
	CALL MUL
""", ["res"]

	def evaluate_div(self,ops):
		return f"""\
	MOV param1,{ops[1]}
	MOV param2,{ops[0]}
	CALL DIV
""", ["res"]

	def evaluate_asign(self,ops):
		if not(re.match("^(\+@(?:0[xb])?[0-9]+)|A|B|U[0-3]|res|param[1-2]$", str(ops[0]))):
			raise CompilerError(f"{ops[0]} is not addressable")
		return f"""\
	MOV {ops[0]},{ops[1]}
""", [f"{ops[0]}"]
			

	def evaluate_equals(self,ops):
		res = ""
		p1,p2 = ops[0], ops[1]
		if ops[0][0] == "#":
			if ops[1][0] == "#": # if both parameters are numbers, then test them at compile time !
				return f"\tMOV res,#{int(ops[0][1:])==int(ops[1][1:])}", ["res"]
		if  ops[0][0] == "#" or ops[0][:2] == "+@":
			if ops[1][0] != "#" and ops[1][:2] != "+@":
				p2, p1 = p1, p2
			else:
				p1 = "res"
				res += f"""\
	MOV res, {ops[0]}
"""
		res += f"""\
	CMP {p1},{p2}
	MOV res,#0
	JNZ _op_{self.label_counter}
	MOV res,#1
_op_{self.label_counter}:\tNOP
"""
		self.label_counter += 1
		return res, ["res"]

	def evaluate_not_equals(self,ops):
		res = ""
		p1,p2 = ops[0], ops[1]
		if ops[0][0] == "#":
			if ops[1][0] == "#": # if both parameters are numbers, then test them at compile time !
				return f"\tMOV res,#{int(ops[0][1:])!=int(ops[1][1:])}", ["res"]
		if ops[0][0] == "#" or ops[0][:2] == "+@":
			if ops[1][0] != "#" and ops[1][:2] != "+@":
				p2, p1 = p1, p2
			else:
				p1 = "res"
				res += f"""\
	MOV res, {ops[0]}
"""
		res += f"""\
	CMP {p1},{p2}
	MOV res,#0
	JZ _op_{self.label_counter}
	MOV res,#1
_op_{self.label_counter}:\tNOP
"""
		self.label_counter += 1
		return res, ["res"]

	def evaluate_strictly_superior(self,ops):
		if ops[0][0] == "#":
			if ops[1][0] == "#":  # if both parameters are numbers, then test them at compile time !
				return f"\tMOV res,#{int(ops[0][1:]) > int(ops[1][1:])}", ["res"]

		p1, p2 = ops[0], ops[1]
		res = ""
		if ops[0][0] == "#" or ops[0][:2] == "+@":
			if ops[1][0] != "#" and ops[1][:2] != "+@":
				p2, p1 = p1, p2
			else:
				p1 = "res"
				res += f"""\
			MOV res, {ops[0]}
		"""
		res += f"""\
	CMP {p1},{p2}
	MOV res,#0
	JG _op_{self.label_counter}
	MOV res,#1
_op_{self.label_counter}:\tNOP
"""
		self.label_counter += 1
		return res, ["res"]

	def evaluate_strictly_inferior(self, ops):
		if ops[0][0] == "#":
			if ops[1][0] == "#":  # if both parameters are numbers, then test them at compile time !
				return f"\tMOV res,#{int(ops[0][1:]) < int(ops[1][1:])}", ["res"]

		p1, p2 = ops[0], ops[1]
		res = ""
		if ops[0][0] == "#" or ops[0][:2] == "+@":
			if ops[1][0] != "#" and ops[1][:2] != "+@":
				p2, p1 = p1, p2
			else:
				p1 = "res"
				res += f"""\
			MOV res, {ops[0]}
		"""
		res += f"""\
	CMP {p1},{p2}
	MOV res,#0
	JL _op_{self.label_counter}
	MOV res,#1
_op_{self.label_counter}:\tNOP
"""
		self.label_counter += 1
		return res, ["res"]

	def evaluate_if(self,ops):
		if not(type(ops[1]) == Expression):
			raise CompilerError(f"Expected {ops[1]} to be an Expression")
		res = ""
		res += f"""\
	CMP {ops[0]}
	JMPEQ _else_{self.depth}_{self.label_counter}
"""
		res += ops[1].asm
		res += f"""\
_else_{self.depth}_{self.label_counter}:
	NOP
"""
		self.label_counter += 1
		return res, []
	
	def evaluate_while(self,ops):
		if not(type(ops[1]) == Expression):
			raise CompilerError(f"Expected {ops[1]} to be an Expression")
		if not(type(ops[0]) == Expression):
			raise CompilerError(f"Expected {ops[0]} to be an Expression")
		#cmp_eval = ops[0].asm
		cmp_reg = "res"
		res = ""
		res += f"""\
_while_{self.depth}_{self.label_counter}: ; while cond calc
"""
		res += ops[0].asm
		res += f"""\
	CMP {cmp_reg}
	JZ _else_{self.depth}_{self.label_counter}
; while body
"""
		res += ops[1].asm
		res += f"""\
	JMP _while_{self.depth}_{self.label_counter}
_else_{self.depth}_{self.label_counter}:
	NOP
"""
		self.label_counter += 1
		return res, []

	def evaluate_increment(self, ops):
		return f"""\
	INC {ops[0]}
""", [ops[0]]

	def evaluate_decrement(self, ops):
		return f"""\
	DEC {ops[0]}
""", [ops[0]]

	def empty_little_stack(self, ops):
		return "", []
	
	def evaluate_log2(self, ops):
		return f"""\
	MOV param1,{ops[0]}
	CALL LOG2
""", ["res"]

	def evaluate_print(self, ops):
		res = ""
		p1 = ops[0]
		if p1[0] == "#":
			res += f"""\
	MOV res, {ops[0]}
"""
			p1 = "res"
		res += f"\tDISP {p1}\n"
		return res, []

	def META_evaluate_declare_var(instance, size):
		def evaluate_declare_var(ops):
			if not(re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", ops[0])):
				raise CompilerError(f"{ops[0]} is not a valid identifier")
			realname = f"_{instance.depth}_{ops[0]}"
			print("Instance vars : ", instance.variables)
			if realname in instance.variables:
				raise CompilerError(f"redefinition of {realname} not allowed !")
			instance.variables[realname] = instance.var_size
			instance.var_size += size
			print("Instance vars after : ", instance.variables)
			return f"""""", [f"+@{instance.var_size-size}"]
		return evaluate_declare_var
	
	def META_evaluate_declare_function(instance, size):
		def evaluate_declare_function(ops):
			if not(re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", ops[0])):
				raise CompilerError(f"{ops[0]} is not a valid identifier for a function")
			#print("Instance vars : ", instance.functions)
			if ops[0] in instance.functions:
				raise CompilerError(f"redefinition of {ops[0]} not allowed !")
			instance.functions[ops[0]] = {"nargs":ops[1]}
			#print("Instance vars after : ", instance.variables)
			return f"", []
		return evaluate_declare_function

	def __init__(self, expr, variables={}, depth=0, debug=False):
		if type(expr) == str:
			expr = re.sub("/\*[^\*]*?\*/", "", expr)
			expr = re.sub("//.*(\n|$)", "\n", expr)
			self.words = list(filter(None, re.split("([\{\}\(\)/\*]|\++|-+|[0-9]+|[a-zA-Z_][a-zA-Z0-9_]*|;)|\s+", expr)))
		elif type(expr) == list:
			self.words = expr[:]
		else:
			raise CompilerError("Expected a list or a string")
		self.variables = variables
		self.functions = {}
		self.depth = depth
		self.asm = ""
		self.debug = debug
		#print(self.words)
		self.var_size = sum(x for x in variables.values())
		self.operators = {
				"+": {"prec":20, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_add},
				"-": {"prec":20, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_sub},
				"*": {"prec":30, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_mul},
				"/": {"prec":30, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_div},
				"=": {"prec":5, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_asign},
				"==":{"prec":10, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_equals},
				"!=":{"prec":10, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_not_equals},
				">":{"prec":10, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_strictly_superior},
				"<": {"prec": 10, "assoc": "left", "nargs": 2, "type": "infix", "what": self.evaluate_strictly_inferior},
				"++": {"prec": 10, "assoc":"left", "nargs":1, "type":"postfix","what":self.evaluate_increment},
				"--": {"prec": 10, "assoc": "left", "nargs": 1, "type": "postfix", "what": self.evaluate_decrement},
				"(": {"prec":1000, "assoc":"left", "nargs":0, "type":"prefix", "what":lambda x:x},
				}
		self.keywords = {
				"if":{"prec":-1,"nargs":2, "what":self.evaluate_if},
				"while":{"prec":-1,"nargs":2, "what":self.evaluate_while},
				"int":{"prec":0,"nargs":1, "what":Expression.META_evaluate_declare_var(self,1), "special_state":"want_new_identifier"},
				"return":{"prec":-1,"nargs":1, "what":self.evaluate_return},
				"print":{"prec":-1,"nargs":1, "what":self.evaluate_print},
				"function":{"prec":0,"nargs":2, "what":Expression.META_evaluate_declare_function(self,1)},
				#";": {"nargs":0, "what":self.empty_little_stack}
				"log": {"prec":0,"nargs":1, "what":self.evaluate_log2}
				}
	
		self.label_counter = 0

		
	def parse(self):
		cur = 0
		stack = []
		opstack = []
		operators = self.operators
		state = "want_operand"
		#arg_count = 1
		print(self.words)
		while True:
			#w = words[cur]
			if cur < len(self.words):
				if self.words[cur] == ";":
					while len(opstack):
						optype, op = opstack.pop()
						if op == "(":
							raise CompilerError("A lone opening parenthesis has been found...")
						stack += [op]
					state = "want_operand"
					cur += 1
					if cur == len(self.words):
						break
					
			if state == "want_new_identifier":
				if cur >= len(self.words):
					raise CompilerError(f"Expected an operand...")
				w = self.words[cur]
				print("want_new_identifier:", w)
				if re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", w):
					identifier_name = f"declare(_{self.depth}_{w})"
					stack += [identifier_name]
					state = "have_operand"
			elif state == "want_operand":
				if cur >= len(self.words):
					raise CompilerError(f"Expected an operand...")
				w = self.words[cur]
				print("want_operand:", w, "type:", self.operators.get(w)["type"] if w in self.operators else "not an op")
				print("DEBUT:", w, stack, opstack)
				if (self.operators.get(w)["type"] == "prefix") if w in self.operators else False:
					opstack += [("prefix", w)]
				elif w in self.keywords:
					opstack += [("prefix", w)]
					print("we have a keyword here !")
					print(self.keywords[w])
					if "special_state" in self.keywords[w]:
						print(f"Set status to {self.keywords[w]['special_state']}")
						state = self.keywords[w]['special_state']
				elif re.match("^[0-9]+$", w) or re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", w):
					stack += [w]
					state = "have_operand"
				elif w == "{":
					cur_debut = cur
					sub_expr = ""
					depth = 1
					while depth > 0:
						cur += 1
						if self.words[cur] == "}":
							depth -= 1
						elif self.words[cur] == "{":
							depth += 1
					sub_expr = self.words[cur_debut+1:cur]
					stack += [Expression(sub_expr, {}, depth+1)]
					state = "want_operand"
				else:
					raise CompilerError(f"Expected an operand after '{opstack[-1]}', got '{w}'")
			else: # state == "have_operand"
				if cur >= len(self.words):
					break
				w = self.words[cur]
				print("have_operand:", w, "type:", self.operators.get(w)["type"] if w in self.operators else "not an op")
				print("DEBUT:", w, stack, opstack)
						
				if (self.operators.get(w)["type"] == "postfix") if w in self.operators else False:
					print("Encountered postfix operator")
					stack += [w]
				elif w == ")":
					print("Encountered closing parenthesis")
					optype, op = opstack.pop()
					while op != "(":
						stack += [op]
						if len(opstack) > 0:
							optype, op = opstack.pop()
						else:
							raise CompilerError("Too much closing parenthesis...")
					if optype == "infix":
						stack += ["call"]
						
				elif w == ",":
					print("The virgule")
					while op != "(":
						stack += [op]
						if len(opstack) > 0:
							optype, op = opstack.pop()
						else:
							raise CompilerError("Too much closing parenthesis...")
					state = "want_operand"
				elif w == "{":
					cur_debut = cur
					sub_expr = ""
					depth = 1
					while depth > 0:
						cur += 1
						if self.words[cur] == "}":
							depth -= 1
						elif self.words[cur] == "{":
							depth += 1
					sub_expr = self.words[cur_debut+1:cur]
					stack += [Expression(sub_expr, {}, depth+1)]
					state = "want_operand"
				elif (self.operators.get(w)["type"] == "infix") if w in self.operators else (self.operators[w]["type"] == "infix") if w in self.keywords else False:
					print("Encountered infix operator")
					while len(opstack):
						print("opstack...")
						optype, op = opstack[-1]
						op_prec, op_assoc, w_type, w_prec = None, None, None, None
						if op in self.operators:
							op_prec = self.operators[op]["prec"]
							op_assoc = self.operators[op]["assoc"]
						else:
							op_prec = self.keywords[op]["prec"]
							op_assoc = "left"
						if w in self.operators:
							w_type = self.operators[w]["type"]
							w_prec = self.operators[w]["prec"]
						else:
							w_type = "prefix"
							w_prec = self.keywords[w]["prec"]
							
						if opstack[-1] in self.keywords:
							stack += [op]
							opstack.pop()
						elif (
								(optype == "prefix" and op_prec >= 0) or
								(op_prec > w_prec and w_type == "infix") or
								(op_prec == w_prec and op_assoc == "left")
							) and op != "(":
							stack += [op]
							opstack.pop()
						else:
							break
					opstack += [('infix', w)]
					state = "want_operand"
				else:
					raise CompilerError(f"'{w}' is an operand while we wanted an operator...")
			cur += 1
			print("FIN:", w, stack, opstack)
					
		while len(opstack):
			optype, op = opstack.pop()
			if op == "(":
				raise CompilerError("A lone opening parenthesis has been found...")
			stack += [op]
				
		print(stack, opstack)
		
		self.stack = stack[::]
		
		def make_node(node_name, stack):
			if node_name in operators:
				nargs = operators[node_name]["nargs"]
				#print(len(stack)-1, nargs, stack)
				leaves = []
				for i in range(nargs):
					leaf = make_node(stack.pop(), stack)
					leaves += [leaf]
					if i != nargs-1 and len(stack) == 0:
						raise CompilerError(f"Ooops, '{node_name}' misses {nargs-i-1} arguments !!!")
				
				return {"name":node_name, "operandes":leaves}
			elif node_name in self.variables:
				#print(self.variables)
				return {"name":"variable", "value":f"+@{self.variables[node_name]}"}
			else:
				return {"name":"integer", "value":f"#{node_name}"}
			
		self.tree = make_node(stack.pop(), stack)
			
		return self.tree
	
	def tree_to_code(self):
		import time
		print("BEGIN TREE TO CODE")
		stack = self.stack[::-1]
		eval_stack = []
		asm = ""
		while len(stack):
			print(stack, eval_stack)
			op = stack.pop()
			ok = False
			print(op)
			if type(op) == Expression:
				print(self.variables)
				op.variables = self.variables
				op.var_size = self.var_size
				op.parse()
				op.tree_to_code()
				self.variables = op.variables
				self.var_size = op.var_size
				eval_stack += [op]
				ok = True
			elif op in self.keywords:
				operandes = [eval_stack.pop() for i in range(self.keywords[op]["nargs"])][::-1]
				res, stackret = self.keywords[op]["what"](operandes)
				asm += res
				eval_stack += stackret
				ok = True
				print(f"KW : res : {res}, stackret = {stackret}")
			elif op in self.operators:
				operandes = [eval_stack.pop() for i in range(self.operators[op]["nargs"])][::-1]
				res, stackret = self.operators[op]["what"](operandes)
				asm += res
				eval_stack += stackret
				ok = True
				print(f"OP : res : {res}, stackret = {stackret}")
			elif "declare(" in op:
				varname = op.split("(")[1].split(")")[0]
				varbasename = varname.split("_",2)[2]
				if varname in self.variables:
					raise CompilerError(f"Variable {varbasename} already defined in this context !")
					
				eval_stack += [varbasename]
				ok = True
				print(f"DEC: self.variables : {self.variables}")
			else:
				#ok = False
				for i in range(self.depth+1):
					temp = f'_{self.depth-i}_{op}'
					#print("temp : ",temp, "self.variables=",self.variables)
					if temp in self.variables:
						eval_stack += [f"+@{self.variables[temp]}"]
						ok = True
						break
				
				
			if not(ok):
				if re.match("^[0-9]+$", op):
					eval_stack += [f"#{op}"]
				elif op not in ["A", "B"]:
					eval_stack += [op]
				else:
					raise CompilerError(f"'{op}' is a reserved symbol !")
					
			if self.debug:
				time.sleep(0.5)
			print(f"({self.depth}) {'****'*self.depth} ===============")
			
		self.asm = asm
		return self.asm
		
	def assembly(self):
		if self.asm == "":
			self.tree_to_code()
			
		asm_suffix = ""
		asm_prefix = ""
		if self.depth == 0:
			for var in self.variables:
				asm_prefix += f"byte {var} +@{self.variables[var]}\n"
			
			asm_prefix += """
include syslib
start:
	CALL main
end:
	DISP res
	HALT
main:
"""
			asm_suffix = """
	JMP end
"""
		return asm_prefix + self.asm + asm_suffix
		


def crapcompile(string, debug=False):
	expr = Expression(string, variables={}, debug=debug)
	expr.parse()
	asm = expr.assembly()
	print("ASSEMBLY\n==============")
	print(asm)
	return asm
	
	
if __name__ == "__main__":
	import argparse
	import os
	import sys
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="enable debug mode, activates verbose")
	parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="enable verbose mode")
	parser.add_argument("-S", "--assembly", dest="assembly", action="store_true", help="outputs assembly only")
	parser.add_argument('-o', '--output', dest="output", metavar="OUTPUT_FILE", help="output file", default="")
	parser.add_argument(metavar="INPUT_FILE", dest="input", help="input file", default="prog.crapasm")
	args = parser.parse_args()
	
	basename = re.split("(\.alang)$", os.path.basename(args.input))[0]
	if args.input == "-":
		basename = "a"
	output = args.output
	if args.output == "":
		output = basename
	
	
	code = ""
	asm = ""
	input_file = sys.stdin
	if args.input != "-":
		input_file = open(args.input, "r")
	code = input_file.read()
	if input_file is not sys.stdin:
		input_file.close()
	asm = crapcompile(code, args.debug)
	if args.assembly:
		with open(f"{output}.crapasm", "w") as compile_file:
			compile_file.write(asm)
			print(f"Assembly code written to file {output}.crapasm")
	else:
		with open(f"{basename}.crapasm", "w") as intermediate_file:
			intermediate_file.write(asm)
		os.system(f"python crappyasm.py {'-v' if args.verbose else ''} -o {output}.ram {basename}.crapasm")
		print(f"RAM written to file {output}.ram")