#!/usr/bin/env python
import xml.dom.minidom
import sys
import getopt
try: 
    scandata = sys.argv[1]
except:
    print "*** You need to supply an Nmap XML file ***"
if scandata:
    doc = xml.dom.minidom.parse(scandata)
    output = []
    for host in doc.getElementsByTagName("host"):
        ip = ''
        commonName = ''
        organizationName = ''
        countryName = ''
        notBefore = ''
        notAfter = ''
        addresses = host.getElementsByTagName("address")
        ip = addresses[0].getAttribute("addr")                         # Get IP address from addr element 
        scripts = host.getElementsByTagName("script")
        for script in scripts:
              for elem in script.getElementsByTagName("elem"):         # Get cert details for each target 
                 try:
                    if elem.getAttribute("key") == 'commonName':
                       if commonName == '':                            # Only get the first commonName 
                           commonName =  elem.childNodes[0].nodeValue
                 except:
                    pass
                 try:
                    if elem.getAttribute("key") == 'organizationName':
                       if organizationName == '': 
                           organizationName =  elem.childNodes[0].nodeValue
                 except:
                    pass
                 try:
                    if elem.getAttribute("key") == 'countryName':
                       countryName =  elem.childNodes[0].nodeValue
                 except:
                    pass
                 try:
                    if elem.getAttribute("key") == 'notBefore':
                       notBefore =  elem.childNodes[0].nodeValue
                       notBefore = notBefore.split('T')[0]
                 except:
                    pass
                 try:
                    if elem.getAttribute("key") == 'notAfter':
                       notAfter =  elem.childNodes[0].nodeValue
                       notAfter = notAfter.split('T')[0]
                 except:
                    pass
        output.append(ip + ',' + commonName + ',' + organizationName + ',' + countryName + ',' + notBefore + ',' + notAfter)
    for i in output:
        print i