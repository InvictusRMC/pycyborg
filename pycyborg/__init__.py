import usb.core
import time
import sys


# --- device info ---
VENDOR=0x06a3
PRODUCT=0x0dc5
CONFIGURATION=1


# protocol constants

COMMAND={
  'enable':0xa1,
  'color':0xa2,
  'position':0xa4,
  'v_position':0xa5,
  'intensity':0xa6,
  'reset':0xa7,
}

POSITION={
 'CENTER':[0x00,0x01],
 'N':[0x01,0x00],
 'NE':[0x02,0x00],
 'E':[0x04,0x00],
 'SE':[0x08,0x00],
 'S':[0x10,0x00],
 'SW':[0x20,0x00],
 'W':[0x40,0x00],
 'NW':[0x80,0x00],
}

V_POS={
 'any':0x00,
 'low':0x08,
 'middle':0x04,
 'high':0x02
}


def v2k(val,dic):
    for k,v in dic.iteritems():
        if v==val:
            return k


class Cyborg(object):
    def __init__(self,usbdev):
        self.usbdev=usbdev
        self.position=None
        self.vertical_position=None
        self.intensity=None
        
    def initialize(self):
        """initialize the device"""
        self.usbdev.set_configuration(CONFIGURATION)
        self._usb_idle_request()
        self._usb_reset_request()
        self._usb_get_report()

    def _usb_idle_request(self):
        self.usbdev.ctrl_transfer(bmRequestType=0x21, bRequest=0x0a, wValue=0x00, wIndex=0, data_or_wLength=None)

    def _usb_reset_request(self):
        self.usbdev.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x03a7, wIndex=0, data_or_wLength=[0xa7,0x00])
 
    def _usb_get_report(self):
        """read the cyborg device status like position and intensity"""
        arraydata=self.usbdev.ctrl_transfer(bmRequestType=0xa1, bRequest=0x01, wValue=0x03b0, wIndex=0, data_or_wLength=9)
        data=arraydata.tolist()
        assert data[0:4]==[0xb0,0x00,0x00,0x01], 'unexpected device status info start: %s'%(data[0:4])
        assert data[8]==1,'unexpected last byte value: %s'%data[8]
        position=data[4:6]
        v_pos=data[6]
        self.vertical_position=v2k(v_pos,V_POS)
        self.intensity=data[7]
        self.position=v2k(position,POSITION)
        
    def set_rgb_color(self,r=0,g=0,b=0):
        """Set the light to a specific color"""
        r=int(r)
        g=int(g)
        b=int(b)
        assert r>=0 and r<=255
        assert g>=0 and g<=255
        assert b>=0 and b<=255
        
        self.usbdev.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x03a2, wIndex=0, data_or_wLength=[0xa2,0x00,r,g,b,0x00,0x00,0x00,0x00])
    
    def lights_off(self):
        self.set_rgb_color(0,0,0)
    
    def set_intensity(self,intensity):
        """sets intensity value (0-100)"""
        intensity=int(intensity)
        assert intensity>=0 and intensity<=100
        self.usbdev.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x03a6, wIndex=0, data_or_wLength=[0xa6,0x00,intensity])
        self.intensity=intensity
        
    def set_position(self,position):
        """set the device position. allowed values are: CENTER,N,NE,E,SE,S,SW,W,NW"""
        assert position in POSITION
        posbytes=POSITION[position]
        self.usbdev.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x03a4, wIndex=0, data_or_wLength=[0xa4,0x00,posbytes[0],posbytes[1]])
        self.position=position

    def set_vertical_position(self,verticalposition):
        """set the vertical position. allowed values are: any, low, middle, high"""
        assert verticalposition in V_POS
        posbyte=V_POS[verticalposition]
        self.usbdev.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x03a5, wIndex=0, data_or_wLength=[0xa5,0x00,posbyte])
        self.position=verticalposition

    def __str__(self):
        return "<Cyborg position=%s v_pos=%s intensity=%s%%>"%(self.position,self.vertical_position,self.intensity) 

def get_all_cyborgs():
    """Search usb bus for cyborg gaming ligts and return all initialized Cyborg objects"""
    retlist=[]
    devs=usb.core.find(find_all=True,idVendor=VENDOR,idProduct=PRODUCT)
    for dev in devs:
        c=Cyborg(dev)
        try:
            c.initialize()
            retlist.append(c)
        except:
            import traceback
            ex=traceback.format_exc()
            sys.stderr.write("Cyborg initialization failed : %s"%ex)

    return retlist


if __name__=='__main__':
    cyborgs=get_all_cyborgs()
    print "found %s cyborg gaming lights"%(len(cyborgs))
    
    for cy in cyborgs:
        print "Cyborg:"
        print cy
        cy.set_rgb_color(255,0,0)
        time.sleep(2)
        cy.lights_off()
    
    print "done"
        
    
