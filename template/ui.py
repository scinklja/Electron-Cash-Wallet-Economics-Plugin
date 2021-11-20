from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from electroncash.i18n import _
from electroncash_gui.qt.util import MyTreeWidget, MessageBoxMixin
from datetime import datetime
from electroncash.commands import Commands

class Ui(MyTreeWidget, MessageBoxMixin):
    def __init__(self, parent, plugin, wallet_name):
        MyTreeWidget.__init__(self, parent, self.create_menu, [
            _(''),
            _('Fiat'),
            _('BCH'),

        ], 0, [])

        self.plugin = plugin
        self.wallet_name = wallet_name

    def create_menu(self):
        pass

    def on_delete(self):
        pass

    def on_update(self):
        w = self.parent
        c = Commands(w.config, w.wallet, w.network, lambda: set_json(True))

        for x in c.history():
            value = float(x["value"]) * 100000000
        item=QTreeWidgetItem([
            _(str(value)),
            _("Blabla"),
            _("Blablabla")])
        self.addTopLevelItem(item)
