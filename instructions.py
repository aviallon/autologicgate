#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:46:42 2020

@author: aviallon
"""

if "DEBUG" not in globals() and "DEBUG" not in locals():
	DEBUG = False
	
if __name__ == "__main__":
	DEBUG = True

micro_inst_number = 64

micro_inst = {
	  "incPC":1,
	  "halt":0,
	  "loadRAM":2,
	  "outPC":3,
	  "outRAM":4,
	  "loadA":5,
	  "loadB":6,
	  "clearMIcounter":7,
	  "enableAdd":8,
	  "outALU":9,
	  "loadInstruction":10,
	  "loadMemAddr":11,
	  "outMemAddr":12,
	  "incRet":13,
	  "outRetAddr":14,
	  "loadPC":15,
	  "outA":16,
	  "outB":17,
	  "enableNOT":18,
	  "loadALU":19,
	  "loadCmp":20,
	  "outCmp":21,
	  "outPCp1":22,
	  "enableXOR":23,
	  "cond_always":24,
	  "cond_neg":25,
	  "cond_null":26,
	  "invert_cond":27,
	  "enableInc":28,
	  "cond_not_null":29,
	  "cond_pos":30,
	  "storeRAM":31,
	  "enableOR":32,
	  "enableSHIFTL":33,
	  "enableSHIFTR":34,
	  "enableAND":35,
	  "outU0":36,
	  "loadU0":37,
	  "selector0":38,
	  "selector1":39,
	  "selector2":40,
	  "cond_selected_bit":41,
	  "loadU1":42,
	  "outU1":43,
	  "loadU2":44,
	  "outU2":45,
	  "loadU3":46,
	  "outU3":47,
	  "flipLed":48,
	  "loadDisplay":49,
	  "loadC":50,
	  "cond_C":51,
	  "enableDEC":52,
	  "loadSleep":53,
	  "decRet":54,
	  "error":63
	  }

registers = ["A", "B", "U0", "U1", "U2", "U3"]

instructions = {
		"default":[
				["outPC", "loadRAM"],
				["outRAM", "loadInstruction", "incPC"],
				],
		"HALT":[ # 0x02
				["halt"]
				],
		"ADD_const_to_const_in_A":[ # 0x03
				["outPC", "loadRAM"],
				["outRAM", "loadA", "incPC"],
				["outPC", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["enableAdd", "loadALU", "outA"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"ADD_mem_to_mem":[ # 0x04
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadA", "incPC"],
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["loadALU", "enableAdd", "outA"],
				["outALU", "storeRAM"],
				["clearMIcounter"]
				],
		"JMP_const":[ # 0x06
				["outPC", "loadRAM"],
				["outRAM", "loadPC", "cond_always"],
				["clearMIcounter"]
				],
		"JMP_if_lt": [ # 0x0E
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_neg", "cond_not_null"],
				["clearMIcounter"]
				],
		"JMP_if_gt": [ # 0x0F
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_pos", "cond_not_null"],
				["clearMIcounter"]
				],
		"JMP_if_eq": [ # 0x10
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_null"],
				["clearMIcounter"]
				],
		"JMP_if_neq": [ # 0x11
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_null", "invert_cond"],
				["clearMIcounter"]
				],
		"JMP_if_le": [ # 0x12
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_neg", "cond_null"],
				["clearMIcounter"]
				],
		"JMP_if_ge": [ # 0x13
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_pos", "cond_null"],
				["clearMIcounter"]
				],
		"STORE_PCp1_to_address":[ #0x18
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["storeRAM", "outPCp1"],
				["clearMIcounter"]
				],
		"CALL_addr": [ # 0x1A
				["outRetAddr", "loadMemAddr"], # MemAddr pointe vers l'adresse de sauvegarde de la pile d'éxécution
				["outPCp1", "storeRAM", "incRet"], # on a sauvegardé l'adresse
				["outPC", "loadRAM"], # on charge la nouvelle adresse
				["outRAM", "loadMemAddr"], # B stocke l'adresse de destination,
				["loadPC", "cond_always", "outMemAddr"],
				["clearMIcounter"]
				],
		"RET": [ # 0x1B
				["decRet"],
				["outRetAddr", "loadRAM"], # on charge l'ancienne adresse
				["outRAM", "loadPC", "cond_always"], # on remplace le PC et on dépile
				["clearMIcounter"]
				],
		"XOR_A_B_to_A": [ # 0x1D
				["enableXOR", "loadALU", "outA"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"COPY_mem": [ # 0x1F
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"], # on charge l'addresse de la variable stockée dans Mem Addr
				["outMemAddr", "loadRAM"], # et on y va
				["outRAM", "loadB"],
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["storeRAM", "outB"],
				["clearMIcounter"]
				],
		"STORE_const_to_address": [ # 0x26
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outPC", "loadRAM"],
				["storeRAM", "outRAM", "incPC"],
				["clearMIcounter"]
				],
		"INC_mem": [ # 0x28
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outMemAddr", "loadRAM"],
				["outRAM", "enableInc", "loadALU"],
				["outALU", "storeRAM"],
				["clearMIcounter"]
				],
		"NOP": [ # 0x29
				["clearMIcounter"]
				],
		"JMP_ptr":[ # 0x2A
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadPC", "cond_always"],
				["clearMIcounter"]
			],
		"CMP_A_B": [ # 0x2B
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU", "outA"],
				["outALU", "loadCmp"],
				["clearMIcounter"]
				],
		"NEG_mem": [ # 0x2F
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr"],
				["outMemAddr", "loadRAM", "incPC"],
				["outRAM", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "storeRAM"],
				["clearMIcounter"]
				],
		"XOR_B_to_B": [ # 0x30
				["enableXOR", "loadALU", "outB"],
				["outALU", "loadB"],
				["clearMIcounter"]
				],
		"COPY_mem_to_cmp": [
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadCmp"],
				["clearMIcounter"]
				],
		"LED_tgl": [
				["flipLed"],
				["clearMIcounter"]
				],
		"FAIL": [
				["error", "halt"]
				],
		"ADD_const_to_mem": [ 
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["loadRAM", "outMemAddr"],
				["outRAM", "loadB"],
				["outPC", "loadRAM"],
				["enableAdd", "loadALU", "outRAM", "incPC"],
				["outALU", "storeRAM"],
				["clearMIcounter"]
				],
		"DISPLAY_mem": [
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["loadRAM", "outMemAddr"],
				["outRAM", "loadDisplay"],
				["clearMIcounter"]
				],
		"SLEEP_const": [
				["outPC", "loadRAM"],
				["outRAM", "loadSleep", "incPC"],
				["clearMIcounter"]
				],
		"SLEEP_mem": [
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["loadRAM", "outMemAddr"],
				["outRAM", "loadSleep"],
				["clearMIcounter"]
				],
		"SUB_B_to_A": [
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU", "outA"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		}

templates = {
		"JMP_sel_bit_%d": [ 
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_selected_bit", "%dd"],
				["clearMIcounter"],
				],
		"JMP_not_sel_bit_%d": [ 
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_selected_bit", "invert_cond", "%dd"],
				["clearMIcounter"],
				],
		"LOAD_ptr_to_%RB": [ 
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outMemAddr", "loadRAM"],
				["outRAM", "load%RB"],
				["clearMIcounter"]
				],
		"XOR_%R_to_%R": [ 
				["out%R", "loadB"],
				["enableXOR", "loadALU", "out%R"],
				["outALU", "load%R"],
				["clearMIcounter"]
				],
		"STORE_%RB_to_address":[ 
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["storeRAM", "out%RB"],
				["clearMIcounter"]
				],
		"COPY_A_to_%U": [ 
				["outA", "load%U"],
				["clearMIcounter"]
				],
		"COPY_B_to_%RB": [
				["outB", "load%RB"],
				["clearMIcounter"]
				],
		"COPY_%RB_to_A": [ 
				["out%RB", "loadA"],
				["clearMIcounter"]
				],
		"COPY_%RB_to_B": [ 
				["out%RB", "loadB"],
				["clearMIcounter"]
				],
		"COPY_%RB_to_cmp": [
				["out%RB", "loadCmp"],
				["clearMIcounter"]
				],
		"LOAD_const_to_%RB": [ 
				["outPC", "loadRAM"],
				["outRAM", "load%RB", "incPC"],
				["clearMIcounter"]
				],
		"ADD_mem_to_%R": [ 
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["loadRAM", "outMemAddr"],
				["outRAM", "loadB"],
				["enableAdd", "loadALU", "out%R"],
				["outALU", "load%R"],
				["clearMIcounter"]
				],
		"ADD_B_to_%R": [
				["enableAdd", "loadALU", "out%R"],
				["outALU", "load%R"],
				["clearMIcounter"]
				],
		"ADD_A_to_%R": [
				["outA", "loadB"],
				["enableAdd", "loadALU", "out%R"],
				["outALU", "load%R"],
				["clearMIcounter"]
				],
		"ADD_%U_to_A": [
				["out%U", "loadB"],
				["enableAdd", "loadALU", "outA"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"ADD_%R_to_mem": [ 
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["loadRAM", "outMemAddr"],
				["outRAM", "loadB"],
				["enableAdd", "loadALU", "out%R"],
				["outALU", "storeRAM"],
				["clearMIcounter"]
				],
		"ADD_const_to_%R": [ # 0x05
				["outPC", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["enableAdd", "loadALU", "out%R"],
				["outALU", "load%R"],
				["clearMIcounter"]
				],
		"NOT_%RB": [ 
				["enableNOT", "loadALU", "out%RB"],
				["outALU", "load%RB"],
				["clearMIcounter"]
				],
		"NEG_%RB": [ 
				["out%RB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "load%RB"],
				["clearMIcounter"]
				],
		"SHIFTL_%RB": [ 
				["out%RB", "enableSHIFTL", "loadALU"],
				["outALU", "load%RB"],
				["clearMIcounter"]
				],
		"SHIFTR_%RB": [ 
				["out%RB", "enableSHIFTR", "loadALU"],
				["outALU", "load%RB"],
				["clearMIcounter"]
				],
		"INC_%RB": [ 
				["out%RB", "enableInc", "loadALU"],
				["outALU", "load%RB"],
				["clearMIcounter"]
				],
		"OR_%R_B_to_itself": [ 
				["enableOR", "loadALU", "out%R"],
				["outALU", "load%R"],
				["clearMIcounter"]
				],
		"AND_%R_B_to_itself": [ 
				["enableAND", "loadALU", "out%R"],
				["outALU", "load%R"],
				["clearMIcounter"]
				],
		"CMP_A_%U": [ 
				["out%U", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU", "outA"],
				["outALU", "loadCmp"],
				["clearMIcounter"]
				],
		"CMP_%U_A": [ 
				["outA", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU", "out%U"],
				["outALU", "loadCmp"],
				["clearMIcounter"]
				],
		"CMP_%R_const": [ 
				["outPC", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU", "out%R"],
				["outALU", "loadCmp"],
				["clearMIcounter"]
				],
		"CMP_%R_mem": [
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadB"],
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU", "out%R"],
				["outALU", "loadCmp"],
				["clearMIcounter"]
				],
		"SUB_mem_to_%R": [
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadB"],
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU", "out%R"],
				["outALU", "load%R"],
				["clearMIcounter"]
				],
		"SUB_%R_to_A": [
				["out%R", "loadB"],
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU", "outA"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"DISPLAY_%RB": [
				["out%RB", "loadDisplay"],
				["clearMIcounter"]
				],
		"SLEEP_%RB": [
				["out%RB", "loadSleep", "incPC"],
				["clearMIcounter"]
				],
		}

from copy import deepcopy
for key in templates.keys():
	template = templates[key]
	generated = []
	if "%d" in key:
		nbits = 3
		for i in range(0, 2**nbits):
			bits = []
			i_bin = bin(i)[2:].zfill(nbits)
			for k in range(nbits):
				if i_bin[nbits-k-1] == "1":
					bits.append(f"selector{k}")
			cur_gen = deepcopy(template)
			for j, micro_instruction_line in enumerate(cur_gen):
				if "%dd" in micro_instruction_line:
					cur_gen[j].remove("%dd")
					cur_gen[j] += bits
			instruction_name = key.replace("%d", str(i))
			generated += [(instruction_name, cur_gen)]
	elif "%U" in key:
		n_uregs = 4
		for n_u in range(n_uregs):
			cur_gen = deepcopy(template)
			for j, micro_instruction_line in enumerate(cur_gen):
				for k, mi in enumerate(micro_instruction_line):
					cur_gen[j][k] = mi.replace("%U", f"U{n_u}")
			instruction_name = key.replace("%U", f"U{n_u}")
			generated += [(instruction_name, cur_gen)]
	elif "%RB" in key:
		for reg in registers:
			cur_gen = deepcopy(template)
			for j, micro_instruction_line in enumerate(cur_gen):
				for k, mi in enumerate(micro_instruction_line):
					cur_gen[j][k] = mi.replace("%RB", f"{reg}")
			instruction_name = key.replace("%RB", f"{reg}")
			generated += [(instruction_name, cur_gen)]
			
	elif "%R" in key:
		for reg in registers:
			if reg == "B":
				continue
			cur_gen = deepcopy(template)
			for j, micro_instruction_line in enumerate(cur_gen):
				for k, mi in enumerate(micro_instruction_line):
					cur_gen[j][k] = mi.replace("%R", f"{reg}")
			instruction_name = key.replace("%R", f"{reg}")
			generated += [(instruction_name, cur_gen)]
					
	for gen in generated:
		if DEBUG:
			print(f"Generated {gen[0]}...")
		instructions[gen[0]] = gen[1]

if DEBUG:
	print(f"{len(instructions)}/{2**8} instructions in total !")
		
if len(instructions) > 256:
	raise ValueError("Too many instructions !")

high_lvl_instructions = {
		"ADD":
			{
				"variants": ["A, U#", "R, B", "R, A", "R, @0xHH", "R, #0xHH", "@0xHH, @0xHH", "@0xHH, R", "#0xHH, #0xHH", "@0xHH, #0xHH"],
				"instructions":[
						 ["ADD_U#_to_A"],
						 ["ADD_B_to_R"],
						 ["ADD_A_to_R"],
						 ["ADD_mem_to_R", "??"],
						 ["ADD_const_to_R", "??"],
						 ["ADD_mem_to_mem", "??", "??"],
						 ["ADD_R_to_mem", "??"],
						 ["ADD_const_to_const_in_A", "??", "??"],
						 ["ADD_const_to_mem", "??", "??"]
						 ],
				"description":"Add a value from a register/memory address/const to a register or a memory address and save it in register A"
			 },
		"SUB":
			{
				"variants": ["R, @0xHH", "A, R"],
				"instructions":[
						 ["SUB_mem_to_R", "??"],
						 ["SUB_R_to_A"]
						 ],
				"description":"Sub a value from a memory/register to register A and save it in register A. Overwrites B."
			 },
		"NEG":
			{
				"variants": ["R", "@0xHH"],
				"instructions":[
						 ["NEG_R"],
						 ["NEG_mem", "??"]
						 ],
				"description":"Compute two's complement of register/memory (useful for substractions), and store result in itself."
			 },
		"MOV":
			{
				"variants": ["A, R", "B, R", "U#, A", "U#, B", "R, @0xHH", "R, #0xHH", "@0xHH, R", "@0xHH, @0xHH", "@0xHH, #0xHH"],
				"instructions":[
						 ["COPY_R_to_A"],
						 ["COPY_R_to_B"],
						 ["COPY_A_to_U#"],
						 ["COPY_B_to_U#"],
						 ["LOAD_ptr_to_R", "??"],
						 ["LOAD_const_to_R", "??"],
						 ["STORE_R_to_address", "??"],
						 ["COPY_mem", "$2", "$1"],
						 ["STORE_const_to_address", "??", "??"]
						 ],
				"description":"Move a value from a register/memory address/const to a register or a memory address"
			 },
		"DISP":
			{
				"variants": ["R", "@0xHH"],
				"instructions":[
						 ["DISPLAY_R"],
						 ["DISPLAY_mem", "??"]
						 ],
				"description":"Display a value contained in specified register/memory address as an unsigned integer."
			 },
		"XOR":
			{
				"variants": ["A, B", "A, A", "U#, U#"],
				"instructions":[
						 ["XOR_A_B_to_A"],
						 ["XOR_A_to_A"],
						 ["XOR_U#_to_U#"]
						 ],
				"description":"XOR two registers, save the result to the first operand"
			 },
		"CLR":
			{
				"variants": ["A", "U#", "@0xHH"],
				"instructions":[
						 ["XOR_A_to_A"],
						 ["XOR_U#_to_U#"],
						 ["STORE_const_to_address", 0x00, "??"]
						 ],
				"description":"Clear a register address."
			 },
		"OR":
			{
				"variants": ["A, B", "U#, B"],
				"instructions":[
						 ["OR_A_B_to_itself"],
						 ["OR_U#_B_to_itself"]
						 ],
				"description":"OR two registers, save the result to the first operand"
			 },
		"AND":
			{
				"variants": ["R, B"],
				"instructions":[
						 ["AND_R_B_to_itself"],
						 ],
				"description":"AND two registers, save the result to the first operand"
			 },
		"NOT":
			{
				"variants": ["R"],
				"instructions":[
						 ["NOT_R"],
						 ],
				"description":"Invert bit by bit register, and store result in itself"
			 },
		"INC":
			{
				"variants": ["R", "@0xHH"],
				"instructions":[
						 ["INC_R"],
						 ["INC_mem", "??"]
						 ],
				"description":"Increment register or value at memory address"
			 },
		"SHIFTL":
			{
				"variants": ["R"],
				"instructions":[
						 ["SHIFTL_R"]
						 ],
				"description":"Shift register to the left"
			 },
		"SHIFTR":
			{
				"variants": ["R"],
				"instructions":[
						 ["SHIFTR_R"]
						 ],
				"description":"Shift register to the right"
			 },
		"NOP":
			{
				"variants": [""],
				"instructions":[
						 ["NOP"],
						 ],
				"description":"Go to next address"
			 },
		"LEDTGL":
			{
				"variants": [""],
				"instructions":[
						 ["LED_tgl"],
						 ],
				"description":"Toggle led. Useful for debugging."
			 },
		"JMP":
			{
				"variants": ["@0xHH", "#0xHH"],
				"instructions":[
						 ["JMP_ptr", "??"],
						 ["JMP_const", "??"]
						 ],
				"description":"Go to specified address"
			 },
		"CMP":
			{
				"variants": ["R, @0xHH", "A, B", "A, U#", "R, #0xHH", "U#, A", "R", "@0xHH"],
				"instructions":[
						 ["CMP_R_mem", "??"],
						 ["CMP_A_B"],
						 ["CMP_A_U#"],
						 ["CMP_R_const", "??"],
						 ["CMP_U#_A"],
						 ["COPY_R_to_cmp"],
						 ["COPY_mem_to_cmp", "??"]
						 ],
				"description":"Compare two values (substracts them) and store the result in CMP register. Overwrites B."
			 },
		"JMPPTR":
			{
				"variants": ["@0xHH"],
				"instructions":[
						 ["JMP_ptr", "??"],
						 ],
				"description":"Go to address value at memory address."
			 },
		"JMPEQ":
			{
				"variants": ["#0xHH"],
				"instructions":[
						 ["JMP_if_eq", "??"],
						 ],
				"description":"Go to specified address if comparison register is zero."
			 },
		"JMPNEQ":
			{
				"variants": ["#0xHH"],
				"instructions":[
						 ["JMP_if_neq", "??"],
						 ],
				"description":"Go to specified address if comparison register is NOT zero."
			 },
		"JMPLT":
			{
				"variants": ["#0xHH"],
				"instructions":[
						 ["JMP_if_lt", "??"],
						 ],
				"description":"Go to specified address if comparison register is strictly negative."
			 },
		"JMPLE":
			{
				"variants": ["#0xHH"],
				"instructions":[
						 ["JMP_if_le", "??"],
						 ],
				"description":"Go to specified address if comparison register is negative or zero."
			 },
		"JMPGT":
			{
				"variants": ["#0xHH"],
				"instructions":[
						 ["JMP_if_gt", "??"],
						 ],
				"description":"Go to specified address if comparison register is strictly positive."
			 },
		"JMPGE":
			{
				"variants": ["#0xHH"],
				"instructions":[
						 ["JMP_if_ge", "??"],
						 ],
				"description":"Go to specified address if comparison register is positive (or zero)."
			 },
		"JMPBIT":
			{
				"variants": ["%b, #0xHH"],
				"instructions":[
						 ["JMP_sel_bit_%b", "??"],
						 ],
				"description":"Go to specified address if selected bit of comparison register is 1."
			 },
		"JMPNBIT":
			{
				"variants": ["%b, #0xHH"],
				"instructions":[
						 ["JMP_not_sel_bit_%b", "??"],
						 ],
				"description":"Go to specified address if selected bit of comparison register is 0."
			 },
		"CALL":
			{
				"variants": ["#0xHH"],
				"instructions":[
						 ["CALL_addr", "??"],
						 ],
				"description":"Jump to specified address and save current PC in Ret register. Useful for subroutines."
			 },
		"RET":
			{
				"variants": [""],
				"instructions":[
						 ["RET"],
						 ],
				"description":"Revert PC to value saved in Ret register. Use with `CALL`."
			 },
		"HALT":
			{
				"variants": [""],
				"instructions":[
						 ["HALT"],
						 ],
				"description":"Halt the CPU"
			},
		"ABRT":
			{
				"variants": [""],
				"instructions":[
						["FAIL"],
						],
				"description":"Set error bit and halt"
			},
		"SLEEP":
			{
				"variants": ["R", "#0xHH", "@0xHH"],
				"instructions":[
						["SLEEP_R"],
						["SLEEP_const"],
						["SLEEP_mem"]
						],
				"description":"Pause clock for specified amount of ticks"
			},
		}
high_lvl_instructions_ordered = sorted(high_lvl_instructions.keys())
instructions_sorted = ["default"] + sorted(list(instructions.keys())[1:])