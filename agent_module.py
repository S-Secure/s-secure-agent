# -*- coding: utf-8 -*-

from socket import gethostname
import requests
import commands
import json
import socket
import uuid
import os.path
import platform

ENDPOINT = "http://192.168.202.51:8000/"

def getAgentDetails():
	agent_details = {}
	agent_details['name'] = str(gethostname())
	agent_details['hostname'] = str(gethostname())
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	agent_details['ipv4address'] = s.getsockname()[0]
	f = open('/etc/redhat-release')
	lines = f.readlines()
	f.close()
	agent_details['os'] = lines[0].rstrip()
	f = open('/etc/system-release-cpe')
	lines = f.readlines()
	f.close()
	agent_details['os_cpe'] = lines[0].rstrip()
	agent_details['os_type'] = platform.system()
	agent_details['bit'] = platform.machine()

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
	data.update(agent)
	#print data
	r = requests.post(ENDPOINT+"agent/add/", json=data)
	print r.text

if __name__ == "__main__":
	agedic = getAgentDetails()
	if os.path.isfile("./.uuid"):	#Agentが初回起動かどうか
	#if not os.path.isfile("./.uuid"):	#Agentが初回起動かどうか
		#	Agentの登録
		try:
			registAgent(agedic)
		except:
			print "Connection refused"
		#	インストールされている全パッケージ情報の取得
		all_package_list = compare([],getPackageDetails())[0]
		#	パッケージ情報（ソフトウェア）の送信
		try:
			sendToApi(all_package_list, agedic)
		except:
			print "Connection refused"
		#	パッケージ情報をファイルに保存
		writePackageDetails(all_package_list)
	else:
		#	前回APIにデータを送信した後に新規にインストールされたパッケージ情報の取得
		inslist = compare(readPackageDetails(), dummyreadPackageDetails())[0]
		#	前回APIにデータを送信した後でアンインストールされたパッケージ情報の取得
		dellist = compare(readPackageDetails(), dummyreadPackageDetails())[1]
		#   新規にインストールされたパッケージ情報（ソフトウェア）の送信
		sendToApi(inslist, agedic)
		#   アンインストールされたパッケージ情報（ソフトウェア）の送信
		sendToApi(dellist, agedic)
		#   インストールされている全パッケージ情報の取得
		all_package_list = compare([],getPackageDetails())[0]
		#	パッケージ情報をファイルに保存
		writePackageDetails(all_package_list)
