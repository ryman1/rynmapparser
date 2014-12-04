#!/usr/bin/env python

import xml.dom.minidom
import sys
import getopt
import csv

filexml = 'testsmall.xml'
testtag = ['address.addr', 'os.osmatch.name']
# testtag = ['address', 'os', 'uptime']
# testtag = ['tcptssequence']
# testtag = ['ports.extraports.extrareasons.reason', 'ports.extraports.extrareasons.count']

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

    def tag_or_attribute(self, dottedstring, elements):
        element = elements[0]
        for tagsubcomponent in dottedstring.split('.')[0:-1]:
            element = element.getElementsByTagName(tagsubcomponent)[0]
        if element.getElementsByTagName(dottedstring.split('.')[-1]):
            return 'tag'
        elif element.getAttribute(dottedstring.split('.')[-1]):
            return 'attribute'
        else:
            return 'neither'

    def get_tag_info(self, tagstogather = 'all', nodeslisttocomb = None, parentnodename = None , recursive = True):
        if nodeslisttocomb is None:
            nodeslisttocomb = self.__hostnodes
        attributetogather = []
        for node in nodeslisttocomb:
            if nodeslisttocomb == self.__hostnodes:
                parentnodename = self.get_host_ip(node)

            ########newstuff




            #if "tagstogather" == all, gather all sub-attributes and sub-elements (subelements only if recursive is enabled)
            if tagstogather == 'all':
                #If the node we're looking at is not a newline
                if node.nodeType == 1:
                    subelementstogothrough = node.childNodes

                    #############Recursive/wildcard code - Doesn't get along with the tag method at the moment.

                    #go through each of the sub-elements gathered i.e. "address", "os", "uptime"
                    for subelement in subelementstogothrough:
                        #if the element we're looking at is not just a newline,
                        if subelement.nodeType == 1:
                            #and has attributes
                            if subelement.hasAttributes():
                                if recursive:
                                    #add each of the attributes to the dictionary.
                                    for attribute in subelement.attributes.items():
                                        infodict.update({str(parentnodename) + '.' + str(subelement.tagName) + '.' + str(attribute[0]):str(attribute[1])})
                                else:
                                    for attribute in attributetogather:
                                        infodict.update({str(parentnodename) + '.' + str(attribute):str(subelement.getAttribute(attribute))})
                            #If the function was called with "recursive = True" and if there are child nodes, dive in to
                            #them just like we did for the parent here .
                            if recursive and subelement.hasChildNodes():
                                self.get_tag_info('all', [subelement], parentnodename + '.' + subelement.tagName, True)



            #add intelligent code to this else loop to make it gather all
            #attributes of a tag if a specific attribute was not specified.


            #process a dotted tag/attribute request i.e. "os.osmatch.osclass" or "status"
            #if the request is for a tag (not an attribute), get that tag's attributes (and subelements if recursive
            #is enabled)
            else:
                for dottedtag in tagstogather:
                    subelementstogothrough = [node]
                    toa = self.tag_or_attribute(dottedtag, subelementstogothrough)
                    for subelement in subelementstogothrough:
                        if toa == 'tag':
                            #add this element's attributes to the dictionary
                            #dig further in to the dotted tag request
                            se = subelement
                            for tag in dottedtag.split('.')[0:-1]:
                                parentnodename = parentnodename + '.' + tag
                                se = se.getElementsByTagName(tag)[0]
                            for attr in se.attributes.items():
                                infodict.update({str(parentnodename) + '.' + dottedtag.split('.')[-1]: str(attr[1])})
                            self.get_tag_info('all', [se], parentnodename, recursive)
                            parentnodename = self.get_host_ip(node)



                        elif toa == 'attribute':
                            se = subelement
                            for tag in dottedtag.split('.')[0:-1]:
                                se = se.getElementsByTagName(tag)[0]
                                parentnodename = parentnodename + '.' + tag
                            if se.getAttribute(dottedtag.split('.')[-1]):
                                ####testing
                                infodict.update({str(parentnodename) + '.' + str(dottedtag.split('.')[-1]):str(se.getAttribute(dottedtag.split('.')[-1]))})
                                ####testing
                                parentnodename = self.get_host_ip(node)
                                break



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
# myparser.get_tag_info()
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
