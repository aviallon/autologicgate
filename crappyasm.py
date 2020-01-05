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

class NotEnoughAddressableMemory(Error):
	pass

def inst_split(string):
	ligne = re.split("(\s+)|,", string)
	return list(filter(lambda x: x is not None and x != " " and x != "", ligne))

def assembler(data, address_bits=8):
	jumplist = {}
	variables = {}
	machine_code = []
	lines = data.split("\n")
	lignes_labelisees = []
	for i,l in enumerate(lines):
		ligne = l.strip("\t").strip(" ")
		ligne = re.split(";.*", ligne)[0]
		regex = "byte\s+([a-zA-Z][a-zA-Z0-9_]*)\s+((?:[\#@](?:0x)?[0-9A-Fa-f]+)|U[0-3]|A|B)"
		if temp := re.findall(regex, ligne):
			print(temp)
			variables[temp[0][0]] = temp[0][1]
			ligne = re.split("byte\s+[a-zA-Z][a-zA-Z0-9_]*\s+(?:[\#@](?:0x)?[0-9A-Fa-f]+)|U[0-3]|A|B", ligne, 1)[1]
		jump = ""
		if temp := re.findall("([a-zA-Z][a-zA-Z0-9_]+):\s*", ligne):
			jump = temp[0]
			jumplist[jump] = -1
			ligne = re.split("[a-zA-Z][a-zA-Z0-9_]+:\s*", ligne, 1)[1]
		
		if data != "":
			lignes_labelisees += [{"label":jump, "data": ligne}]
		
	print("Jumplist :", jumplist)
	print("Variables : ", variables)
	#print(lignes_labelisees)
	
	for k,l in enumerate(lignes_labelisees):
		ligne = inst_split(l["data"])
		if len(ligne) > 0 or l["label"] != "":
			print(f"-------------\nLine {k+1}/{len(lignes_labelisees)}\n-------------")
		if l["label"] != "":
			print(f'Label \033[1m{l["label"]}\033[0m found at {len(machine_code)}')
			#print(l)
			jumplist[l["label"]] = len(machine_code)
		if len(ligne) > 0:
			print("\tASM : ", " ".join(ligne))
			if ligne[0] not in high_lvl_instructions:
				raise UndefinedInstruction(f"{ligne[0]} does not exists in the instruction set !")
			instruction = high_lvl_instructions[ligne[0]]
			print("\tInstruction: ", instruction["description"])
			args = ligne[1:]
			not_found_arg = ""
			for k,variant in enumerate(instruction["variants"]):
				variant = inst_split(variant)
				if len(variant) != len(args):
					print("too short")
					print(args, variant)
					continue
				
				ok = True
				vals = []
				register_names = []
				uregister_names = []
				placeholders = []
				for i in range(len(variant)):
					print(f"{i} : Comparing {args[i]} to {variant[i]}")
					cur_arg = args[i]
					if cur_arg in variables.keys():
						cur_arg = variables[cur_arg]
					
					base = 10
					if cur_arg[1:2+1] == "0x":
						base = 16
					if cur_arg[1:2+1] == "0b":
						base = 2
					if variant[i] == "%b" and cur_arg[0] == "#":
						placeholders += [int(cur_arg[1:], base)]
					elif cur_arg in registers and (variant[i] == "R" or variant[i] == cur_arg or cur_arg[0] == "U" and variant[i] == "U#"):
						#print(f"Operand {i} is a register ({args[i]})")
						reg = cur_arg
						if variant[i] == "U#":
							uregister_names += [reg]
						elif variant[i] == "R":
							register_names += [reg]
					elif cur_arg[0] == variant[i][0] and variant[i][0] == "@":
						#print(args[i])
						vals += [int(cur_arg[1:], base)]
						#print(f"Operand {i} is an address ({vals[-1]})")
					elif cur_arg[0] == "#" and cur_arg[0] == variant[i][0]:
						#print(args[i])
						vals += [int(cur_arg[1:], base)]
						#print(f"Operand {i} is a value ({vals[-1]})")
					elif cur_arg in jumplist.keys() and variant[i][0] == "#":
						vals += [cur_arg]
					else:
						not_found_arg = cur_arg
						print("Couldn't find variant !", instruction["variants"][k], args)
						ok = False
						break
				#print(vals)
				if ok:
					def generate_mcode(real_instruction, register_names, uregister_names, vals):
						mcode = []
						for placeholder in placeholders:
							real_instruction = real_instruction.replace("%b", str(placeholder), 1)
						for reg in register_names:	
							real_instruction = real_instruction.replace("_R", "_"+reg, 1)
						for reg in uregister_names:
							real_instruction = real_instruction.replace("_U#", "_"+reg, 1)
													  
						print("\tReal instruction :", real_instruction, end=' ')
						for val in vals:
							if type(val) == int:
								val = hex(val)
							print(val, end=' ')
						print("")
						#print("register_names :", register_names)
						#print("uregister_names :", uregister_names)
						
						
						instruction_code = hex(instructions_sorted.index(real_instruction))[2:].zfill(8//4)
						mcode += [instruction_code]
						for inst_data in vals:
							if inst_data in jumplist:
								mcode += [inst_data]
							else:
								mcode += [hex(inst_data)[2:].zfill(8//4)]
						return mcode
								
					parent = instruction['instructions'][k]
					if type(parent) == tuple:
						for t, real_instruction_dad in enumerate(parent):
							real_instruction = real_instruction_dad[0]
							if t == len(parent) - 1:
								machine_code += generate_mcode(real_instruction, register_names, uregister_names, vals)
							else:
								machine_code += generate_mcode(real_instruction, [], [], [])
					else:
						real_instruction = parent[0]
						machine_code += generate_mcode(real_instruction, register_names, uregister_names, vals)
					
					
					if len(machine_code) > 2**address_bits:
						raise NotEnoughAddressableMemory(f"generated machine code is over {2**address_bits - 1} in size")
					break
				
			else: # else after a for, yes, very pythonic
				if not_found_arg != "":
					found = True
					jumpfound = ""
					x = 2
					while found:
						found = False
						key = 0
						#print("test")
						while key < len(jumplist.keys()):
							#print(key, list(jumplist.keys())[key])
							if not_found_arg[:x] in list(jumplist.keys())[key]:
								found = True
								break
							key += 1
						
						if found:
							jumpfound = list(jumplist.keys())[key]
						x += 1
						if x > len(not_found_arg):
							break
					#print(found, jumpfound, x, cur_arg[:x])
					if jumpfound != "":
						print(f"\n\033[1m\033[36mHint:\033[0m Label \033[1m{not_found_arg}\033[0m is perhaps mispelled : \033[1m{jumpfound}\033[0m found in the jumplist\n")
						
				raise UndefinedInstructionVariant(f"Instruction {ligne[0]} can't be used with given args")
					
				  
	print("\nJumplist (completed) :", jumplist)
	for i, m in enumerate(machine_code):
		if m in jumplist.keys():
			machine_code[i] = hex(jumplist[m])[2:].zfill(8//4)
		
	return " ".join(machine_code)

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--output', dest="output", metavar="OUTPUT_FILE", help="output file", default="ram.txt")
	parser.add_argument(metavar="INPUT_FILE", dest="input", help="input file", default="prog.crapasm")
	args = parser.parse_args()
	
	address_bits = 8
	
	with open(args.input, "r") as file:
		data = file.read()
		
	print(f"Assembly:\n{data}")
	
	print("================")
	
	mcode = assembler(data, address_bits)
	
	print("================")
	
	print(f"\033[1m\033[31mMachine-code:\033[0m \n{mcode}\n\n{len(mcode.split(' '))}/{(2**address_bits)} bytes of data")
	
	with open(args.output, "w") as file:
		file.write("v2.0 raw\n")
		file.write(mcode)