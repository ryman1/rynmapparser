#!/usr/bin/env python
import xml.dom.minidom
import sys
import getopt
import time
try: 
    scandata = sys.argv[1]
except:
    print "*** You need to supply an Nmap XML file ***"
if scandata:
    doc = xml.dom.minidom.parse(scandata)
    output = []
    for host in doc.getElementsByTagName("host"):
        ip = ''
        type = ''
        vendor = ''
        osfamily = ''
        osgen = ''
        osclassaccuracy = ''
        name = ''
        nameaccuracy = ''
        cpe = ''
        state = ''
        commonName = ''
        organizationName = ''
        countryName = ''
        notBefore = ''
        notAfter = ''
        addresses = host.getElementsByTagName("address")
        ip = addresses[0].getAttribute("addr")                         # Get IP address from addr element 
        oss = host.getElementsByTagName("os")
        for os in oss:
            for osclass in os.getElementsByTagName("osclass"):
                if type == '':
                    type = osclass.getAttribute("type")
                if vendor == '':
                    vendor = osclass.getAttribute("vendor")
                if osfamily == '':
                    osfamily = osclass.getAttribute("osfamily")
                if osgen == '':
                    osgen = osclass.getAttribute("osgen")
                if osclassaccuracy == '':
                    osclassaccuracy = osclass.getAttribute("accuracy")
                if cpe == '':
                    try:
                        cpe = osclass.getElementsByTagName("cpe")[0].childNodes[0].nodeValue
                    except:
                        pass
                    
                        
            for osmatches in os.getElementsByTagName("osmatch"):
                name = osmatches.getAttribute("name")
                nameaccuracy = osmatches.getAttribute("accuracy")
                
        for st in host.getElementsByTagName("status"):
            state = st.getAttribute("state")


        
        output.append(state + '\t' + ip + '\t' + type + '\t' + vendor + '\t' + osfamily + '\t' + osgen + '\t' + osclassaccuracy + '\t' + name + '\t' + cpe + '\t' + nameaccuracy)
    for i in output:
        print i