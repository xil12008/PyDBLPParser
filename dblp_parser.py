#!/usr/bin/python
#-*-coding:utf-8-*-

import xml.sax
import requests
import sys
import string
import json

class DBLPXMLHandler( xml.sax.ContentHandler ):
    dblptag1 = ["article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"]
    authorList = []
    title = ""
    paperKey = ""
    year = ""
    where = ""

    jsonWrite = u""
    count = 0

    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

    def _sendJSON(self):
        #print "SEND JSON::", self.jsonWrite
        jsonOut = u"[%s]" % self.jsonWrite
        jsonOut = jsonOut.decode('iso-8859-1').encode('utf8')

        # jsonOut2 = "{\"subject\": \"J.-Pa. Lév\",\"predicate\": \"publishFirst\",\"object\": \"journals/acta/Levy74\"}"
        # r = requests.post('http://127.0.0.1:64210/api/v1/write', headers=self.headers, data="["+jsonOut2+"]")
        # print r.text

        r = requests.post('http://127.0.0.1:64210/api/v1/write', headers=self.headers, data=jsonOut)
        #print r.text
        return r

    def filterJSON(self, str):
        #str = str.replace('\"', '\\\"')
        i = str.rfind("\n")
        if i != -1:
            #print "#", i, ":", str[i+1:], "<--", str
            return str[i+1:]
        else:
            return str

    def _prepareJSON(self, subject, predicate, object):
        try:
            subject = self.filterJSON(subject)
            object = self.filterJSON(object)
            
            self.jsonWrite = u"{\"subject\": %s,\"predicate\": \"%s\",\"object\": %s}" % (json.dumps(subject), predicate, json.dumps(object) )
            r = self._sendJSON()
            myStr = "%s" % r
            #print r.text
            if myStr.find("200") == -1:
                print r.text
                print r
                print self.jsonWrite
        except Exception as e:
            print e
            file_object = open('logfile.txt','a+')
            file_object.write("<"+str(e.message)+"\n"+self.jsonWrite+">\n")
            file_object.close()
            pass

        # if self.jsonWrite == u"":
        #     self.jsonWrite = u"{\"subject\": \"%s\",\"predicate\": \"%s\",\"object\": \"%s\"}" % (subject, predicate, object )
        # else:
        #     self.jsonWrite += u",{\"subject\": \"%s\",\"predicate\": \"%s\",\"object\": \"%s\"}" % (subject, predicate, object )

    def __init__(self):
        self.lastTag = ""
        self.lastContent = ""
        self.count = 0

    def startElement(self, tag, attributes):
        if tag == "i" or tag == "sub":
            self.lastContent += "<"+tag+">"
            return

        #print 10*"_", "startElement:", tag
        self.lastTag = tag
        if tag in self.dblptag1:
            #print "*****%s*****" % tag
            self.paperKey = attributes["key"]
            #print "Key: %s" %( self.paperKey)

    def endElement(self, tag):
        if tag == "i" or tag == "sub":
            self.lastContent += "</"+tag+">"
            return

        #print 10*"_", "endElement:", tag
        if tag not in self.dblptag1 :
            #print self.lastTag, ": ", self.lastContent
            if tag == "author":
                self.authorList.append(self.lastContent)
            elif tag == "title":
                self.title = self.lastContent
            elif tag == "year":
                self.year = self.lastContent
            elif tag == "journal" or tag == "conference":
                self.where = self.lastContent
        elif tag in self.dblptag1:
            self.count += 1
            i = 0
            for authorItem in self.authorList:
                i += 1
                if i == 1:
                    self._prepareJSON(authorItem, "publishFirst", self.paperKey) #first author
                elif i == len(self.authorList):
                    self._prepareJSON(authorItem, "publishLast", self.paperKey) #last author
                else:
                    self._prepareJSON(authorItem, "publish", self.paperKey) #other authors

            self._prepareJSON(self.paperKey, "hasTitle", self.title)
            self._prepareJSON(self.paperKey, "onYear", self.year)
            self._prepareJSON(self.paperKey, "at", self.where)

            print self.paperKey
            # r = self._sendJSON()
            # print r
            # print r.text

            self.authorList = []
            self.title = ""
            self.paperKey = ""
            self.year = ""
            self.where = ""
            self.jsonWrite = ""
        self.lastTag = ""
        self.lastContent = ""

    def characters(self, content):
        self.lastContent += content

if ( __name__ == "__main__"):


    reload(sys)
    sys.setdefaultencoding("utf-8")

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    parser.setContentHandler( DBLPXMLHandler() )
    parser.parse("dblp2.xml")

    print "finish"
