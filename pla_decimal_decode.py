#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 19:50:43 2020

@author: aviallon
"""
nbits = 8
convert_table = {
		0: "01110111",
		1: "01000001",
		2: "00111011",
		3: "01101011",
		4: "01001101",
		5: "01101110",
		6: "01111110",
		7: "01000011",
		8: "01111111",
		9: "01101111"
		}

nombres = {}

for i in range(0, 2**nbits):
	unites = i % 10
	dizaines = (i // 10) % 10
	centaines = (i // 10**2) % 10
	print(centaines, dizaines, unites)
	nombres[i] = [convert_table[centaines], convert_table[dizaines], convert_table[unites]]

for i in range(len(nombres[0])):
	with open(f"digit_decoder_{i}.txt", "w") as file:
		file.write("# Logisim PLA program table\n")
		for nombre in nombres:
			nombre_bin = bin(nombre)[2:].zfill(nbits)
			digit = nombres[nombre][i]
			file.write(f"{nombre_bin} {digit} #{nombre}\n")