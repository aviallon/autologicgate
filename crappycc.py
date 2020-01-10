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
		res += "\tJMP end\n"
		return res, []
	
	def evaluate_add(self,ops):
		res = ""
		if ops[1] != "A":
			res += f"\tMOV A,{ops[1]}\n"
		res += f"\tADD A,{ops[0]}\n"
			
		return res, ["A"]

	def evaluate_sub(self,ops):
		res = ""
		if ops[1] != "A":
			res += f"\tMOV A,{ops[1]}\n"
		res += f"\tSUB A,{ops[0]}\n"
			
		return res, ["A"]

	def evaluate_mul(self,ops):
		return f"""\
\tMOV param1,{ops[1]}
\tMOV param2,{ops[0]}
\tCALL MUL
""", ["res"]

	def evaluate_div(self,ops):
		return f"""\
\tMOV param1,{ops[1]}
\tMOV param2,{ops[0]}
\tCALL DIV
""", ["res"]

	def evaluate_asign(self,ops):
		if not(re.match("^(\+@(?:0[xb])?[0-9]+)|A|B|U[0-3]|res|param[1-2]$", str(ops[0]))):
			raise CompilerError(f"{ops[0]} is not addressable")
		return f"""\
\tMOV {ops[0]},{ops[1]}
""", [f"{ops[0]}"]
			

	def evaluate_equals(self,ops):
		return f"""\
\tCMP {ops[0]},{ops[1]}
\tMOV res,#0
\tJMPNEQ _op_{self.label_counter}
\tMOV res,#1
_op_{self.label_counter}:\tNOP
""", ["res"]

	def evaluate_not_equals(self,ops):
		return f"""\
\tCMP {ops[0]},{ops[1]}
\tMOV res,#0
\tJMPEQ _op_{self.label_counter}
\tMOV res,#1
_op_{self.label_counter}:\tNOP
""", ["res"]

	def evaluate_strictly_superior(self,ops):
		return f"""\
\tCMP {ops[0]},{ops[1]}
\tMOV res,#0
\tJMPGT _op_{self.label_counter}
\tMOV res,#1
_op_{self.label_counter}:\tNOP
""", ["res"]

	def evaluate_if(self,ops):
		return f"""\
\tCMP {ops[0]}
\tJMPEQ {ops[1]}
""", []

	def evaluate_increment(self, ops):
		return f"""\
\tINC {ops[0]}
""", [ops[0]]

	def empty_little_stack(self, ops):
		return "", []
	
	def evaluate_log2(self, ops):
		return f"""\
\tMOV param1,{ops[0]}
\tCALL LOG2
""", ["res"]

	def META_evaluate_declare_var(instance, size):
		def evaluate_declare_var(ops):
			if not(re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", ops[0])):
				raise CompilerError(f"{ops[0]} is not a valid identifier")
			print("Instance vars : ", instance.variables)
			if ops[0] in instance.variables:
				raise CompilerError(f"redefinition of {ops[0]} not allowed !")
			instance.variables[ops[0]] = instance.var_size
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

	def __init__(self, expr, variables):
		self.words = list(filter(None, re.split("([\(\)/\*-]|\++|[0-9]+|[a-zA-Z_][a-zA-Z0-9_]*|;)|\s+", expr)))
		self.variables = variables
		self.functions = {}
		#print(self.words)
		self.var_size = sum(x for x in variables.values())
		self.operators = {
				"+": {"prec":20, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_add},
				"-": {"prec":20, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_return},
				"*": {"prec":30, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_mul},
				"/": {"prec":30, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_div},
				"=": {"prec":5, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_asign},
				#"¤": {"prec":1, "assoc":"left", "nargs":4, "what":lambda x:print(x)},
				"==":{"prec":10, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_equals},
				"!=":{"prec":10, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_not_equals},
				">":{"prec":10, "assoc":"left", "nargs":2, "type":"infix", "what":self.evaluate_strictly_superior},
				"++": {"prec": 10, "assoc":"left", "nargs":1, "type":"postfix","what":self.evaluate_increment},
				"(": {"prec":1000, "assoc":"left", "nargs":0, "type":"prefix", "what":lambda x:x},
				}
		self.keywords = {
				"if":{"nargs":2, "what":self.evaluate_if},
				"int":{"nargs":1, "what":Expression.META_evaluate_declare_var(self,1)},
				"return":{"nargs":1, "what":self.evaluate_return},
				"function":{"nargs":2, "what":Expression.META_evaluate_declare_function(self,1)},
				#";": {"nargs":0, "what":self.empty_little_stack}
				"log": {"nargs":1, "what":self.evaluate_log2}
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
						
			if state == "want_operand":
				if cur >= len(self.words):
					raise CompilerError(f"Expected an operand...")
				w = self.words[cur]
				print("want_operand:", w, "type:", self.operators.get(w)["type"] if w in self.operators else "not an op")
				print("DEBUT:", w, stack, opstack)
				if (self.operators.get(w)["type"] == "prefix") if w in self.operators else False:
						opstack += [("prefix", w)]
				elif w in self.keywords:
					opstack += [("prefix", w)]
					
				elif re.match("^[0-9]+$", w) or re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", w):
					stack += [w]
					state = "have_operand"
				else:
					raise CompilerError(f"Expected an operand after '{opstack[-1]}', got '{w}'")
			else:
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
				elif (self.operators.get(w)["type"] == "infix") if w in self.operators else False:
					print("Encountered infix operator")
					while len(opstack):
						print("opstack...")
						optype, op = opstack[-1]
						if opstack[-1] in self.keywords:
							stack += [op]
							opstack.pop()
						elif (
								optype == "prefix" or
								(operators[op]["prec"] > operators[w]["prec"] and operators[w]["type"] == "prefix") or
								(operators[op]["prec"] == operators[w]["prec"] and operators[op]["assoc"] == "left")
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
		print("BEGIN TREE TO CODE")
		operators = self.operators
		stack = self.stack[::-1]
		eval_stack = []
		asm = ""
		while len(stack):
			#print(stack, eval_stack)
			op = stack.pop()
			#print(op)
			if op in self.keywords:
				operandes = [eval_stack.pop() for i in range(self.keywords[op]["nargs"])][::-1]
				res, stackret = self.keywords[op]["what"](operandes)
				asm += res
				eval_stack += stackret
			elif op in operators:
				operandes = [eval_stack.pop() for i in range(operators[op]["nargs"])][::-1]
				res, stackret = operators[op]["what"](operandes)
				asm += res
				eval_stack += stackret
			elif op in self.variables:
				eval_stack += [f"+@{self.variables[op]}"]
			elif re.match("^[0-9]+$", op):
				eval_stack += [f"#{op}"]
			elif op not in ["A", "B"]:
				eval_stack += [op]
			else:
				raise CompilerError(f"'{op}' is a reserved symbol !")
		#print(stack, eval_stack)
		
		asm_prefix = ""
		for var in self.variables:
			asm_prefix += f"byte {var} +@{self.variables[var]}\n"
		
		asm_prefix += """
include syslib
start:
	JMP main
end:
	DISP res
	HALT
main:
"""
		asm_suffix = """
	JMP end
"""
		return asm_prefix + asm + asm_suffix
		


#class Context:
#	def __str__(self):
#		s = f"Context (depth={self.depth}) :\n=============\n"
#		for l in self.lines:
#			s += l + "\n"
#		return s
#	
#	def __repr__(self):
#		lines = "\n".join(self.lines)
#		s = f"Context(depth={self.depth}, code=\"\"\"\\\n\
#{lines}\n\
#\"\"\")"
#		return s
#	
#	def __init__(self, code, depth=0):
#		parser = re.compile("\n+|;")
#		self.lines = []
#		if type(code) == str:
#			self.lines = list(filter(lambda x: not(re.match("^\s*$", x)), re.split(parser, code)))
#		else:
#			self.lines = code
#			
#		self.depth = depth
#			
#		print(self.__str__())
#		self.contexts = []
#		level = 0
#		line_begin = 0
#		car_begin = 0
#		for i,line in enumerate(self.lines):
#			#print(f"Line ({i}): ", line)
#			if "}" in line:
#				level -= 1
#				car_end = line.index("}")
#				line_end = i
#				if level == 0:
#					content = ""
#					if line_end == line_begin:
#						content = [self.lines[line_begin][car_begin+1:car_end]]
#					else:
#						#print(line_begin, line_end, car_begin, car_end)
#						content = [self.lines[line_begin][car_begin+1:]]+self.lines[line_begin+1:line_end]+[self.lines[line_end][:car_end]]
#					#print(content)
#					self.contexts += [{
#							"begin": (line_begin, car_begin),
#							"end": (i, line.index("}")),
#							"content": Context(content, depth+1)
#							}]
#				#print(f"Found '}}' at ({i}:{car_end}) - level = {level}")
#					
#			if "{" in line:
#				what_index = line.index("{")
#				#print(f"Found '{{' at ({i}:{what_index}) - level = {level}")
#				if level == 0:
#					#print("HELP : ", car_begin, len(line))
#					if car_begin == len(line)-1:
#						line_begin = i+1
#						car_begin = 0
#					else:
#						line_begin = i
#						car_begin = what_index
#				level += 1
#				
#				
#		for i, line in enumerate(self.lines):
#			lineparse = re.compile("\s+")

def crapcompile(string):
	expr = Expression(string, variables={})
	expr.parse()
	asm = expr.tree_to_code()
	print("ASSEMBLY\n==============")
	print(asm)
	return asm
	
	
if __name__ == "__main__":
	import argparse
	import os
	import sys
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="enable debug mode, activates verbose")
	parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="enable debug mode")
	parser.add_argument("-S", "--assembly", dest="assembly", action="store_true", help="outputs assembly only")
	parser.add_argument('-o', '--output', dest="output", metavar="OUTPUT_FILE", help="output file", default="")
	parser.add_argument(metavar="INPUT_FILE", dest="input", help="input file", default="prog.crapasm")
	args = parser.parse_args()
	
	basename = re.split("(\.alang)$", os.path.basename(args.input))[0]
	if args.input == "-":
		basename = "a"
	output = args.output
	if args.output == "":
		output = basename+".crapasm"
	
	with open(output, "w") as compile_file:
		code = ""
		asm = ""
		input_file = sys.stdin
		if args.input != "-":
			input_file = open(args.input, "r")
		code = input_file.read()
		if input_file is not sys.stdin:
			input_file.close()
		asm = crapcompile(code)
		if args.assembly:
			compile_file.write(asm)
		else:
			with open(f"{basename}.crapasm", "w") as intermediate_file:
				intermediate_file.write(asm)