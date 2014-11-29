#!/usr/bin/env python

import xml.dom.minidom
import sys
import getopt
import csv

testtag = 'os'

class Parser:
    def __init__(self, xmlfile):
        try:
            self.__dom = xml.dom.minidom.parse(xmlfile)
        except IOError:
            print "IO error with opening " + xmlfile
            sys.exit(1)
        except:
            sys.exit(2)
        self.__hostnodes = self.__dom.getElementsByTagName("host") 
    
    def get_host_ip(self, nodein):
        print 'type' + str(type(nodein))
        print 1
        n = nodein
        print 'nodein.tagName' + str(nodein.tagName)
        print 'n.tagName' + str(n.tagName)
        while str(n.tagName) != "host":
            print n.tagName
            print 2
            n = n.parentNode
            
        for a in n.getElementsByTagName('address'):
            if a.getAttribute('addrtype') == 'ipv4':
                return a.getAttribute('addr')
            
            
    def gather_all_ips(self):
        ips = []
        for host in self.__hostnodes:
            for addresstag in host.getElementsByTagName('address'):
                if addresstag.getAttribute("addrtype") == 'ipv4':
                    ips.append(str(addresstag.getAttribute('addr')))
                    break
        return ips
        
        
    def get_all_tag_info(self, tagtogather = 'all', nodeslisttocomb = None, parentnodename = None):
        '''if parent == None:
            parent = self.__hostnodes'''
        if nodeslisttocomb == None:
            print "-1"
            nodeslisttocomb = self.__hostnodes
            
            
        for node in nodeslisttocomb:
            if nodeslisttocomb == self.__hostnodes:
                print 'ttt' + str(type(node))
                print node.tagName
                parentip = self.get_host_ip(node)
                print 'parentip = ' + parentip
            print 1
            #gather all sub-elements that have the tag that's specified. 
            #if a tag was not specified, gather all child elements
            if tagtogather == 'all':
                print 2
                #and the node we're looking at is not a newline
                if node.nodeType == 1:
                    print 3
                    subelementstogothrough = node.childNodes
                    
            else: 
                print 4
                
                subelementstogothrough = node.getElementsByTagName(tagtogather)
            print "subelementstogothrough length  " + str(len(subelementstogothrough))
                
            #go through each of the sub-elements gathered 
            for subelement in subelementstogothrough:
                print 5
                #if the element we're looking at is not just a newline,
                if subelement.nodeType == 1:
                    print 6
                    #and has attributes
                    if subelement.hasAttributes():
                        print 7
                        #add each of the attributes to the dictionary.
                        for attribute in subelement.attributes.items():
                            print 8
                            infodict.update({tagtogather + '.' + str(attribute[0]):str(attribute[1])})
                            print str(infodict) 
                    #if there are child nodes, dive in to them just like we did for the parent here.
                    if subelement.hasChildNodes():
                        print 9
                        self.get_all_tag_info('all', [subelement])
               
            
            

    def returncols(self, fieldlist):
        #addressdict can store multiple types of addresses i.e. ipv4, ipv6, mac, etc.
        addressesdict = {}
        columndict = {}
        for host in self.__hostnodes:
            for field in fieldlist:
                try:
                    if field == "addresses":
                        for address in host.getElementsByTagName("address"):
                            addrtype = address.getAttribute("addrtype")

                            '''if there are multiple addresses of the same type, 
                            keep them in the same cell and separate with a 
                            newline. For instance, if there are multiple ip 
                            addresses, this will be used.'''
                            if addressesdict.has_key(addrtype):
                                addressesdict.update({addrtype : addressesdict[addrtype] + "\n" + address.getAttribute("addr")})
                            else:
                                addressesdict.update({address.getAttribute("addrtype"):address.getAttribute("addr")})
                    else:
                        columndict.update({field:host.getElementByTagName(field)})
                except:
                    pass
                

opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["inputfile=","outputfile="])

infodict = {}
myparser = Parser('test.xml')
myparser.get_all_tag_info(testtag)

sys.exit()
'''except getopt.GetoptError:
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
    csvout.writerow(['State', 'IP', 'type', 'vendor', 'OS Family',
                    'OS Generation', 'OS Class Accuracy', 'Name', 'CPE',
                    'Name Accuracy'])
    #go through every host element in the xml document
    for host in doc.getElementsByTagName("host"):
        ip = type = vendor = osfamily = osgen = osclassaccuracy = name = nameaccuracy = cpe = ''

        oss = host.getElementsByTagName("os")
        for st in host.getElementsByTagName("status"):
            state = st.getAttribute("state")
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

        output.append([str(state),str(ip),str(type),str(vendor),str(osfamily),str(osgen),str(osclassaccuracy),str(name),str(cpe),str(nameaccuracy)])
    for row in output:
        if row[0] is not '':
            csvout.writerow(row)
            print row'''
