# -*- coding: utf-8 -*-

from socket import gethostname
import requests
import time
import commands
import json
import socket
import uuid
import os.path

ENDPOINT = "http://192.168.202.13:8000/"

def getAgentDetails():
	agent_details = {}
	dummy_mac = "52:54:00:86:c5:a3"
	dummy_ip = "192.168.202.11"
	agent_details['name'] = str(gethostname())
	agent_details['hostname'] = str(gethostname())
	agent_details['ipv4address'] = dummy_ip
	agent_details['macaddress'] = dummy_mac

	if os.path.isfile("./.uuid"):
		f = open(".uuid","r")
		for row in f:
			agent_details['uuid'] = row
		f.close()
	else:
		f = open(".uuid","w")
		f.write(str(uuid.uuid4()))
		f.close()
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

def nullreadPackageDetails():
	return []

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
			if c_row == l_row:
				match = True
		if not match:
			install_package_list.append(l_row)

	"リムーブされたパッケージを抽出"
	#for c_row in current_package_list:
	#	match = False
	#	for l_row in latest_package_list:
	#		if c_row == l_row:
	#			match = True
	#
	#	if not match:
	#		delete_package_list.append(c_row)
	return (install_package_list, delete_package_list)

def sendToApi(package, agent):
	data = {}
	data['uuid'] = agent['uuid']
	if package[0] == "install" :
		data['method'] = package[0]
		package.remove("install")
		for p in package:
			data['software'] = p
			r = requests.post(ENDPOINT+"agent/software/add/", json=data)
			print r.text
		print data
		#送信するデータ hostname ip mac software
	elif package[0] == "delete" :
		data['method'] = package[0]
		#ここからIterato
		package.remove("delete")
		for p in package:
			data['software'] = p
			r = requests.post(ENDPOINT+"agent/software/delete/", json=data)
			print r.text
		print data
	
def registAgent(agent):
	data = {}
#	data['method'] = "join"
	data.update(agent)
	r = requests.post(ENDPOINT+"agent/add/", json=data)
	#print data
	print r.status_code
	print r.text

if __name__ == "__main__":
	agedic = getAgentDetails()
	if not os.path.isfile("./.uuid"):	#Agentが初回起動かどうか
		#	Agentの登録
		registAgent(agedic)
		#	インストールされている全パッケージ情報の取得
		all_package_list = compare([],getPackageDetails())[0]
		#	パッケージ情報（ソフトウェア）の送信
		sendToApi(all_package_list, agedic)
	else:
		#inslist = compare(readPackageDetails(), dummyreadPackageDetails())[0]
		#dellist = compare(readPackageDetails(), dummyreadPackageDetails())[1]
		pass
