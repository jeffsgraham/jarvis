from netaddr import *
import urllib2
import os
from collections import OrderedDict

class JarvisIPUtilities():
    @staticmethod
    def sweep_range(ip_base, ip_mask):
        net = IPNetwork(ip_base + "/" + str(ip_mask))
        results = OrderedDict()
        for ip in net:
            found = False
            web_path = False
            if JarvisIPUtilities.ping(ip):
                found = True
                web_path = JarvisIPUtilities.port_80(ip)

            results[ip] = {"ping":found, "web_path":web_path}
        return results

    @staticmethod
    def ping(ip):
        resp = os.system("ping -c 1 -w 1 " + str(ip))
        if resp == 0:
            return True
        else:
            return False

    @staticmethod
    def port_80(ip):
        http_paths = ["/www/", "/nortxe_index.html", "/cgi-bin/main.cgi?page=MENU_STATUS&lang=e"]
        for path in http_paths:
            try:
                urllib2.urlopen("http://" + str(ip) + path, timeout = 1)
                return path #found, stop looping
            except urllib2.HTTPError, e: #catch path errors
                if e.code == 404:
                    continue #to next path option
                else:
                    return path
            except urllib2.URLError, e: #catch timeouts
                return False #timeout or other error, stop looping
        return False #catch all others

