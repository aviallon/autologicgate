#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 15:27:22 2019

@author: aviallon
"""

from instructions import instructions, micro_inst, micro_inst_number, high_lvl_instructions, registers
		
def inst_to_micro_instructions(inst):
	mi_s = []
	if inst != "default":
		mi_s += instructions["default"] + instructions[inst]
	else:
		# print(instructions["default"])
		mi_s = instructions["default"].copy()
		mi_s += [["clearMIcounter"]]
	instruction_mis = {}
	micro_counter = 0x0
	for mi_line in mi_s:
		line = [0]*micro_inst_number
		for mi in mi_line:
			line[micro_inst[mi]] = 1
		instruction_mis[micro_counter] = line
		micro_counter += 0x1
	return instruction_mis

def gen_instructions():

    binary_inst = {}
    instruction_code = 0x01
    for inst in instructions:
    	if inst == "default":
    		continue
    	binary_inst[instruction_code] = inst_to_micro_instructions(inst)
    	instruction_code += 0x01
    	
    for i_code in range(0, 0xFF):
    	if binary_inst.get(i_code) is None:
    		binary_inst[i_code] = inst_to_micro_instructions("default")
    
    
    file1_lines = ["0"*(32//4)]*4096
    file2_lines = ["0"*(32//4)]*4096
    for inst in binary_inst:
    	line_prefix = inst
    	inst_mi = binary_inst[inst]
    	for mi in inst_mi:
    		#print(mi)
    		line_suffix = mi
    		line = (line_prefix << 4) + line_suffix
    		#print(bin(line)[2:].zfill(12))
    		bin_str = "0b"+"".join([str(i) for i in reversed(inst_mi[mi])])
    		hex_str = hex(int(bin_str, 2))[2:].zfill(micro_inst_number//4)
    		part2 = hex_str[:32//4]
    		part1 = hex_str[32//4:64//4]
    		file1_lines[line] = part1.zfill(32//4)
    		file2_lines[line] = part2.zfill(32//4)
    		
    file1_concat = "\n".join(file1_lines)
    file2_concat = "\n".join(file2_lines)
    
    with open("instructions1.txt", 'w') as file:
    	file.write("v2.0 raw\n")
    	file.write(file1_concat)
    	
    with open("instructions2.txt", 'w') as file:
    	file.write("v2.0 raw\n")
    	file.write(file2_concat)
    
def escape_for_marktex(string):
    escapelist = ["_", "**", "#"]
    for e in escapelist:
        string = string.replace(e, "\\"+e)
    return string
    

def gen_documentation():
    with open("description.Rmd", 'w') as file:
        file.write(
"""---
title: Crappy CPU machine code equivalence
author: Antoine {\scshape Viallon}
date: \\today
---

# Registers
_Available registers :_

- `A`: multi-purpose register. Is not overwriten quietly.
- `B`: work register. Used in many operations as a buffer
- `U\#`: user registers. Will **never** be overwritten unless _explicitely_ mentionned (see the instructions for more detail). There are only 1 of those currently.
- `ret`: not directly accessible. Used with `CALL` and `RET`
- `cmp`: not directly accessible. Used with `CMP` and `JMPxxx`

# High level instructions
""")
        for i,inst in enumerate(high_lvl_instructions):
            inst_paragraph = f"## {escape_for_marktex(inst)}\n"
            inst_paragraph += f"_{escape_for_marktex(high_lvl_instructions[inst]['description'])}_\n"
            for j,variant in enumerate(high_lvl_instructions[inst]["variants"]):
                size = len(high_lvl_instructions[inst]['instructions'][j])
                low_inst_name = high_lvl_instructions[inst]['instructions'][j][0].replace("_R", "_A")
                duration = len(instructions[low_inst_name]) + len(instructions["default"])
                inst_paragraph += f"- `{escape_for_marktex(inst)} {escape_for_marktex(variant)}` (size: {size}, duration: {duration})\n"
            inst_paragraph += "\n\n"
            file.write(inst_paragraph)
            
        file.write(
"""
# Instructions (low level)
""")
        for i,inst in enumerate(instructions):
            code = hex(i)[2:].zfill(8//4)
            inst_paragraph = f"#### {escape_for_marktex(inst)} : `0x{code}`\n_Micro-instructions :_\n"
            for i,mi_line in enumerate(instructions[inst]):
                inst_paragraph += f"{i}. "
                for i,mi in enumerate(mi_line):
                    inst_paragraph += f"`{escape_for_marktex(mi)}`"
                    if i != len(mi_line) - 1:
                        inst_paragraph += ", "
                inst_paragraph += " <br>\n"
            file.write(inst_paragraph)
            
        file.write("\n")
        import os
        os.system("~/bin/marktex -c description.Rmd")
        
        

if __name__ == "__main__":
    gen_instructions()
    print("Done writing instructions files !")
    gen_documentation()
    print("Done writing documentation files !")