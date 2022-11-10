import math
import threading
def addtask(tarurl,headers,url=''):
    data = {"address":url,"description":url,"criticality":"10"}
    try:
        response = requests.post(tarurl+"/api/v1/targets",data=json.dumps(data),headers=headers,timeout=30,verify=False)
        result = json.loads(response.content)
        return result['target_id']
    except Exception as e:
        print(str(e))
        return
def startscan(tarurl,headers,target_id):
    data = {"target_id":target_id,"profile_id":"11111111-1111-1111-1111-111111111111","schedule": {"disable": False,"start_date":None,"time_sensitive": False}}
    try:
        response = requests.post(tarurl+"/api/v1/scans",data=json.dumps(data),headers=headers,timeout=30,verify=False)
        result = json.loads(response.content)
        return result['target_id']
    except Exception as e:
        print(str(e))
        return   
list_url = [] #urrl lay tu aquatone
class myThread(threading.Thread):

    def __init__(self, threadID, ip, apikey, output):
        threading.Thread.__init__(self)
        self.threadID = threadID	
        self.ip = ip	
        self.apikey = apikey	
        self.output = output	
    def run(self):
        tarurl = "https://"+self.ip+":3443/"
        headers = {"X-Auth":self.apikey,"content-type": "application/json"}
        threadLock.acquire()
            #can them lay urrl trong list
        startscan(tarurl,headers,addtask(tarurl,headers,url))
        # Giai phong lock cho thread ke tiep
        threadLock.release()
threads = []
thread1 = myThread(1, "192.168.32.222","1986ad8c0a5b3df4d7028d5f3c06e936c0d5fcab7ab93418d84681370004db207",#output)
thread2 = myThread(2, "192.168.32.220","1986ad8c0a5b3df4d7028d5f3c06e936c0d5fcab7ab93418d84681370004db207",#output)
thread1.start()
thread2.start()# Them cac thread vao list
threads.append(thread1)
threads.append(thread2)# Doi cho tat ca thread ket thuc
for t in threads:
    t.join()
