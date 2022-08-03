import os
import re
import copy
import subprocess
import traceback
import time
import sys
import datetime
import multiprocessing as mp
from multiprocessing import Pool
import getpass

sys.path.append('./libs')
import lib as lib


def _proc_cisco(v):
	global vprn_dict
	global dev_name
	global dev_ip
	global g_user
	global g_pwd
	ret = []

	print(vprn_dict[v])
	cmd_out = lib.run_cmd_telnet_cisco(dev_ip, g_user, g_pwd, 'show ip arp vrf ' + v )
	now = datetime.datetime.now()
	if(cmd_out==''):
		print('no data')
		return []
				
	f= open('output_raw/arp'+  '_' + dev_name + '_' + '_' + vprn_dict[v] + '_' + str(now.hour) + '_' + str(now.minute) +'.txt',"w")
	f.write(cmd_out)
	f.close()
	
	for c in cmd_out.split('\n'):
		c = c.replace('\r', '').replace('\n', '')
		cc = ' '.join(c.split())
		if( ' ARPA' in cc and len(cc.split(' '))==6 ):
			a = {}
			a['vrf'] = vprn_dict[v]
			h = cc.split(' ')[3].replace('.', '')
			a['mac']= ':'.join(h[i:i+2] for i in range(0,12,2))
			a['ip'] = cc.split(' ')[1]
			a['int'] = cc.split(' ')[5]
			a['exp'] = cc.split(' ')[2]
			if(a['exp'] != '-'):
				ret.append(a)
	return ret


def _proc_nk(v):
	global vprn_dict
	global dev_name
	global dev_ip
	global g_user
	global g_pwd
	ret = []

	print(vprn_dict[v])
	cmd_out = lib.run_cmd_telnet_nokia(dev_ip, g_user, g_pwd, 'show service id ' + v + ' arp', '#')
	now = datetime.datetime.now()
	if(cmd_out==''):
		print('no data')
		return []
				
	f= open('output_raw/arp'+  '_' + dev_name + '_' + '_' + vprn_dict[v] + '_' + str(now.hour) + '_' + str(now.minute) +'.txt',"w")
	f.write(cmd_out)
	f.close()
	for c in cmd_out.split('\n'):
		c = c.replace('\r', '').replace('\n', '')
		cc = ' '.join(c.split())
		if( ' Dynamic ' in cc and len(cc.split(' '))==6 ):
			a = {}
			a['vrf'] = vprn_dict[v]
			a['mac'] = cc.split(' ')[1]
			a['ip'] = cc.split(' ')[0]
			a['int'] = cc.split(' ')[5]
			a['exp'] = cc.split(' ')[3]
			ret.append(a)
	return ret
	
	
if __name__ == '__main__':
	try:
		input = raw_input
	except NameError:
		pass

	dev_list = lib.get_result('ip-list.txt', False)


	g_user = input("user: ")
	g_pwd = getpass.getpass(prompt='Password: ')


	for d in dev_list:
		dev_name = d['name']
		dev_ip = d['ip']
		print(d)
		cmd_out = ''
		o_file_name = 'mac'
			
		if (d['vendor']=='juniper' and 'mx' in d['model']):
			cmd_out = lib.run_cmd_telnet_juniper(d['ip'], g_user, g_pwd, 'show configuration routing-instances | display set | match "instance-type vrf"')
			if(cmd_out==''):
				print('no data')
				sys.exit()
			vrf_list = []
			for c in cmd_out.split('\n'):
				if('instance-type' in c and 'set routing-instances' in c):
					vrf_name = c.split(' ')[2]
					vrf_list.append(vrf_name)

			
			vrf_int_dict = {}
			cmd_out = lib.run_cmd_telnet_juniper(d['ip'], g_user, g_pwd, 'show configuration routing-instances | display set | match "interface"')
			if(cmd_out==''):
				print('no data')
				sys.exit()
			for c in cmd_out.split('\n'):
				if(c.startswith('set ') and len(c.split(' '))==5):
					c = c.replace('\r', '').replace('\n', '')
					c_int = c.split(' ')[4]
					c_vrf = c.split(' ')[2]
					if(c_vrf in vrf_list):
						vrf_int_dict[c_int] = c_vrf

			
			
			
			int_list_outer_dict = {}
			int_list_inner_dict = {}
			int_list_vlanid_dict = {}
			
			cmd_out = lib.run_cmd_telnet_juniper(d['ip'], g_user, g_pwd, 'show configuration interfaces | display set | match "vlan-tags"')
			if(cmd_out==''):
				print('no data')
				sys.exit()
			for c in cmd_out.split('\n'):
				if(c.startswith('set ') and len(c.split(' '))==8):
					if(c.split(' ')[6] == 'outer'):
						c = c.replace('\r', '').replace('\n', '')
						c_int = c.split(' ')[2]
						c_unit = c.split(' ')[4]
						c_tag = c.split(' ')[7]
						int_list_outer_dict[c_int + '.' + c_unit] = c_tag
					if(c.split(' ')[6] == 'inner'):
						c = c.replace('\r', '').replace('\n', '')
						c_int = c.split(' ')[2]
						c_unit = c.split(' ')[4]
						c_tag = c.split(' ')[7]
						int_list_inner_dict[c_int + '.' + c_unit] = c_tag

			cmd_out = lib.run_cmd_telnet_juniper(d['ip'], g_user, g_pwd, 'show configuration interfaces | display set | match "vlan-id"')
			if(cmd_out==''):
				print('no data')
				sys.exit()
			for c in cmd_out.split('\n'):
				if(c.startswith('set ') and len(c.split(' '))==7):
					if(c.split(' ')[5] == 'vlan-id'):
						c = c.replace('\r', '').replace('\n', '')
						c_int = c.split(' ')[2]
						c_unit = c.split(' ')[4]
						c_tag = c.split(' ')[6]
						int_list_vlanid_dict[c_int + '.' + c_unit] = c_tag

			
			arp_list = []
			cmd_out = lib.run_cmd_telnet_juniper(d['ip'], g_user, g_pwd, 'show arp no-resolve expiration-time')
			now = datetime.datetime.now()
			
			f= open('output_raw/arp'+  '_' + d['name'] + '_' + str(now.hour) + '_' + str(now.minute) +'.txt',"w")
			f.write(cmd_out)
			f.close()
			if(cmd_out!=''):
				
				for c in cmd_out.split('\n'):
					c = c.replace('\r', '').replace('\n', '')
					cc = ' '.join(c.split())
					if( ' none ' in cc and len(cc.split(' '))==5 ):
						a = {}				
						a['mac'] = cc.split(' ')[0]
						a['ip'] = cc.split(' ')[1]
						a['int'] = cc.split(' ')[2]
						a['exp'] = cc.split(' ')[4]
						a['vrf'] = vrf_int_dict.get(a['int'], '')
						for tag_outer in int_list_outer_dict:
							if(tag_outer == a['int']):
								a['tag_outer'] = int_list_outer_dict[tag_outer]
						for tag_inner in int_list_inner_dict:
							if(tag_inner == a['int']):
								a['tag_inner'] = int_list_inner_dict[tag_inner]
						for tag_vlanid in int_list_vlanid_dict:
							if(tag_vlanid == a['int']):
								a['tag_vlanid'] = int_list_vlanid_dict[tag_vlanid]

						arp_list.append(a)
				lib.print_result('output/arp' + '_' + d['name'] + '_' + str(now.hour) + '_' + str(now.minute) +'.csv', ['ip', 'int', 'mac', 'exp', 'vrf', 'tag_inner', 'tag_outer', 'tag_vlanid'], arp_list, False)
				print('arp_list_len='+str(len(arp_list)))

				
		if (d['vendor']=='nokia'):
			
			cmd_out = lib.run_cmd_telnet_nokia(d['ip'], g_user, g_pwd, 'show service service-using vprn', '#')
			if(cmd_out==''):
				print('no data')
				sys.exit()
			
			now = datetime.datetime.now()
			f= open('output_raw/vrf'+  '_' + d['name'] + '_' + str(now.hour) + '_' + str(now.minute) +'.txt',"w")
			f.write(cmd_out)
			f.close()

			vprn_dict = {}
			for c in cmd_out.split('\n'):
				c = c.replace('\r', '').replace('\n', '')
				cc = ' '.join(c.split())
				if( 'VPRN' in cc and 'Up' in cc and len(cc.split(' '))==6 ):
					s_id = cc.split(' ')[0]
					s_name = cc.split(' ')[5]
					vprn_dict[s_id] = s_name
			print(vprn_dict)
			
			arp_list = []
			
			p = Pool(processes=5)
			data = p.map(_proc_nk, [i for i in vprn_dict])
			p.close()
			for dd in data:
				for a in dd:
					arp_list.append(a)
			print(data)
			
			
			lib.print_result('output/arp' + '_' + d['name'] + '_' + str(now.hour) + '_' + str(now.minute) +'.csv', ['ip', 'int', 'mac', 'exp', 'vrf'], arp_list, False)
			print('arp_list_len='+str(len(arp_list)))


		if (d['vendor']=='cisco' and '760' in d['model']):
			
			cmd_out = lib.run_cmd_telnet_cisco(d['ip'], g_user, g_pwd, 'show ip vrf interfaces')
			if(cmd_out==''):
				print('no data')
				sys.exit()
			
			now = datetime.datetime.now()
			f= open('output_raw/vrf'+  '_' + d['name'] + '_' + str(now.hour) + '_' + str(now.minute) +'.txt',"w")
			f.write(cmd_out)
			f.close()

			vprn_dict = {}
			for c in cmd_out.split('\n'):
				c = c.replace('\r', '').replace('\n', '')
				cc = ' '.join(c.split())
				if( 'up' in cc.lower() and len(cc.split(' '))==4 ):
					s_id = cc.split(' ')[2]
					s_name = cc.split(' ')[2]
					if(s_id not in vprn_dict):
						vprn_dict[s_id] = s_name
			print(vprn_dict)
			
			arp_list = []
			
			p = Pool(processes=5)
			data = p.map(_proc_cisco, [i for i in vprn_dict])
			p.close()
			for dd in data:
				for a in dd:
					arp_list.append(a)
			#print(data)
			
			
			lib.print_result('output/arp' + '_' + d['name'] + '_' + str(now.hour) + '_' + str(now.minute) +'.csv', ['ip', 'int', 'mac', 'exp', 'vrf'], arp_list, False)
			print('arp_list_len='+str(len(arp_list)))
