


import os
import xml.dom.minidom



class DaisyBook:
    def __init__(self, folder):
        self.folder = folder
        self.parse()

    def f(self,x):
        return os.path.join(self.folder,x)

    def parse(self):
        DOMTree = xml.dom.minidom.parse(self.f("master.smil"))
        self.smil_meta = { meta.getAttribute('name') : meta.getAttribute('content') 
                           for meta in DOMTree.documentElement.getElementsByTagName('meta') }        
        self.smil_refs = [  [ ref.getAttribute('src'), ref.getAttribute('title')  ]
                            for ref in DOMTree.documentElement.getElementsByTagName('ref') ]
    def title(self):
        return self.smil_meta['dc:title']

    def duration(self):
        return self.smil_meta['ncc:timeInThisSmil']

    def refs(self):
        return self.smil_refs


    def dump(self,pfn):
        pfn("Book Title   : ",self.title())
        pfn("Book Duration: ",self.duration())
        for f in self.refs():
            pfn("  + ",f[1], " ( ", f[0], " ) ")
