# -*- coding: utf-8 -*-

from socket import gethostname
import time
import commands
import json
import socket

def getAgentDetails():
	agent_details = {}
	dummy_mac = "52:54:00:86:c5:a3"
	dummy_ip = "192.168.202.11"
	agent_details['hostname'] = str(gethostname())
	agent_details['ipv4_address'] = dummy_ip
	agent_details['mac_address'] = dummy_mac
	return agent_details

def getPackageDetails():
	package_data = []
	"""
	1.All Package Name get
	1.Iteratable PackageDetail
	1.add dic
	2.add list
	4.return list
	"""
	#package_names = commands.getstatusoutput('rpm -qa --qf={\'product\'" ":" \""%{NAME}"\""", "\"version\"" ":" \""%{VERSION}"\""", "\"vendor\"" ":" \""%{VENDOR}"\""", "\"release\"" ":" \""%{RELEASE}"\""", "\"nevr\"" ":" \""%{NEVR}"\""", "\"platform\"" ":" \""%{PLATFORM}"\"\}@@@@@" bash')[1]
	package_names = commands.getstatusoutput('bash callme.sh')[1]
	package_name_list = package_names.split("@@@@@")
	package_name_list = filter(lambda s:s != '', package_name_list)
	for i in package_name_list:
		package_data.append(i)
	return package_data
		
def writePackageDetails(li):
	with open('package_data.json', 'w') as f:
		json.dump(li, f, sort_keys=True, indent=4)

def readPackageDetails():
	with open('package_data.json', 'r') as f:
		read_dic = json.load(f)
	return read_dic

def dummywritePackageDetails(li):
	with open('dummy_package_data.json', 'w') as f:
		json.dump(li, f, sort_keys=True, indent=4)

def dummyreadPackageDetails():
	with open('dummy_package_data.json', 'r') as f:
		read_dic = json.load(f)
	return read_dic

def compare(current_list, latest_list):
	"インストールされているパッケージの最新情報と、前回比較時に取得したパッケージ情報を比較し差分を抽出するメソッド"
	current_package_list = current_list
	latest_package_list = latest_list
	install_package_list = ["install"]
	update_package_list = []
	delete_package_list = ["delete"]
	
	"インストールされたパッケージを抽出"
	for l_row in latest_package_list:
		match = False
		for c_row in current_package_list:
			#time.sleep(0.5)
			#print l_row
			#print c_row
			#print "--------------"
			if c_row == l_row:
				#print("hit")
				match = True
		if not match:
			install_package_list.append(l_row)

	"リムーブされたパッケージを抽出"
	for c_row in current_package_list:
		match = False
		for l_row in latest_package_list:
			if c_row == l_row:
				match = True

		if not match:
			delete_package_list.append(c_row)
	return (install_package_list, delete_package_list)

def sendToApi(package, agent):
	data = {}
	data.update(agent)
	if package[0] == "install" :
		data['method'] = package[0]
		#ここからIterato
	xxx
		data['software'] = package[1]
		pass
		#送信するデータ hostname ip mac software
	elif package[0] == "delete" :
		pass
	
		#Send
	print json.dumps(data, indent=4)
		
	

agedic = getAgentDetails()
inslist = compare(readPackageDetails(), dummyreadPackageDetails())[0]
dellist = compare(readPackageDetails(), dummyreadPackageDetails())[1]
sendToApi(inslist, agedic)
