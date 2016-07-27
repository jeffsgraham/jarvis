#!/usr/bin/env python
from threading import Thread
from jarvis import wsgi
from inventory.models import Item
from jarvis_utilities import JarvisIPUtilities
from Queue import Queue

class Uptime(object):
    '''
        Ping collection of hosts/ips and sort into online and offline lists
    '''
    results = {"Online": [], "Offline": []}
    ip_queue = Queue()
    thread_count = 20
    
    def __init__(self, ip_addresses, thread_count):
        self.thread_count = thread_count
        for ip in ip_addresses:
            self.ip_queue.put(ip)

    def start(self):
        #create thread_count number of workers
        for i in range(self.thread_count):
            t = Worker(self.ip_queue, self.results)
            t.start()
            
        #wait for all tasks in queue to be completed
        self.ip_queue.join()

        return self.results

class Worker(Thread):
    def __init__(self, queue, results):
        super(Worker, self).__init__()
        self.queue = queue
        self.results = results
        
    def run(self):
        while not self.queue.empty():
            item = self.queue.get()
            ip = item.attributes['IP Address']
            link = JarvisIPUtilities.ping(ip)
            item.link_update(link==True) #store current link state
            result = "Online" if link else "Offline"
            self.results[result].append(ip)
            self.queue.task_done() #notify queue that task is complete

        return 


if __name__ == '__main__':
    hosts = Item.objects.raw_query({'attributes.IP Address':{'$exists':True}})
    ping = Uptime(hosts, 20)
    ping.start()
