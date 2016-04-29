#!/usr/bin/env python2

##
## daisy-tools  (C) Vardhan Varma <vardhanvarma@gmail.com>
##  LICENSE:  GPL3
##


import xml.dom.minidom
import xml.etree.ElementTree as ET
import os.path

import os
import cStringIO
import xml.sax
from xml.sax.handler import ContentHandler,EntityResolver,DTDHandler
from xml.sax import make_parser
import sys
from  xml.sax.saxutils import escape, quoteattr
import zipfile

from daisy import DaisyBook



##class BaseHandler(ContentHandler,EntityResolver,DTDHandler):
##
##    def __init__(self,infile,outfile, trigger, before, insert):
##        self.out = open(outfile,'w')
##        self.tag = False
##        self.trigger = trigger
##        self.before = before
##        self.insert = insert
##        self.triggered = False
##        parser = make_parser()
##        parser.setContentHandler(self)
##        parser.setDTDHandler( self )
##        parser.setEntityResolver( self )        
##        datasource = open(infile,"r")
##        self.write(datasource.readline())
##        self.write(datasource.readline())
##        parser.parse(datasource)
##        self.out.write('\n')
##        self.out.close()
##        datasource.close()
##        
##    def write(self,*str):
##        self.out.write(''.join(str))
##
##    def do_attr(self,tag,order, attr):
##        allattr = { x:0 for x in attr.getNames()}
##        ret = []
##        for o in order:
##            if o in allattr:
##                ret.append([o,attr.getValue(o)])
##                del allattr[o]
##        if len(allattr) > 0:
##            print "ERROR: ATTR:" , allattr.keys()
##        if len(ret) > 0:
##            if not self.triggered:
##                if self.trigger[0] == tag:
##                    for n in ret:
##                        if self.trigger[1] == n[0] and self.trigger[2] == n[1].split('#')[0]:
##                            print "TRIGGERED"
##                            self.triggered = True                                                    
##            self.updateAttrVal(tag,ret)
##            return ' ' + ' '.join(['%s=%s'%(x[0],quoteattr(x[1])) for x in ret])
##        else:
##            return ''
##
##    def startElement(self, name, attrs):
##        if self.tag:
##            self.write('>')
##            self.tag = False
##        if self.triggered and name in self.before[0]:
##            self.triggered = False
##            print "CAPTURED"
##            self.write(self.insert)
##        self.write( '<',name, self.do_attr(name,self.order(name),attrs))
##        self.tag = True
##        
##
##    def endElement(self,name):
##        if self.tag:
##            self.write('/>')
##            self.tag = False
##        else:
##            if self.triggered and name in self.before[1]:
##                self.triggered = False
##                print "CAPTURED"
##                self.write(self.insert)                
##            self.write('</',name,'>')            
##        
##    def characters(self,str):
##        if self.tag:
##            self.write('>')
##            self.tag = False
##        self.write(escape(str).replace('\n','\n'))
##        
##    
##class MasterSMILHandler(BaseHandler):
##
##    def order(self,tag):
##        ors = { 'smil' : [],
##                   'head' : [],
##                   'meta' : [ 'name', 'content' ],
##                   'layout' : [],
##                   'region' : [ 'id' ],
##                   'body' : [ ],
##                   'ref' : [ 'src', 'title', 'id' ] }
##        return ors[tag]                           
##        
##
##    def updateAttrVal(self,tag,attrs):
##        newval = None
##        if tag == 'meta':
##            if attrs[0][1] == 'ncc:timeInThisSmil':
##                newval  = "mew"
##        if newval:
##                print "Changing %s from %s to %s" % ( attrs[0][1], attrs[1][1], newval)
##                attrs[1][1] = newval
##
##
##class NccHTMLHandler(BaseHandler):
##    
##    def order(self,tag):
##        ors  = { 'html' : [ 'xml:lang', 'lang', 'xmlns' ],
##                   'head' : [],
##                   'meta' : [ 'name', 'http-equiv', 'content',  'scheme' ],
##                   'title': [ ],
##                   'body' : [ ],                   
##                   'h1' : [ 'id', 'class' ],
##                   'a' : [ 'href'  ],
##                   'span' : [ 'id', 'class' ]
##        }
##        return ors[tag]                           
##    def updateAttrVal(self,tag,attrs):
##        newval = None
##        if tag == 'meta':
##            if attrs[0][1] == "ncc:tocItems":
##                newval  = "mew"
##            elif attrs[0][1] == "ncc:totalTime":
##                newval  = "mew"
##            elif attrs[0][1] == "ncc:files":
##                newval  = "mew"
##        if newval:
##                print "Changing %s from %s to %s" % ( attrs[0][1], attrs[1][1], newval)
##                attrs[1][1] = newval
##            
##
##                
##        
##
##def update(folderin, folderout, copyright_mp3file, copyright_duration,aftersmil):
##
##    MasterSMILHandler(os.path.join(folderin,'master.smil'),
##                      os.path.join(folderout,'master.smil'),
##                      ['ref', 'src', aftersmil], 
##                      [ set(['ref']),set(['body'])],
##                      '<ref src="copyright.smil" title="Copyright" id="ref_copyright"/>\n		')
##    
##    NccHTMLHandler(os.path.join(folderin,'ncc.html'),
##                   os.path.join(folderout,'ncc.html'),
##                   [ 'a', 'href', aftersmil],
##                   [ set(['h1']),set(['body'])],
##		   '<h1 id="h1_copyright" class="section"><a href="copyright.smil">Copyright</a></h1>\n		')
##
##
##



def convert( input_dir ,
             output_dir ,
             notice_file ,
             notice_durn ,
             logfn):
    ## Recurse in input_Dir
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)
    notice_file = os.path.abspath(notice_file)
    notice_durn = float(notice_durn)
    for root, dir, files in os.walk(input_dir):
        logfn("Checking ",root)
        db = DaisyBook(logfn,root)
        if db.is_valid():
            db.dump()
            after = db.get_smil(0)
            title = db.title()
            #outfolder = os.path.join(output_dir,title.replace(' ','-'))
            outfolder = os.path.join(output_dir,
                                     os.path.basename(root))
            logfn("-----------------------------------------------")
            logfn(" Found book: ",title)
            logfn(" ** Inserting Notice after ",after)
            logfn(" Book will be written to ", outfolder)
            db.insert(1, notice_file, notice_durn)
            db.copyto(outfolder)
            dbc = DaisyBook(logfn,outfolder)
            logfn("Checking ",root)
            if not dbc.is_valid():
                logfn('  ***** FAILED *****')
            dbc.dump()
            logfn('And we are done with this ...')
    return True

        

if __name__ == "__main__":
    def log(*args):
        print ' '.join([str(y) for y in args])
    if len(sys.argv) != 5:
        print "Usage: ./convert.py <input_dir> <output_dir> <notice_file> <notice_durn>"
    else:
        convert(input_dir = sys.argv[1],
                output_dir = sys.argv[2],
                notice_file = sys.argv[3],
                notice_durn = sys.argv[4],
                logfn = log)
        
