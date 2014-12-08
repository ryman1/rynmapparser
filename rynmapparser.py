#!/usr/bin/env python

import xml.dom.minidom
import sys
import getopt
import csv
import re

recurse = True
filexml = 'test.xml'

# testtag = ['ports.port']
# testtag = ['os.osmatch.name', 'address']
# testtag = ['address.addr', 'address.addrtype']
# testtag = ['address', 'os', 'uptime']
testtag = ['address.addr', 'uptime']
# testtag = ['ports.extraports']
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
        currentrow = list(defaultcurrentrow)

    def get_host_ip(self, nodein):
        n = nodein
        while str(n.tagName) != "host":
            n = n.parentNode
        for a in n.getElementsByTagName('address'):
            if a.getAttribute('addrtype') == 'ipv4':
                return str(a.getAttribute('addr'))

    def gather_all_ips(self):
        ips = []
        for host in self.__hostnodes:
            for addresstag in host.getElementsByTagName('address'):
                if addresstag.getAttribute("addrtype") == 'ipv4':
                    ips.append(str(addresstag.getAttribute('addr')))
                    break
        return ips

    # Determines if the dotted string that is passed is an xml attribute or just a tag
    def tag_or_attribute(self, dottedstring, elements):
        element = elements[0]
        for tagsubcomponent in dottedstring.split('.')[0:-1]:
            try:
                element = element.getElementsByTagName(tagsubcomponent)[0]
            except:
                return 'neither'
        if element.getElementsByTagName(dottedstring.split('.')[-1]):
            return 'tag'
        elif element.getAttribute(dottedstring.split('.')[-1]):
            return 'attribute'
        else:
            return 'neither'

    def add_attribute_to_csv_row(self, attribute, value):
        # if there's not a column for the current attribute yet, add it to the header row. Also add blank values to the
        # row variables so the indexes for the new values is available for assignment.
        if attribute not in cols:
            global currentrow
            cols.append(attribute)
            defaultcurrentrow.append('')
            currentrow.append('')
        # If the current attribute hasn't already been filled for this row,
        if currentrow[cols.index(attribute)] == '':
            # add it to the current row.
            currentrow[cols.index(attribute)] = re.sub(r'\n', ' ', str(value))

    # Responsible for the bulk of the data gathering.
    def get_tag_info(self, tagstogather='all', nodeslisttocomb=None, parentnodename=None, recursive=True):
        # The node list that this method is going to parse through. By default this is all the "host" nodes in the
        # xml document.
        if nodeslisttocomb is None:
            nodeslisttocomb = self.__hostnodes
        attributetogather = []
        global currentrow
        for node in nodeslisttocomb:
            # set the new csv output row to have the appropriate number of columns.
            if nodeslisttocomb == self.__hostnodes:
                # the 'parentnodename' string is used by this method to properly format the output. i.e.
                # '10.0.0.1.address.addr'
                parentnodename = self.get_host_ip(node)
            # if "tagstogather" == all, gather all sub-attributes and sub-elements (subelements
            # only if recursive is enabled)
            if tagstogather == 'all':
                # If the node we're looking at is an element node,
                if node.nodeType == 1:
                    subelementstogothrough = node.childNodes
                    # go through each of the sub-elements gathered i.e. "address", "os", "uptime"
                    for subelement in subelementstogothrough:
                        # if the element we're looking at is not just a newline (sometimes every other child node is
                        # a '\n' character)
                        if subelement.nodeType == 1:
                            # and has attributes
                            if subelement.hasAttributes():
                                if recursive:
                                    # add each of the attributes to the csv row.
                                    for attribute in subelement.attributes.items():
                                        self.add_attribute_to_csv_row(str(attribute[0]),str(attribute[1]))
                                        # infodict.update({
                                        #     str(parentnodename) + '.' + str(subelement.tagName) + '.' + str(
                                        #         attribute[0]): str(attribute[1])})
                                else:
                                    for attribute in attributetogather:
                                        self.add_attribute_to_csv_row(str(attribute), str(subelement.getAttribute(attribute)))
                                        # infodict.update({str(parentnodename) + '.' + str(attribute): str(
                                        #     subelement.getAttribute(attribute))})
                            # If the function was called with "recursive = True" and if there are child nodes, dive in
                            # to them just like we did for the parent here .
                            if recursive and subelement.hasChildNodes():
                                self.get_tag_info('all', [subelement], parentnodename + '.' + subelement.tagName, True)
            # If 'tagstogather' is not 'all', process a dotted tag/attribute request i.e. "os.osmatch.osclass" or "status"
            # if the request is for a tag (not an attribute), get that tag's attributes (and its subelements if recursive
            # is enabled)
            else:
                for dottedtag in tagstogather:
                    subelementstogothrough = [node]
                    toa = self.tag_or_attribute(dottedtag, subelementstogothrough)
                    for subelement in subelementstogothrough:
                        # If this dotted tag request points to a tag(instead of a specific tag attribute), gather all
                        # that element's attributes.
                        if toa == 'tag':
                            se = subelement
                            # if this dotted tag contain dots. i.e. 'os.osmatch'
                            if len(dottedtag.split('.')) > 1:
                                # go through each of the elements of the dotted tag until se's value is elements
                                # of the farthest right value in the i.e. all osmatch nodes in the current subelement
                                for tag in dottedtag.split('.'):
                                    parentnodename = parentnodename + '.' + tag
                                    # currently we're only taking the first matching element. So for example if there
                                    # are multiple 'address' node for a host (mac and ipv4) it will only used the first
                                    # one, which is usually the ipv4 address. This will be changed going forward so one
                                    # can decide which specific addresses to keep etc.
                                    se = se.getElementsByTagName(tag)[0]
                            # otherwise, we don't have to do much to process this 'dotted' tag request.
                            else:
                                # currently we're only taking the first matching element. So for example if there
                                # are multiple 'address' node for a host (mac and ipv4) it will only used the first
                                # one, which is usually the ipv4 address. This will be changed going forward so one
                                # can decide which specific addresses to keep etc.
                                se = se.getElementsByTagName(dottedtag)[0]
                            # gather the attributes for the elements that have the tag specified
                            for attr in se.attributes.items():
                                # and save them to the csv row
                                if len(dottedtag.split('.')) > 1:
                                    self.add_attribute_to_csv_row(str(attr[0]), str(attr[1]))
                                    # infodict.update({str(parentnodename) + '.' + str(attr[0]): str(attr[1])})
                                else:
                                    self.add_attribute_to_csv_row(str(attr[0]), str(attr[1]))
                                    # infodict.update({
                                    #     str(parentnodename) + '.' + dottedtag.split('.')[-1] + '.' + str(attr[0]): str(
                                    #         attr[1])})
                            # gather all sub-info of this element. Not currently sure why this behaves correctly with
                            # regards to recursiveness since I don't have an 'if recursive' statement here. ???
                            self.get_tag_info('all', [se], parentnodename, recursive)
                            parentnodename = self.get_host_ip(node)
                        # if the dotted tag is a specific attribute of an element, grab that attribute's value and add
                        # it to the csv row
                        elif toa == 'attribute':
                            se = subelement
                            for tag in dottedtag.split('.')[0:-1]:
                                se = se.getElementsByTagName(tag)[0]
                                parentnodename = parentnodename + '.' + tag
                            if se.getAttribute(dottedtag.split('.')[-1]):
                                # infodict.update({str(parentnodename) + '.' + str(dottedtag.split('.')[-1]): str(se.getAttribute(dottedtag.split('.')[-1]))})
                                self.add_attribute_to_csv_row(str(dottedtag.split('.')[-1]), str(se.getAttribute(dottedtag.split('.')[-1])))
                                parentnodename = self.get_host_ip(node)
                                break
            if currentrow != defaultcurrentrow:
                csvout.writerow(currentrow)
            currentrow = list(defaultcurrentrow)

# file argument code. Will be re-implemented once testing slows down.
# try:
#     opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["inputfile=", "outputfile="])
# except getopt.GetoptError:
#     print 'rynnmapparser.py -i <inputfile> -o [outputfile] '
#     sys.exit(2)
# for opt, arg in opts:
#     if opt == '-h':
#         print 'rynnmapparser.py -i <inputfile> -o [outputfile] '
#         sys.exit()
#     elif opt in ("-i", "--inputfile"):
#         inputfile = arg
#     elif opt in ("-o", "--outputfile"):
#         outputfile = arg


outputfile = 'testoutput.csv'
#infodict = {}
defaultcurrentrow = []
currentrow = []
cols = []
myparser = Parser(filexml)

with open(outputfile, 'wb') as csvfile:
    csvout = csv.writer(csvfile, delimiter = "," ,quotechar = '"', dialect = csv.QUOTE_NONE)
    myparser.get_tag_info(testtag, None, None, recurse)
# myparser.get_tag_info()
# print str(infodict)

with open(outputfile, 'r') as csvfile:
    original = csvfile.read()
with open(outputfile, 'wb') as csvfile:
    csvout = csv.writer(csvfile, delimiter = "," ,quotechar = '"', dialect = csv.QUOTE_NONE)
    csvout.writerow(cols)
with open(outputfile, 'a') as csvfile:
    csvfile.write(original)
sys.exit()