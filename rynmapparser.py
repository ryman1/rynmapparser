#!/usr/bin/env python
import xml.dom.minidom
import sys
import getopt
import csv
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["inputfile=","outputfile="])
except getopt.GetoptError:
    print 'rynnmapparser.py -i <inputfile> -o [outputfile] '
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'rynnmapparser.py -i <inputfile> -o [outputfile] '
        sys.exit()
    elif opt in ("-i", "--inputfile"):
        inputfile = arg
    elif opt in ("-o", "--outputfile"):
        outputfile = arg

doc = xml.dom.minidom.parse(inputfile)
output = []

with open(outputfile, 'w') as csvfile:
    csvout = csv.writer(csvfile, delimiter=",",quotechar="'", quoting=csv.QUOTE_MINIMAL)
    csvout.writerow(['State','IP','type','vendor','OS Family','OS Generation','OS Class Accuracy','Name', 'CPE',
                    'Name Accuracy'])
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

        output.append([str(state),str(ip),str(type),str(vendor),str(osfamily),str(osgen),str(osclassaccuracy),str(name),str(cpe),str(nameaccuracy)])
    for row in output:
        if row[0] is not '':
            csvout.writerow(row)
            print row
