"""Abre a interface instalada, sem acessar CUPS ou enviar impressão."""
import sys
sys.path.insert(0, '/usr/share/zebra-raw')
import core
core.printers = lambda: [('Zebra', 'usb://Zebra/GC420t')]
from zebra import Window
from gi.repository import GLib, Gtk
window = Window()
window.show_all()
GLib.timeout_add(500, Gtk.main_quit)
Gtk.main()
assert window.printer.get_active_id() == 'Zebra'
assert window.settings().width == 100
print('Interface instalada: OK')
