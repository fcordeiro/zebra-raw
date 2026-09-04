import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import core

class CoreTests(unittest.TestCase):
    def test_settings(self):
        z=core.Settings(width=104,length=30,method='D',media='M',speed=4).zpl(True)
        self.assertIn(b'^PW832^LL240',z)
        self.assertIn(b'^MTD^MNM^MMT',z)
        self.assertIn(b'^JUS',z)
        self.assertNotIn(b'^JUS',core.Settings().zpl())
    def test_limits(self):
        for kw in [dict(width=105),dict(speed=5),dict(darkness=31),dict(length=float('nan')),dict(method='x')]:
            with self.assertRaises(ValueError):core.Settings(**kw).zpl()
    def test_raw_bytes(self):
        data=b'^XA\r\n^FO1,1^FD\xe7\xe3^FS^XZ\r\n'
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'label.txt';p.write_bytes(data)
            self.assertEqual(core.read_zpl(p),data)
            p.write_bytes(b'ordinary text')
            with self.assertRaises(ValueError):core.read_zpl(p)
    @patch('core.printers',return_value=[('Zebra','usb://GC420t')])
    @patch('core.run',return_value='request id is Zebra-42 (1 file(s))')
    def test_transport(self,run,printers):
        data=b'^XA^FDhello^FS^PQ2^XZ'
        core.submit('Zebra',data,'a; $(bad)',2)
        args,payload=run.call_args.args
        self.assertEqual(payload,data*2)
        self.assertIn('raw',args)
        self.assertEqual(args[-1],'a; $(bad)')
        with self.assertRaises(ValueError):core.submit('Canon',data,'x')
    @patch('core.run',return_value='device for Canon: usb://Canon\ndevice for Zebra: usb://Zebra/ZTC%20GC420t%20(EPL)?serial=x')
    def test_filter(self,_):self.assertEqual(core.printers()[0][0],'Zebra');self.assertEqual(len(core.printers()),1)

if __name__=='__main__':unittest.main()
