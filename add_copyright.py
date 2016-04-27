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


copyrightsmil = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE smil PUBLIC "-//W3C//DTD SMIL 1.0//EN" "http://www.w3.org/TR/REC-smil/SMIL10.dtd">
<smil>
	<head>
		<meta name="dc:identifier" content="EA22"/>
		<meta name="dc:title" content="{title}"/>
		<meta name="dc:format" content="Daisy 2.02"/>
		<meta name="title" content="{title}"/>
		<meta name="ncc:totalElapsedTime" content="{elapsed}"/>
		<meta name="ncc:timeInThisSmil" content="{inthis}"/>
		<meta name="ncc:generator" content="Regenerator 0.6.172"/>
		<layout>
			<region id="txtView"/>
		</layout>
	</head>
	<body>
		<seq dur="{dur}">
			<par endsync="last" id="par_copyright">
				<text src="ncc.html#h1_copyright" id="txt_copyright"/>
				<seq>
					<audio src="{mp3}" clip-begin="npt=0.000s" clip-end="npt="{dur}" id="aud_copyright"/>
				</seq>
			</par>
		</seq>
	</body>
</smil>
"""

class BaseHandler(ContentHandler,EntityResolver,DTDHandler):

    def __init__(self,infile,outfile, trigger, before, insert):
        self.out = open(outfile,'w')
        self.tag = False
        self.trigger = trigger
        self.before = before
        self.insert = insert
        self.triggered = False
        parser = make_parser()
        parser.setContentHandler(self)
        parser.setDTDHandler( self )
        parser.setEntityResolver( self )        
        datasource = open(infile,"r")
        self.write(datasource.readline())
        self.write(datasource.readline())
        parser.parse(datasource)
        self.out.write('\n')
        self.out.close()
        datasource.close()
        
    def write(self,*str):
        self.out.write(''.join(str))

    def do_attr(self,tag,order, attr):
        allattr = { x:0 for x in attr.getNames()}
        ret = []
        for o in order:
            if o in allattr:
                ret.append([o,attr.getValue(o)])
                del allattr[o]
        if len(allattr) > 0:
            print "ERROR: ATTR:" , allattr.keys()
        if len(ret) > 0:
            if not self.triggered:
                if self.trigger[0] == tag:
                    for n in ret:
                        if self.trigger[1] == n[0] and self.trigger[2] == n[1].split('#')[0]:
                            print "TRIGGERED"
                            self.triggered = True                                                    
            self.updateAttrVal(tag,ret)
            return ' ' + ' '.join(['%s=%s'%(x[0],quoteattr(x[1])) for x in ret])
        else:
            return ''

    def startElement(self, name, attrs):
        if self.tag:
            self.write('>')
            self.tag = False
        if self.triggered and name in self.before[0]:
            self.triggered = False
            print "CAPTURED"
            self.write(self.insert)
        self.write( '<',name, self.do_attr(name,self.order(name),attrs))
        self.tag = True
        

    def endElement(self,name):
        if self.tag:
            self.write('/>')
            self.tag = False
        else:
            if self.triggered and name in self.before[1]:
                self.triggered = False
                print "CAPTURED"
                self.write(self.insert)                
            self.write('</',name,'>')            
        
    def characters(self,str):
        if self.tag:
            self.write('>')
            self.tag = False
        self.write(escape(str).replace('\n','\n'))
        
    
class MasterSMILHandler(BaseHandler):

    def order(self,tag):
        ors = { 'smil' : [],
                   'head' : [],
                   'meta' : [ 'name', 'content' ],
                   'layout' : [],
                   'region' : [ 'id' ],
                   'body' : [ ],
                   'ref' : [ 'src', 'title', 'id' ] }
        return ors[tag]                           
        

    def updateAttrVal(self,tag,attrs):
        newval = None
        if tag == 'meta':
            if attrs[0][1] == 'ncc:timeInThisSmil':
                newval  = "mew"
        if newval:
                print "Changing %s from %s to %s" % ( attrs[0][1], attrs[1][1], newval)
                attrs[1][1] = newval


class NccHTMLHandler(BaseHandler):
    
    def order(self,tag):
        ors  = { 'html' : [ 'xml:lang', 'lang', 'xmlns' ],
                   'head' : [],
                   'meta' : [ 'name', 'http-equiv', 'content',  'scheme' ],
                   'title': [ ],
                   'body' : [ ],                   
                   'h1' : [ 'id', 'class' ],
                   'a' : [ 'href'  ],
                   'span' : [ 'id', 'class' ]
        }
        return ors[tag]                           
    def updateAttrVal(self,tag,attrs):
        newval = None
        if tag == 'meta':
            if attrs[0][1] == "ncc:tocItems":
                newval  = "mew"
            elif attrs[0][1] == "ncc:totalTime":
                newval  = "mew"
            elif attrs[0][1] == "ncc:files":
                newval  = "mew"
        if newval:
                print "Changing %s from %s to %s" % ( attrs[0][1], attrs[1][1], newval)
                attrs[1][1] = newval
            

                
        

def update(folderin, folderout, copyright_mp3file, copyright_duration,aftersmil):

    MasterSMILHandler(os.path.join(folderin,'master.smil'),
                      os.path.join(folderout,'master.smil'),
                      ['ref', 'src', aftersmil], 
                      [ set(['ref']),set(['body'])],
                      '<ref src="copyright.smil" title="Copyright" id="ref_copyright"/>\n		')
    
    NccHTMLHandler(os.path.join(folderin,'ncc.html'),
                   os.path.join(folderout,'ncc.html'),
                   [ 'a', 'href', aftersmil],
                   [ set(['h1']),set(['body'])],
		   '<h1 id="h1_copyright" class="section"><a href="copyright.smil">Copyright</a></h1>\n		')




update('StoriesForChildren',
       'In-Start',
       'Copyright_Notice_Saksham/aud001_Copyright_Notice_English.mp3',
       61.4,
       'dtb_0001.smil')
update('StoriesForChildren',
       'In-End',
       'Copyright_Notice_Saksham/aud001_Copyright_Notice_English.mp3',
       61.4,
       'dtb_0031.smil')

