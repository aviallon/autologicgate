#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:46:42 2020

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
	  "enableAND":35,
      "outU":36,
      "loadU":37
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
		"ADD_const_to_A": [ # 0x05
				["outPC", "loadRAM"],
				["outRAM", "loadB"],
				["enableAdd", "loadALU"],
				["outALU", "loadA", "incPC"],
				["clearMIcounter"]
				],
		"JMP_const":[ # 0x06
				["outPC", "loadRAM"],
				["outRAM", "loadPC", "cond_always"],
				["clearMIcounter"]
			],
		"NEG_A":[ # 0x07
				["outA", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
                ["outALU", "loadA"],
				["clearMIcounter"]
				],
		"LOAD_const_to_B":[ # 0x08
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
                ["outRAM", "loadMemAddr", "incPC"],
                ["outMemAddr", "loadRAM"],
				["outRAM", "loadB"],
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"CMP_A_mem": [ # 0x0D
				["outPC", "loadRAM"],
                ["outRAM", "loadMemAddr", "incPC"],
                ["outMemAddr", "loadRAM"],
				["outRAM", "loadB"],
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
		"ADD_mem_to_A": [ # 0x1C
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["loadRAM", "outMemAddr"],
				["outRAM", "loadB"],
				["enableAdd", "loadALU"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"XOR_A_B_to_A": [ # 0x1D
				["enableXOR", "loadALU", "outA"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"XOR_A_to_A": [ # 0x1E
				["outA", "loadB"],
				["enableXOR", "loadALU", "outA"],
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
		"OR_A_B_to_A": [ # 0x20
				["enableOR", "loadALU", "outA"],
				["outALU", "loadA"],
				["clearMIcounter"]
				],
		"AND_A_B_to_A": [ # 0x21
				["enableAND", "loadALU", "outA"],
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
        "STORE_const_to_address": [ # 0x26
                ["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
                ["outPC", "loadRAM"],
				["storeRAM", "outRAM", "incPC"],
				["clearMIcounter"]
                ],
        "INC_B": [ # 0x27
				["outB", "enableInc", "loadALU"],
				["outALU", "loadB"],
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
				["enableAdd", "loadALU"],
				["outALU", "loadCmp"],
				["clearMIcounter"]
				],
        "CMP_A_const": [ # 0x2C
				["outPC", "loadRAM"],
				["outRAM", "loadB", "incPC"],
				["outB", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadB"],
				["enableAdd", "loadALU"],
				["outALU", "loadCmp"],
				["clearMIcounter"]
				],
        "INC_U": [ # 0x2D
				["outU", "enableInc", "loadALU"],
				["outALU", "loadU"],
				["clearMIcounter"]
				],
        "LOAD_ptr_to_U": [ # 0x2E
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["outMemAddr", "loadRAM"],
				["outRAM", "loadU"],
				["clearMIcounter"]
				],
		"STORE_U_to_address":[ #0x2F
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["storeRAM", "outU"],
				["clearMIcounter"]
				],
        "XOR_U_to_U": [ # 0x30
				["outU", "loadB"],
				["enableXOR", "loadALU", "outU"],
				["outALU", "loadU"],
				["clearMIcounter"]
				],
        "OR_U_B_to_U": [ # 0x31
				["enableOR", "loadALU", "outU"],
				["outALU", "loadU"],
				["clearMIcounter"]
				],
		"AND_U_B_toU": [ # 0x32
				["enableAND", "loadALU", "outU"],
				["outALU", "loadU"],
				["clearMIcounter"]
				],
        "NOT_A": [ # 0x33
                ["enableNOT", "loadALU", "outA"],
                ["outALU", "loadA"],
                ["clearMIcounter"]
                ],
        "NOT_B": [ # 0x34
                ["enableNOT", "loadALU", "outB"],
                ["outALU", "loadB"],
                ["clearMIcounter"]
                ],
        "NOT_U": [ # 0x35
                ["enableNOT", "loadALU", "outU"],
                ["outALU", "loadU"],
                ["clearMIcounter"]
                ],
        "NEG_U": [ # 0x36
				["outU", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "loadU"],
				["clearMIcounter"]
				],
        "NEG_mem": [ # 0x37
                ["outPC", "loadRAM"],
                ["outRAM", "loadMemAddr"],
                ["outMemAddr", "loadRAM", "incPC"],
				["outRAM", "enableNOT", "loadALU"],
				["outALU", "enableInc", "loadALU"],
				["outALU", "storeRAM"],
				["clearMIcounter"]
				],
        "COPY_A_to_U": [ # 0x38
                ["outA", "loadU"],
                ["clearMIcounter"]
                ],
        "COPY_B_to_U": [ # 0x39
                ["outB", "loadU"],
                ["clearMIcounter"]
                ],
        "COPY_U_to_A": [ # 0x3A
                ["outU", "loadA"],
                ["clearMIcounter"]
                ],
        "COPY_U_to_B": [ # 0x3B
                ["outU", "loadB"],
                ["clearMIcounter"]
                ],
        "LOAD_const_to_U": [ # 0x3C
				["outPC", "loadRAM"],
				["outRAM", "loadU"],
				["clearMIcounter"]
				],
        "ADD_mem_to_U": [ # 0x3D
				["outPC", "loadRAM"],
				["outRAM", "loadMemAddr", "incPC"],
				["loadRAM", "outMemAddr"],
				["outRAM", "loadB"],
				["enableAdd", "loadALU"],
				["outALU", "loadU"],
				["clearMIcounter"]
				],
		}

high_lvl_instructions = {
        "ADD":
            {
                "variants": ["A, @0xHH", "U#, @0xHH", "A, #0xHH", "@0xHH, @0xHH"],
                "instructions":[
                         ["ADD_mem_to_A", "??"],
                         ["ADD_mem_to_U", "??"],
                         ["ADD_const_to_A", "??"],
                         ["ADD_mem", "??", "??"]
                         ],
                "description":"Add a value from a register/memory address/const to a register or a memory address and save it in register A"
             },
        "SUB":
            {
                "variants": ["A, @0xHH"],
                "instructions":[
                         ["SUB_to_A", "??"],
                         ],
                "description":"Sub a value from a memory to a register A and save it in register A. Overwrites B."
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
                "variants": ["A0, U", "U#, A", "B, U#", "U#, B", "R, @0xHH", "R, #0xHH", "@0xHH, R", "@0xHH, @0xHH", "@0xHH, #0xHH"],
                "instructions":[
                         ["COPY_U_to_A"],
                         ["COPY_A_to_U"],
                         ["COPY_U_to_B"],
                         ["COPY_B_to_U"],
                         ["LOAD_ptr_to_R", "??"],
                         ["LOAD_const_to_R", "??"],
                         ["STORE_R_to_address", "??"],
                         ["COPY", "??", "??"],
                         ["STORE_const_to_address", "??", "??"]
                         ],
                "description":"Move a value from a register/memory address/const to a register or a memory address"
             },
        "XOR":
            {
                "variants": ["A, B", "A, A", "U#, U#"],
                "instructions":[
                         ["XOR_A_B_to_A"],
                         ["XOR_A_to_A"],
                         ["XOR_U_to_U"]
                         ],
                "description":"XOR two registers, save the result to the first operand"
             },
        "OR":
            {
                "variants": ["A, B", "U#, B"],
                "instructions":[
                         ["OR_A_B_to_A"],
                         ["OR_U_B_to_U"]
                         ],
                "description":"OR two registers, save the result to the first operand"
             },
        "AND":
            {
                "variants": ["A, B"],
                "instructions":[
                         ["AND_A_B_to_A"],
                         ["AND_U_B_to_U"]
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
                "variants": ["A", "@0xHH"],
                "instructions":[
                         ["INC_R"],
                         ["INC_mem", "??"]
                         ],
                "description":"Increment register or value at memory address"
             },
        "NOP":
            {
                "variants": [""],
                "instructions":[
                         ["NOP"],
                         ],
                "description":"Go to next address"
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
                "variants": ["A, @0xHH", "A, B", "A, #0xHH"],
                "instructions":[
                         ["CMP_A_mem", "??"],
                         ["CMP_A_B"],
                         ["CMP_A_const", "??"]
                         ],
                "description":"Compare two values (substracts them) and store the result in CMP register. Overwrites B."
             },
        "JMPEQ":
            {
                "variants": ["#0xHH"],
                "instructions":[
                         ["JMP_if_A_eq_B", "??"],
                         ],
                "description":"Go to specified address if comparison register is zero."
             },
        "JMPNEQ":
            {
                "variants": ["#0xHH"],
                "instructions":[
                         ["JMP_if_A_neq_B", "??"],
                         ],
                "description":"Go to specified address if comparison register is NOT zero."
             },
        "JMPLT":
            {
                "variants": ["#0xHH"],
                "instructions":[
                         ["JMP_if_A_lt_B", "??"],
                         ],
                "description":"Go to specified address if comparison register is strictly negative."
             },
        "JMPLE":
            {
                "variants": ["#0xHH"],
                "instructions":[
                         ["JMP_if_A_le_B", "??"],
                         ],
                "description":"Go to specified address if comparison register is negative or zero."
             },
        "JMPGT":
            {
                "variants": ["#0xHH"],
                "instructions":[
                         ["JMP_if_A_gt_B", "??"],
                         ],
                "description":"Go to specified address if comparison register is strictly positive."
             },
        "JMPGE":
            {
                "variants": ["#0xHH"],
                "instructions":[
                         ["JMP_if_A_ge_B", "??"],
                         ],
                "description":"Go to specified address if comparison register is positive (or zero)."
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
        }
            
registers = ["A", "B", "U0"]