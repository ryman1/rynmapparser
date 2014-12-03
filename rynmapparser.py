#!/usr/bin/env python

import xml.dom.minidom
import sys
import getopt
import csv

filexml = 'test.xml'
testtag = ['address.addr', 'os.osmatch.name']

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
        n = nodein
        while str(n.tagName) != "host":
            n = n.parentNode
            
        for a in n.getElementsByTagName('address'):
            if a.getAttribute('addrtype') == 'ipv4':
                return str(a.getAttribute('addr'))
            
    #def gather_os_info(self):
        
    def gather_all_ips(self):
        ips = []
        for host in self.__hostnodes:
            for addresstag in host.getElementsByTagName('address'):
                if addresstag.getAttribute("addrtype") == 'ipv4':
                    ips.append(str(addresstag.getAttribute('addr')))
                    break
        return ips
        
    def get_tag_info(self, tagstogather = 'all', nodeslisttocomb = None, parentnodename = None , recursive = True):
        if nodeslisttocomb == None:
            nodeslisttocomb = self.__hostnodes
            
        for node in nodeslisttocomb:
            if nodeslisttocomb == self.__hostnodes:
                parentnodename = self.get_host_ip(node)
            #gather all sub-elements that have the tag that's specified. 
            #if a tag was not specified, gather all child elements
            if tagstogather == 'all':
                #and the node we're looking at is not a newline
                if node.nodeType == 1:
                    subelementstogothrough = node.childNodes
            else: 
                #process a dotted tag request i.e. "os.osmatch.osclass" or "status"
                for tag in tagstogather:
                    subelementstogothrough = [node]
                    attributetogather = []
                    for tagsubcomponent in tag.split('.'):
                        for subelement in subelementstogothrough:
                            #detect if we're at an attribute insteaad of a tag. This if statement should probably be retooled so it doesn't mess up if there's an attribute with a tag name.
                            #also need to be able to gather multiple identical tags. i.e. <address> and <address>

                            #if the selected subelement (i.e. a "host" element or an "os" element) has any children that
                            # match the part of the dotted tag address we're looking for(i.e. "address" or  "osmatch")
                            if len(subelement.getElementsByTagName(tagsubcomponent)) > 0:
                                #dig further in to the dotted tag request
                                subelementstogothrough = subelement.getElementsByTagName(tagsubcomponent)
                                #now "subelementstogothrough" only contains the child objects we're digging for in the
                                # current parent node (i.e. all the "address"-tagged elements under host 10.0.0.1)
                                parentnodename = parentnodename + '.' + tagsubcomponent
                            else:
                                #if there are no selected subelements that have the tag we're looking for then
                                #it must be the Attribute were looking for (unless the dotted tag address is typoed).
                                if subelement.getAttribute(tagsubcomponent):
                                    ####testing
                                    infodict.update({str(parentnodename) + '.' + str(tagsubcomponent):str(subelement.getAttribute(tagsubcomponent))})
                                    ####testing
                                    parentnodename = self.get_host_ip(node)
                                    break

        #############Recursive/wildcard code - Doesn't get along with the tag method at the moment.
'''            #go through each of the sub-elements gathered
            for subelement in subelementstogothrough:
                #if the element we're looking at is not just a newline,
                if subelement.nodeType == 1:
                    #and has attributes
                    if subelement.hasAttributes():
                        if recursive:
                            #add each of the attributes to the dictionary.
                            for attribute in subelement.attributes.items():
                                print '1 attribute = ' + str(attribute)
                                infodict.update({str(parentnodename) + '.' + subelement.tagName + '.' + str(attribute[0]):str(attribute[1])})
                        else:
                            for attribute in attributetogather:
                                print '2 attribute = ' + str(attribute)
                                infodict.update({str(parentnodename) + '.' + str(attribute):str(subelement.getAttribute(attribute))})
                    #If the function was called with "recursive = True" and if there are child nodes, dive in to them just like we did for the parent here .
                    if recursive and subelement.hasChildNodes():
                        self.get_tag_info('all', [subelement], parentnodename + '.' + subelement.tagName, True)'''

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
                            addresses for a given host, this will be used.'''
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
myparser = Parser(filexml)
myparser.get_tag_info(testtag, None, None, False)
print str(infodict)

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
