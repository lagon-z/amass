import threading
from queue import Queue
import json
import requests
import urllib3
import time
urllib3.disable_warnings()
list_url = Queue()
list_url.put('http://fbox-fw.fpt.vn/')
list_url.put('http://fti.fpt.vn/')
list_url.put('http://popmail.fpt.vn:8080/')
list_url.put('https://qr.fpt.vn/')
list_url.put('http://isp-relay.fpt.vn/')
list_url.put('http://fbox-api.fpt.vn/')
list_url.put('http://api-insidev3-paytv.fpt.vn/')
list_url.put('https://notification-dev.scc.fpt.vn/')
list_url.put('http://uat-tstv.fbox.fpt.vn/')
list_url.put('https://hr.fpt.vn/')
list_url.put('https://mobisaleguide.fpt.vn/')
list_url.put('https://survey-paytv.fpt.vn/')
list_url.put('https://api-cms.fbox.fpt.vn/')
list_url.put('http://staging-payment.fbox.fpt.vn/')
class myThread(threading.Thread):

    def __init__(self, threadID, ip, apikey):
        threading.Thread.__init__(self)
        self.threadID = threadID	
        self.tarurl = "https://"+ip+":3443"
        self.headers = {"X-Auth":apikey,"content-type": "application/json"}	
        self.url = ''
        self.list_processing = []
    def run(self):
        while( not list_url.full() ):
            self.checkProcess()
            process = len(self.list_processing)
            if process >=3 :
                time.sleep(6)
            else : 
                self.url = list_url.get()
                self.list_processing.append(self.startscan(self.addtask()))
    def addtask(self):
        data = {"address":self.url,"description":self.url,"criticality":"10"}
        try:
            response = requests.post(self.tarurl+"/api/v1/targets",data=json.dumps(data),headers=self.headers,timeout=30,verify=False)
            result = json.loads(response.content)
            return result['target_id']
        except Exception as e:
            print(str(e))
            return
    def startscan(self,target_id):
        data = {"target_id":target_id,"profile_id":"11111111-1111-1111-1111-111111111117","schedule": {"disable": False,"start_date":None,"time_sensitive": False}}
        try:
            response = requests.post(self.tarurl+"/api/v1/scans",data=json.dumps(data),headers=self.headers,timeout=30,verify=False)
            result = json.loads(response.content)
            return result['target_id']
        except Exception as e:
            print(str(e))
            return  
    def checkProcess(self) :
        for scan_id in self.list_processing : 
            try:
                response = requests.get(self.tarurl + '/api/v1/scans/' + str(scan_id), headers = self.headers, verify=False)
                print(self.tarurl+'/api/v1/scans/'+ str(scan_id))
                print(self.headers)
                result = json.loads(response.content)
                print(result)
                status = result['current_session']['status']
                if status == "completed":
                    self.list_processing.remove(scan_id)
            except Exception as e:
                print(str(e))
                return
        return
threads = []
thread1 = myThread(1, "192.168.233.130","1986ad8c0a5b3df4d7028d5f3c06e936c0d5fcab7ab93418d84681370004db207")
thread1.start()
threads.append(thread1)
for t in threads:
    t.join()
