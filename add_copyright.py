#!/usr/bin/env python2

import xml.etree.ElementTree as ET
import os.path

import os
import cStringIO
import xml.sax
from xml.sax.handler import ContentHandler,EntityResolver,DTDHandler
from xml.sax import make_parser
import sys
from  xml.sax.saxutils import escape, quoteattr



class BaseHandler(ContentHandler,EntityResolver,DTDHandler):

    def __init__(self,folder,infile,outfile):
        self.out = open(os.path.join(folder,outfile),'w')
        self.tag = False        
        parser = make_parser()
        parser.setContentHandler(self)
        parser.setDTDHandler( self )
        parser.setEntityResolver( self )        
        datasource = open(os.path.join(folder,infile),"r")
        self.write(datasource.readline())
        self.write(datasource.readline())
        parser.parse(datasource)
        self.out.write('\r\n')
        self.out.close()
        datasource.close()
        
    def write(self,*str):
        self.out.write(''.join(str))

    def do_attr(self,order, attr):
        allattr = { x:0 for x in attr.getNames()}
        ret = []
        for o in order:
            if o in allattr:
                ret.append([o,attr.getValue(o)])
        
        if len(ret) > 0:
            return ' ' + ' '.join(['%s=%s'%(x[0],quoteattr(x[1])) for x in ret])
        else:
            return ''

    
class MasterSMILHandler(BaseHandler):
    
    def startElement(self, name, attrs):
        orders = { 'smil' : [],
                   'head' : [],
                   'meta' : [ 'name', 'content' ],
                   'layout' : [],
                   'region' : [ 'id' ],
                   'body' : [ ],
                   'ref' : [ 'src', 'title', 'id' ] }
        order = orders[name]                           
        if self.tag:
            self.write('>')
            self.tag = False
        self.write( '<',name, self.do_attr(order,attrs))
        self.tag = True
        

    def endElement(self,name):
        if self.tag:
            self.write('/>')
            self.tag = False
        else:
            self.write('</',name,'>')            
        

    def characters(self,str):
        if self.tag:
            self.write('>')
            self.tag = False
        self.write(escape(str).replace('\n','\r\n'))

class Handler(BaseHandler):
    
    def startElement(self, name, attrs):
        orders = { 'smil' : [],
                   'head' : [],
                   'meta' : [ 'name', 'content' ],
                   'layout' : [],
                   'region' : [ 'id' ],
                   'body' : [ ],
                   'ref' : [ 'src', 'title', 'id' ] }
        order = orders[name]                           
        if self.tag:
            self.write('>')
            self.tag = False
        self.write( '<',name, self.do_attr(order,attrs))
        self.tag = True
        

    def endElement(self,name):
        if self.tag:
            self.write('/>')
            self.tag = False
        else:
            self.write('</',name,'>')            
        

    def characters(self,str):
        if self.tag:
            self.write('>')
            self.tag = False
        self.write(escape(str).replace('\n','\r\n'))

        

def update(folder,copyright_mp3file, copyright_duration):

    MasterSMILHandler(folder,'master.smil','master.smil.new')
    Ncc:Revision(folder,'ncc.html','ncc.html.new')




update('StoriesForChildren','Copyright_Notice_Saksham/aud001_Copyright_Notice_English.mp3',61.4)

