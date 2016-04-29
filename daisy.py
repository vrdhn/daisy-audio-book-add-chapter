##
## daisy-tools  (C) Vardhan Varma <vardhanvarma@gmail.com>
##  LICENSE:  GPL3
##



import os
import xml.dom.minidom
from  shutil import copyfile
import math

def s2hms(sf):
    """ 100 ==> 00:01:40"""
    f,s = math.modf(float(sf))
    a = s % 60
    s = s / 60
    b = s % 60
    s = s / 60
    return  "%.2d:%.2d:%.2d"%(s,b,a)


def s2hmsf(sf):
    """ 100 ==> 00:01:40"""
    f,s = math.modf(float(sf))
    a = s % 60
    s = s / 60
    b = s % 60
    s = s / 60
    return "%.2d:%.2d:%.2d.%d"%(s,b,a,int(f*1000.0))
             

def hms2s(hms):
    x = [ float(z) for z in hms.split(':')]
    return float(x[0] * 60 * 60 + x[1] * 60 + x[2])

siml_templ = """<?xml version="1.0" encoding="utf-8"?>
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
		<seq dur="{dur}s">
			<par endsync="last" id="par_notice">
				<text src="ncc.html#h1_notice" id="txt_notice"/>
				<seq>
					<audio src="{mp3}" clip-begin="npt=0.000s" clip-end="npt={dur}s" id="aud_notice"/>
				</seq>
			</par>
		</seq>
	</body>
</smil>
"""
## title, elapsed, inthis, dur, mp3



class DaisyBook:
    def __init__(self, logfn,folder):
        self.folder = folder
        self.log = logfn
        if os.path.exists(os.path.join(folder,'master.smil')):            
            self.parse()
            self.todo = None
            self.valid = True
        else:
            self.valid = False;

    def is_valid(self):
        return self.valid
    def f(self,x):
        return os.path.join(self.folder,x)

    def parse(self):
        #self.log('Parsing ' , self.f("master.smil"))
        DOMTree = xml.dom.minidom.parse(self.f("master.smil"))
        self.smil_master = { meta.getAttribute('name') : meta.getAttribute('content') 
                           for meta in DOMTree.documentElement.getElementsByTagName('meta') }        
        self.smil_refs = [  [ ref.getAttribute('src'), ref.getAttribute('title') , self.parse_smil(ref.getAttribute('src')) ]
                            for ref in DOMTree.documentElement.getElementsByTagName('ref') ]

    def parse_smil(self,smil):
        #self.log('Parsing ' , self.f(smil))        
        dom = xml.dom.minidom.parse(self.f(smil))
        ret = {}
        ret["meta"] = {  meta.getAttribute('name') : meta.getAttribute('content') 
                         for meta in dom.documentElement.getElementsByTagName('meta') }
        return ret

    def get_smil(self,idx):
        return self.smil_refs[idx][0]
    
    def title(self):
        return self.smil_master['dc:title']

    def duration(self):
        return self.smil_master['ncc:timeInThisSmil']

    def refs(self):
        return self.smil_refs
            

    def dump(self):
        pfn = self.log
        pfn("Book Title   : ",self.title())
        pfn("Book Duration: ",self.duration())
        for f in self.refs():
            e = f[2]["meta"]["ncc:totalElapsedTime"]
            i = f[2]["meta"]["ncc:timeInThisSmil"]
            n = s2hms( hms2s(e) + hms2s(i))
            pfn("  + ",f[1], " ( ", f[0], " )  [ " , e, n,' ]')
                
    #### Insert, and copy to a folder ####
    def insert(self, idx, mp3file, mp3durn):
        self.todo = [ siml_templ, mp3file, mp3durn ]

    def dom_search(self, dom,tag, main_attr, main_attrval):
        ret = []
        for node in dom.documentElement.getElementsByTagName(tag):
            if node.getAttribute(main_attr) == main_attrval:
                ret.append( node)
        if len(ret) != 1:
            self.log("###ERROR dom_search:",tag,main_attrval,main_attrval,str(node))
        return ret[0]
        
    def copyto(self,outfolder):
        self.outfolder = outfolder
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)
        ## First write out the smil's, and copy the mp3's
        ## Updating the ncc:totalElapsedTime
        mp3s = set()
        time_of_first = self.copyto_smil(0,0,mp3s)
        for x in range(1,len(self.smil_refs)):
            self.copyto_smil(x,self.todo[2],mp3s)
        for mp3 in sorted(mp3s):
            outfile =  os.path.join(self.outfolder,mp3)
            self.log( '     => ',outfile)                    
            copyfile ( os.path.join(self.folder,mp3),outfile)
        ## Now update the mastersmil
        ## time in this smil
        dom = xml.dom.minidom.parse(self.f("master.smil"))
        et_node = self.dom_search(dom,'meta', 'name', 'ncc:timeInThisSmil')
        et_new = s2hmsf(hms2s( et_node.getAttribute('content')) + self.todo[2])
        et_node.setAttribute('content', et_new)
        ## add line after first ref ..
        ref = dom.documentElement.getElementsByTagName('ref')[1]
        par = ref.parentNode
        ref1 = ref.nextSibling
        cp = ref.cloneNode(True)
        cp1 = ref1.cloneNode(True)
        cp.setAttribute('id','id_notice')
        cp.setAttribute('src','notice.smil')
        cp.setAttribute('title','Notice')
        ref.parentNode.insertBefore(cp,ref)
        ref.parentNode.insertBefore(cp1,ref)
        # write out master..
        outfile = os.path.join(self.outfolder, 'master.smil')
        self.log( '     => ',outfile)        
        with  open(outfile,'w') as of:
            of.write(dom.toxml(encoding='utf-8'))
            #dom.writexml(of,encoding='utf-8')
        ## now for the ncc.htm
        dom = xml.dom.minidom.parse(self.f("ncc.html"))
        ## time in this smil
        et_node = self.dom_search(dom,'meta', 'name', 'ncc:totalTime')
        et_new = s2hms(hms2s( et_node.getAttribute('content')) + self.todo[2])
        et_node.setAttribute('content', et_new)        
        ## tocItems
        et_node = self.dom_search(dom,'meta', 'name', 'ncc:tocItems')
        et_new = str(int( et_node.getAttribute('content')) + 1)
        et_node.setAttribute('content', et_new)        
        ## files
        et_node = self.dom_search(dom,'meta', 'name', 'ncc:files')
        et_new = str(int( et_node.getAttribute('content')) + 2)
        et_node.setAttribute('content', et_new)
        ## add h1 after first h1
        ref = dom.documentElement.getElementsByTagName('h1')[1]
        par = ref.parentNode
        ref1 = ref.nextSibling
        cp = ref.cloneNode(True)
        cp1 = ref1.cloneNode(True)
        ref.parentNode.insertBefore(cp,ref)
        ref.parentNode.insertBefore(cp1,ref)
        cp.setAttribute('id','h1_notice')
        for x in cp.getElementsByTagName('a'):
            x.setAttribute('href','notice.smil#text_notice')
            x.firstChild.replaceWholeText('Notice')        
        ## write out ncc
        outfile = os.path.join(self.outfolder, 'ncc.html')
        self.log( '     => ',outfile)        
        with  open(outfile,'w') as of:
            of.write(dom.toxml(encoding='utf-8'))
            #dom.writexml(of,encoding='utf-8')
        ## writeout the notice.smil
        outfile = os.path.join(self.outfolder, 'notice.smil')
        self.log( '     => ',outfile)        
        with  open(outfile,'w') as of:
            of.write( self.todo[0].format(
                dur = str(self.todo[2]),
                mp3 = 'notice.mp3',
                elapsed = s2hms(time_of_first),
                inthis = s2hms(self.todo[2]),
                title = self.title()))
        ## finally the mp3 file..
        outfile = os.path.join(self.outfolder, 'notice.mp3')
        self.log( '     => ',outfile)        
        copyfile(self.todo[1],outfile)
        
        
        
    def copyto_smil( self, idx, et_delta,mp3s):
        """ Take number to add to et , and return self time """
        dom = xml.dom.minidom.parse(self.f(self.smil_refs[idx][0]))
        et_node = self.dom_search(dom,'meta', 'name', 'ncc:totalElapsedTime')
        et_new = s2hms(hms2s( et_node.getAttribute('content')) + et_delta)
        et_node.setAttribute('content', et_new)

        el_node = self.dom_search(dom,'meta', 'name', 'ncc:timeInThisSmil')
        el = hms2s( el_node.getAttribute('content'))
        
        outfile = os.path.join(self.outfolder, self.smil_refs[idx][0])
        self.log( '     => ',outfile)        
        with  open(outfile,'w') as of:
            of.write(dom.toxml(encoding='utf-8'))
            #dom.writexml(of,encoding='utf-8')

        for au in dom.documentElement.getElementsByTagName('audio'):
            mp3s.add( au.getAttribute('src'))

        return el
        
