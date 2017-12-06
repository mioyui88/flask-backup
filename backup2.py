from flask import Flask
from flask import request
from flaskext.mysql import MySQL
import json
from flask_script import Manager
import re
import os

mysql = MySQL()

app = Flask(__name__)
manager = Manager(app)
 
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'cnvd'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

def fun_1(cursor):
    all_devices = []
    cursor.execute('SELECT COUNT(*) FROM DEVICE_list_0 ')
    count = cursor.fetchone()[0]
    for i in range(1,count+1):
        all_devices.append(fun_2(cursor,i))
    return count,all_devices

def fun_3(cursor):
	cursor.execute('SELECT COUNT(*) FROM DEVICE_list_0 ')
	count = cursor.fetchone()[0]
	return count

def fun_2(cursor,i):
    cursor.execute('SELECT * FROM DEVICE_list_0 WHERE DEV_id = "'+str(i)+'"')
    MAC_org_0 = cursor.fetchone()
    
    mac = MAC_org_0[1]
    ip = MAC_org_0[2]
    org = MAC_org_0[3].split()[0].split(',')[0]
    ports = MAC_org_0[4].replace('None','')

    ip=re.sub(r'192\.168\.1\.(1[5-6]\d|17[0-2])','192.168.1.149',ip)

    try:
    	cursor.execute("select os from OS where ip = '"+ip+"'")
    	os = cursor.fetchone()[0]
    except:
    	os = None

    if os == 'Windows NT kernel 5.x':  #os =='Windows:XP' or 
    	table = 'os_windowsXP' 
    elif os == 'Windows 7 or 8':
    	table = 'os_windows7'
    else:
    	table = None

    patchs = None
    
    try:
    	cursor.execute("select patch from %s order by last_updated desc limit 0,10" % table )
    	patchs = cursor.fetchall()
    except:
    	patchs = None

    cursor.execute('SELECT PRODUCT_id FROM PRODUCT_list_0 WHERE PRODUCT_name like "''%'+org+'%''"')
    PRODUCT_id=cursor.fetchall()
    
    #print "%d: %s \n %s \n %s \n %s \n" %(i,mac,ip,org,ports)

    dev = [i,mac,ip,org,os,ports]

    productname=[]

    if PRODUCT_id==():
        pass#print "no product \n"
    else:
        num = 0
        for product_id in PRODUCT_id:
            p_id=str(product_id[0])
            cursor.execute('SELECT PRODUCT_name FROM PRODUCT_list_0 WHERE PRODUCT_id = "'+p_id+'"')
            PRODUCT_name=cursor.fetchone()
            #print "-----------------------------------------------------"
            #print "Version: %s \n" %PRODUCT_name[0]  #every PRODUCT_name

            productname.append([PRODUCT_name[0]]) 
            
            cursor.execute('SELECT CNVD_id FROM CNVD_PRODUCT_list_0 WHERE PRODUCT_id = "'+p_id+'"')
            CNVD_id=cursor.fetchall()
            for cnvd_id in CNVD_id:  
                #print '%s \n'%cnvd_id[0]  #id[0] every CNVD_id in one packet
                productname[num].append(cnvd_id[0]) 
                #cursor.execute('SELECT * FROM CNVD_list_0 WHERE CNVD_id = "'+cnvd_id[0]+'"')
                #CNVD=cursor.fetchone()#list (1.CNVD_id,2.CNVD_title,3.CNVD_time,4.CNVD_level,5.CNVD_desc,6.CVE_id,7.CVE_id_href,8.CNVD_refer_href,9.CNVD_plan,10.CNVD_patch,11.CNVD_patch_href )
                #print CNVD
            num = num + 1
    return dev, productname, patchs


@app.route("/")
def hello():
    return "Welcome to Python Flask App!"

@app.route("/ID")
def dev_id():
    id = request.args.get('id')
    cursor = mysql.connect().cursor()
    
    data = fun_2(cursor,id)
    if data == ():
        return "no data"
    else:
        r = json.dumps(data)
        return r

@app.route("/all")
def all_dev():
    cursor = mysql.connect().cursor()
    data = fun_1(cursor)
    if data == ():
        return "no data"
    else:
        r = json.dumps(data)
        return r


@app.route("/count")
def count():
	cursor = mysql.connect().cursor()
	data = fun_3(cursor)
	r = json.dumps(data)
	return r

if __name__ == "__main__":
    manager.run()
