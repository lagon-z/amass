import threading
from queue import Queue
import json
import requests
import urllib3
import time
import sys
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
    def addtask(self):#them target
        data = {"address":self.url,"description":self.url,"criticality":"10"}
        try:
            response = requests.post(self.tarurl+"/api/v1/targets",data=json.dumps(data),headers=self.headers,timeout=30,verify=False)
            result = json.loads(response.content)
            return result['target_id']
        except Exception as e:
            print(str(e))
            return
    def startscan(self,target_id):#bat dau scan target
        data = {"target_id":target_id,"profile_id":"11111111-1111-1111-1111-111111111117","schedule": {"disable": False,"start_date":None,"time_sensitive": False}}
        try:
            response = requests.post(self.tarurl+"/api/v1/scans",data=json.dumps(data),headers=self.headers,timeout=30,verify=False)
            result = json.loads(response.content)
            return result['target_id']
        except Exception as e:
            print(str(e))
            return  
    def generated_report(self,scan_id,target):#report sang 1 file xml 
        data = {"template_id": "21111111-1111-1111-1111-111111111111","source": {"list_type": "scans", "id_list":[scan_id]}}
        try:
            response = requests.post(self.tarurl + "/api/v1/reports", data=json.dumps(data), headers=self.headers, verify=False)
            report_url = self.tarurl.strip('/') + response.headers['Location']
            requests.get(str(report_url),headers=self.headers, verify=False)
            while True:
                report = self.get_report(response.headers['Location'])
                if not report:
                    time.sleep(5)
                elif report:
                    break
            if(not os.path.exists("reports")):
                os.mkdir("reports")
                
            report = requests.get(self.tarurl + report,headers=self.headers, verify=False,timeout=120)
            
            filename = str(target.strip('/').split('://')[1]).replace('.','_').replace('/','-')
            file = "reports/" + filename + "%s.xml" % time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time()))
            with open(file, "wb") as f:
                f.write(report.content)
            print("[INFO] %s report have %s.xml is generated successfully" % (target,filename))
        except Exception as e:
            raise e
        finally:
            self.delete_report(response.headers['Location'])
    def get_report(self,reportid):
        res = requests.get(url=self.tarurl + reportid, timeout=10, verify=False, headers=self.headers)
        try:
            report_url = res.json()['download'][0]
            return report_url
        except Exception as e:
            return False
    def delete_scan(self,scan_id):#xoa target sau khi quet xong
        try:
            response = requests.delete(self.tarurl+"/api/v1/scans/"+str(scan_id),headers=self.headers,timeout=30,verify=False)
            if response.status_code == "204":
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return
    def checkProcess(self) : # kiem tra dang chay may tien trinh va xem cái nào đã xong thì report
        for scan_id in self.list_processing : 
            try:
                response = requests.get(self.tarurl + '/api/v1/scans/' + str(scan_id), headers = self.headers, verify=False)
                print(self.tarurl+'/api/v1/scans/'+ str(scan_id))
                print(self.headers)
                result = json.loads(response.content)
                print(result)
                status = result['current_session']['status']
                if status == "completed":
                    self.getreports(scan_id)
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
