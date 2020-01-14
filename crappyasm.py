#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:47:56 2020

@author: aviallon
"""
from instructions import instructions, micro_inst, micro_inst_number, high_lvl_instructions, registers, instructions_sorted

import re

class Error(Exception):
	def __init__(self, message):
		import sys
		print(f"\033[31m{self.__class__.__name__}:\033[0m {message}", file=sys.stderr)
		
class UndefinedInstruction(Error):
	pass

class UndefinedInstructionVariant(Error):
	pass

class UndefinedVar(Error):
	pass

class NotEnoughAddressableMemory(Error):
	pass

def find_similar(search_key, liste):
	found = True
	foundname = False
	x = 2
	while found:
		found = False
		index = 0
		while index < len(liste):
			if search_key[:x] in liste[index]:
				found = True
				break
			index += 1
		
		if found:
			foundname = liste[index]
		x += 1
		if x > len(search_key):
			break
		
	return foundname

identifier_regex = "[a-zA-Z_][a-zA-Z0-9_]*"

def inst_split(string):
	ligne = re.split("(\s+)|,", string)
	return list(filter(lambda x: x is not None and x != " " and x != "", ligne))

def get_syslib():
	syslib = """\
; System Library
byte    param1    U1
byte    param2    U2
byte    res    U3

        JMP start
DIV:
        MOV A,param1 ; move parameters to work registers
        MOV B,param2
        MOV U1,B
        
        CMP param2,#0
        JNZ _div_loop
        ABRT
_div_loop:
        SUB A,U1 ; we substract b to a' once
        CMP A,#0 ; if the result is superior to 0, then we increment the quotient, and retest
        JG _div_next
        JMP _div_end
_div_next:
        INC res
        JMP _div_loop
_div_end:
        RET
		
MUL:
        MOV B,param1 ; we do that because it is faster to add from B (removes unnecessary move operation)
        ; MOV U2,param2 redundant, as param2 is already U2
        MOV res,#0x00
_mul_loop:
        CMP param2 ; compares to 0
        JZ _mul_end ; if y is zero, then we do not have to add "x" to "z" anymore -> multiplication is finished
        JBIT #0x00, _mul_bit_is_one_do_add
        JMP _mul_bit_is_zero_do_not_add
_mul_bit_is_one_do_add:
        ADD res,B
_mul_bit_is_zero_do_not_add:
        SHIFTL B
        SHIFTR param2
        JMP _mul_loop
_mul_end:
        RET

LOG2:
        MOV A,param1
        MOV res,#0
        MOV B,#0
_log2_loop:
        INC B
        SHIFTR A
        CMP A
        JZ _log2_end
        JBIT #0, _log2_no_cp_to_res
        MOV res, B
_log2_no_cp_to_res:
        JMP _log2_loop
_log2_end:
        RET
"""
	return syslib.split("\n")

def assembler(data, address_bits=8, debug=False, verbose=True):
	machine_code = []
	lines = data.split("\n")
	includes = []
	for i, l in enumerate(lines):
		ligne = l.strip("\t").strip(" ")
		ligne = re.split(";.*", ligne)[0]
		if temp := re.findall("^include\s+("+identifier_regex+")", ligne):
			includes.append(temp[0])
			lines[i] = ""
	
	if "syslib" in includes:
		lines = get_syslib() + lines
	
	def secondpass(lines):
		jumplist = {}
		variables = {}
		includes = []
		lignes_labelisees = []
		for i,l in enumerate(lines):
			ligne = l.strip("\t").strip(" ")
			ligne = re.split(";.*", ligne)[0]
			regex = "byte\s+("+identifier_regex+")\s+(.+)"
			if temp := re.findall(regex, ligne):
				if debug:
					print(temp)
				identifier, value = temp[0][0], temp[0][1]
				if identifier in variables:
					raise Error(f"Redifinition of variable {temp[0][0]}")
					
				if re.findall("#|(\+?@)(0[xb])?[0-9A-Fa-f]+", value):
					pass
				elif value in registers:
					pass
				else:
					raise Error(f"Illegal value '{value}' for a variable !")
					
				variables[identifier] = value
				ligne = ""
			jump = ""
			if temp := re.findall("^("+identifier_regex+"):\s*", ligne):
				jump = temp[0]
				if jump in jumplist:
					raise Error(f"Labels must be unique, found {jump} more than once")
				jumplist[jump] = -1
				ligne = re.split(identifier_regex+":\s*", ligne, 1)[1]
			include = ""
			
			if data != "":
				lignes_labelisees += [{"label":jump, "data": ligne}]
		return jumplist, variables, lignes_labelisees
	
	jumplist, variables, lignes_labelisees = secondpass(lines)
		
	if "start" not in jumplist:
		raise Exception("start symbol is needed !")
	
	if verbose:
		print("Jumplist :", jumplist)
		print("Variables : ", variables)
	#print(lignes_labelisees)
	
	relative_addresses = []
	
	for k,l in enumerate(lignes_labelisees):
		ligne = inst_split(l["data"])
		if verbose and (len(ligne) > 0 or l["label"] != ""):
			print(f"-------------\nLine {k+1}/{len(lignes_labelisees)}\n-------------")
		if l["label"] != "":
			if verbose:
				print(f'Label \033[1m{l["label"]}\033[0m found at {len(machine_code)}')
			#print(l)
			jumplist[l["label"]] = len(machine_code)
		if len(ligne) > 0:
			if verbose:
				print("\tASM : ", " ".join(ligne))
			if ligne[0] not in high_lvl_instructions:
				if hint_instruction := find_similar(ligne[0], list(high_lvl_instructions.keys())):
					print(f"\n\033[1m\033[36mHint:\033[0m Instruction \033[1m{ligne[0]}\033[0m is perhaps mispelled : \033[1m{hint_instruction}\033[0m found in the instruction set\n")

				raise UndefinedInstruction(f"{ligne[0]} does not exists in the instruction set !")
			instruction = high_lvl_instructions[ligne[0]]
			if verbose:
				print("\tInstruction: ", instruction["description"])
			args = ligne[1:]
			not_found_arg = ""
			for k,variant in enumerate(instruction["variants"]):
				variant = inst_split(variant)
				if len(variant) != len(args):
					if debug:
						print("len(variant) and len(args) don't match")
						print(args, variant)
					continue
				
				ok = True
				vals = []
				register_names = []
				uregister_names = []
				placeholders = []
				for i in range(len(variant)):
					if debug:
						print(f"{i} : Comparing {args[i]} to {variant[i]}")
					cur_arg = args[i]
					if cur_arg in variables.keys():
						cur_arg = variables[cur_arg]
					elif cur_arg in jumplist.keys():
						pass
					elif cur_arg in registers:
						pass
					elif re.match(identifier_regex, cur_arg):
						if hint_var := find_similar(cur_arg, list(variables.keys())):
							print(f"\n\033[1m\033[36mHint:\033[0m Variable name \033[1m{cur_arg}\033[0m is perhaps mispelled : \033[1m{hint_var}\033[0m found\n")
						raise UndefinedVar(f"{cur_arg} was not found and is not a jump label")

					relative_address = False
					if cur_arg[0] == "+":
						relative_address = True
						cur_arg = cur_arg[1:]
					base = 10
					if cur_arg[1:2+1] == "0x":
						base = 16
					if cur_arg[1:2+1] == "0b":
						base = 2
					if variant[i] == "%b" and cur_arg[0] == "#":
						placeholders += [int(cur_arg[1:], base)]
					elif cur_arg in registers and (variant[i] == "R" or variant[i] == cur_arg or cur_arg[0] == "U" and variant[i] == "U#"):
						if debug:
							print(f"Operand {i} is a register ({args[i]})")
						reg = cur_arg
						if variant[i] == "U#":
							uregister_names += [reg]
						elif variant[i] == "R":
							register_names += [reg]
					elif cur_arg[0] == variant[i][0] and variant[i][0] == "@":
						#print(args[i])
						vals += [(relative_address, int(cur_arg[1:], base))]
						if debug:
							print(f"Operand {i} is an address ({vals[-1]})")
					elif cur_arg[0] == "#" and cur_arg[0] == variant[i][0]:
						#print(args[i])
						vals += [int(cur_arg[1:], base)]
						if debug:
							print(f"Operand {i} is a value ({vals[-1]})")
					elif cur_arg in jumplist.keys() and variant[i][0] == "#":
						vals += [cur_arg]
					else:
						not_found_arg = cur_arg
						if debug:
							print("Couldn't find variant !", instruction["variants"][k], args)
						ok = False
						break
				#print(vals)
				if ok:
					def generate_mcode(real_instruction, params, register_names, uregister_names, vals, mcode_len, relative_addresses):
						mcode = []
						for placeholder in placeholders:
							real_instruction = real_instruction.replace("%b", str(placeholder), 1)
						for reg in register_names:	
							real_instruction = real_instruction.replace("_R", "_"+reg, 1)
						for reg in uregister_names:
							real_instruction = real_instruction.replace("_U#", "_"+reg, 1)
													  
						if verbose:
							print("\tReal instruction :", real_instruction, end=' ')
							print("("+hex(instructions_sorted.index(real_instruction))+")", end=' ')
							cursor = 0
							for param in params:
								val = ""
								if param == "??":
									val = vals[cursor]
									cursor += 1
								elif str(param)[0] == "$":
									val = vals[int(param[1:])-1]
								else:
									val = param
									
								if type(val) == int:
									val = hex(val)
								print(val, end=' ')
							print("")
						if debug:
							print("register_names :", register_names)
							print("uregister_names :", uregister_names)
						
						
						instruction_code = hex(instructions_sorted.index(real_instruction))[2:].zfill(8//4)
						mcode += [instruction_code]
						
						def _add_data(inst_data, mcode_len):
							mcode = []
							rel_addr = []
							if inst_data in jumplist:
								mcode += [inst_data]
							elif type(inst_data) == tuple: # means we have an address
								if inst_data[0]: # we have a relative address
									rel_addr += [len(mcode)+mcode_len]
									mcode += [inst_data[1]]
								else:
									mcode += [hex(inst_data[1])[2:].zfill(8//4)]
							else:
								mcode += [hex(inst_data)[2:].zfill(8//4)]
								
							if debug:
								print("_add_data:", "inst_data=", inst_data, "rel_addr=", rel_addr, "mcode=", mcode)
								
							return mcode, rel_addr
						
						cursor = 0
						for param in params:
							mcode_tmp, reladdr_tmp = [], []
							if debug:
								print("param:", param)
							val = ""
							if param == "??":
								val = vals[cursor]
								cursor += 1
							elif str(param)[0] == "$":
								val = vals[int(param[1:])-1]
							else:
								val = param
							if debug:
								print("val:", val)
							mcode_tmp, reladdr_tmp = _add_data(val, mcode_len+len(mcode))
							mcode += mcode_tmp
							relative_addresses += reladdr_tmp

						return mcode
								
					instruction_list = instruction['instructions'][k]
					params = instruction_list[1:]
					real_instruction = instruction_list[0]
					machine_code += generate_mcode(real_instruction, params, register_names, uregister_names, vals, len(machine_code), relative_addresses)
					
					
					if len(machine_code) > 2**address_bits:
						raise NotEnoughAddressableMemory(f"generated machine code is over {2**address_bits - 1} in size")
					break
				
			else: # else after a for, yes, very pythonic
				
				if not_found_arg != "":
					if jumpfound := find_similar(not_found_arg, list(jumplist.keys())):
						print(f"\n\033[1m\033[36mHint:\033[0m Label \033[1m{not_found_arg}\033[0m is perhaps mispelled : \033[1m{jumpfound}\033[0m found in the jumplist\n")
						
				raise UndefinedInstructionVariant(f"Instruction {ligne[0]} can't be used with given args")
	
	# We replace each relative address with an absolute one
	mcode_len = len(machine_code)
	rel_vars = {}
	for rel_addr in relative_addresses:
		#print(machine_code[rel_addr])
		new_addr = machine_code[rel_addr]+mcode_len
		rel_vars[new_addr] = rel_addr
		if verbose:
			print(f"\nVariable at {rel_addr} got its address transformed from {machine_code[rel_addr]} to {new_addr}")
		machine_code[rel_addr] = hex(new_addr)[2:].zfill(8//4)
	if verbose:
		print("\nJumplist (completed) :", jumplist)
		print("\nRelative addresses :", [hex(i) for i in list(rel_vars.keys())])
		
	# We use our completed jumplist to replace each occurence of a label by its actual address
	for i, m in enumerate(machine_code):
		if m in jumplist.keys():
			machine_code[i] = hex(jumplist[m])[2:].zfill(8//4)
		
	return " ".join(machine_code)

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="enable debug mode, activates verbose")
	parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="enable debug mode")
	parser.add_argument('-o', '--output', dest="output", metavar="OUTPUT_FILE", help="output file", default="ram.txt")
	parser.add_argument(metavar="INPUT_FILE", dest="input", help="input file", default="prog.crapasm")
	args = parser.parse_args()
	
	address_bits = 8
	
	with open(args.input, "r") as file:
		data = file.read()
		
	print(f"Assembly:\n{data}")
	
	print("================")
	
	mcode = assembler(data, address_bits, args.debug, args.verbose or args.debug)
	
	print("================")
	
	print(f"\033[1m\033[31mMachine-code:\033[0m \n{mcode}\n\n{len(mcode.split(' '))}/{(2**address_bits)} bytes of data")
	
	with open(args.output, "w") as file:
		file.write("v2.0 raw\n")
		file.write(mcode)