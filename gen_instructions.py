#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 15:27:22 2019

@author: aviallon
"""

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
	  "loadRet":13,
	  "outRet":14,
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
	  "enableAND":35
	  }

instructions = {
		"default":[
					["outPC", "loadRAM"],
					["outRAM", "loadInstruction", "incPC"],
				],
		"LOAD_const_to_A":[ # 0x01
					["outPC", "loadRAM"],
					["outRAM", "loadA", "incPC"],
					["clearMIcounter"]
				],
		"HALT":[ # 0x02
				["halt"]
				],
		"ADD_direct":[ # 0x03
				["outPC", "loadRAM"],
				["outRAM", "loadA", "incPC"],
				["outPC", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["enableAdd", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"ADD_mem":[ # 0x04
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadA", "incPC"],
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["loadALU", "enableAdd"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"ADD_const_toA": [ # 0x05
				["outPC", "loadRAM"],
				["outRAM", "loadB"],
				["enableAdd", "loadALU"],
				["outALU", "loadA", "incPC"],
				["clearMIcounter"]
				],
		"JMP":[ # 0x06
				["outPC", "loadRAM"],
				["outRAM", "loadPC", "cond_always"],
				["clearMIcounter"]
			],
		"NEG_A":[ # 0x07
				["outA", "enableNOT", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"LOAD_const_toB":[ # 0x08
				["outPC", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["clearMIcounter"]
				],
		"MOVE_B_to_A": [ # 0x09
				["outB", "loadA"],
				["clearMIcounter"]
				],
		"MOVE_A_to_B": [ # 0x0A
				["outA", "loadB"],
				["clearMIcounter"]
				],
		"NEG_B": [ # 0x0B
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["clearMIcounter"]
				],
		"SUB_to_A": [ # 0x0C
				["outPC", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"CMP_A_mem": [ # 0x0D
				["outPC", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU"],
				["outALU", "loadCmp"],
				["clearMIcounter"]
				],
		"JMP_if_A_lt_B": [ # 0x0E
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_neg", "cond_not_null"],
				["clearMIcounter"]
				],
		"JMP_if_A_gt_B": [ # 0x0F
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_pos", "cond_not_null"],
				["clearMIcounter"]
				],
		"JMP_if_A_eq_B": [ # 0x10
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_null"],
				["clearMIcounter"]
				],
		"JMP_if_A_neq_B": [ # 0x11
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_null", "invert_cond"],
				["clearMIcounter"]
				],
		"JMP_if_A_le_B": [ # 0x12
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_neg", "cond_null"],
				["clearMIcounter"]
				],
		"JMP_if_A_ge_B": [ # 0x13
				["outPC", "loadRAM"],
				["incPC"],
				["outRAM", "loadPC", "cond_pos", "cond_null"],
				["clearMIcounter"]
				],
		"LOAD_ptr_to_A": [ # 0x14
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadA"],
				["clearMIcounter"]
				],
		"LOAD_ptr_to_B": [ # 0x15
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadB"],
				["clearMIcounter"]
				],
		"STORE_B_to_address":[ #0x16
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["storeRAM", "outB"],
				["clearMIcounter"]
				],
		"STORE_A_to_address":[ #0x17
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["storeRAM", "outA"], # when storeRAM is activated, it automatically outputs the content of the mem addr register to the mem addr bus
				["clearMIcounter"]
				],
		"STORE_PCp1_to_address":[ #0x18
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["storeRAM", "outPCp1"],
				["clearMIcounter"]
				],
		"INC_A": [ # 0x19
				["outA", "enableInc", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"CALL_addr": [ # 0x1A
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outPC", "loadRet"],
				["loadPC", "cond_always", "outMemAddr"],
				["clearMIcounter"]
				],
		"RET": [ # 0x1B
				["outRet", "loadPC", "cond_always"],
				["clearMIcounter"]
				],
		"ADD_mem_toA": [ # 0x1C
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["loadRAM", "outMemAddr"],
				["outRAM", "loadB"],
				["enableAdd", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"XOR_A_B_toA": [ # 0x1D
				["enableXOR", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"XOR_A_toA": [ # 0x1E
				["outA", "loadB"],
				["enableXOR", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"COPY": [ # 0x1F
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadB"],
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["storeRAM", "outB"],
				["clearMIcounter"]
				],
		"OR_A_B_toA": [ # 0x20
				["enableOR", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"AND_A_B_toA": [ # 0x21
				["enableAND", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"SHIFTL_A": [ # 0x22
				["outA", "enableSHIFTL", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"SHIFTL_B": [ # 0x23
				["outB", "enableSHIFTL", "loadALU"],
				["outALU", "loadB"],
				["clearMIcounter"]
				],
		"SHIFTR_A": [ # 0x24
				["outA", "enableSHIFTR", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"SHIFTR_B": [ # 0x25
				["outB", "enableSHIFTR", "loadALU"],
				["outALU", "loadB"],
				["clearMIcounter"]
				],
		}
		
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
	
print("Done writing file !")