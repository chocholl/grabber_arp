
import os
import subprocess
import traceback
import telnetlib
import time
import paramiko

def run_cmd_ssh(p_host, p_user, p_pwd, p_cmd):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(p_host, username=p_user, password=p_pwd, look_for_keys=False, timeout=5)
		stdin, stdout, stderr = ssh.exec_command(p_cmd)
		resp = stdout.read()
		return resp
	except Exception:
		#print 'telnet error '
		traceback.print_exc()
		return ''

def run_cmd_nokia(p_host, p_user, p_pwd, p_cmd, p_end_marker, mode):
	if(mode == 'telnet'):
		return run_cmd_telnet_nokia(p_host, p_user, p_pwd, p_cmd, p_end_marker)
	if(mode == 'ssh'):
		return run_cmd_ssh(p_host, p_user, p_pwd, p_cmd)

def run_cmd_telnet_nokia(p_host, p_user, p_pwd, p_cmd, p_end_marker):
	try:
		user = p_user
		password = p_pwd
		telnet = telnetlib.Telnet(p_host, 23, 50)
		#resp = telnet.set_debuglevel(1000)
		telnet.read_until("Login: ", 5)
		telnet.write(user + '\r')
		telnet.read_until("Password: ", 5)
		telnet.write(password + '\r')
		telnet.read_until(p_end_marker, 5)
		telnet.write("environment no more"+ "\r\n")
		telnet.read_until(p_end_marker, 15)
		time.sleep(5)
		telnet.write(p_cmd+ "\r\n")
		#telnet.read_until(p_end_marker, 5)
		#telnet.write('quit' '\r\n')
		time.sleep(3)	
		telnet.write('logout'+'\r\n')
		
		#resp = telnet.read_until('Error: Bad command.', 3500)
		resp = telnet.read_all()
		return resp
	except Exception:
		#print 'telnet error '
		traceback.print_exc()
		return ''


def run_cmd_cisco(p_host, p_user, p_pwd, p_cmd, mode):
	if(mode == 'telnet'):
		return run_cmd_telnet_cisco(p_host, p_user, p_pwd, p_cmd)
	if(mode == 'ssh'):
		return run_cmd_ssh(p_host, p_user, p_pwd, p_cmd)

def run_cmd_telnet_cisco(p_host, p_user, p_pwd, p_cmd):
	try:
		user = p_user
		password = p_pwd
		telnet = telnetlib.Telnet(p_host, 23, 50)
		#resp = telnet.set_debuglevel(1000)
		telnet.read_until("sername: ", 5)
		telnet.write(user + '\r')
		telnet.read_until("assword: ", 5)
		telnet.write(password + '\r')
		time.sleep(3)
		telnet.write("term length 0"+ "\r\n")
		telnet.write(p_cmd+ "\r\n")
		telnet.write('exit' '\r\n')
		
		resp = telnet.read_all()
		return resp
	except Exception:
		#print 'telnet error '
		traceback.print_exc()
		return ''

def run_cmd_juniper(p_host, p_user, p_pwd, p_cmd, mode):
	if(mode == 'telnet'):
		return run_cmd_telnet_juniper(p_host, p_user, p_pwd, p_cmd)
	if(mode == 'ssh'):
		return run_cmd_ssh(p_host, p_user, p_pwd, p_cmd)

def run_cmd_telnet_juniper(p_host, p_user, p_pwd, p_cmd):
	try:
		user = p_user
		password = p_pwd
		telnet = telnetlib.Telnet(p_host, 23, 50)
		#resp = telnet.set_debuglevel(1000)
		telnet.read_until("login: ", 5)
		telnet.write(user + '\r')
		telnet.read_until("password: ", 5)		
		telnet.write(password + '\r')
		time.sleep(3)
		telnet.write(p_cmd+ " | no-more" + "\r\n")
		telnet.write('exit' '\r\n')

		resp = telnet.read_all()
		return resp
	except Exception:
		#print 'telnet error '
		traceback.print_exc()
		return ''

def print_result(p_f_name, p_keys_list, p_dict_list, is_screen=False):

	all_keys = []
	for t_s in p_dict_list:
		keys = t_s.keys()
		for k in keys:
			if ((k not in all_keys) and (k not in p_keys_list)):
				all_keys.append(k)
	if(len(all_keys)>0):
		all_keys.sort()

	f= open(p_f_name,"w")
	out=''
	p = p_keys_list + all_keys

	for pp in p:
		out = out + pp + ';'
	out = out[:-1]
	if (is_screen==True):
		print(out)
	f.write(out+"\n")

	for ss in p_dict_list:
		out = ''
		for pp in p:
			out = out + str(ss.get(pp, '')) + ';'
		out = out[:-1]
		if (is_screen==True):
			print(out)
		f.write(out+"\n")

	f.close() 
		
		
		
def get_result(p_f_name, is_screen=False):
	ret = []
	keys = []

	f = open(p_f_name)
	i = 0
	for line in f:
		l_line = line.rstrip()
		if(i==0):
			keys = l_line.split(';')
			i=i+1
		else:
			j=0
			d = {}
			for val in l_line.split(';'):
				if(val!=''):
					d[keys[j]]=val
				j=j+1
			ret.append(d)
	f.close()

  

	return ret

