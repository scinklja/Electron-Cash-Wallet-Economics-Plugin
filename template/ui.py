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
        total_invest = 0
        total_received = 0
        total_sent = 0


        for x in c.history():
            value = float(x["value"]) * 100000000
            timestamp = datetime.fromtimestamp(x["timestamp"])
            investment = float(self.parent.fx.historical_value_str(value, timestamp))
            total_invest = total_invest + investment
            if investment > 0:
                total_received = total_received + investment
            else:
                total_sent = total_sent + investment

        balance = float(c.history()[0]["balance"]) * 100000000
        balance_bch = float(c.history()[0]["balance"])

        balance_usd = float(self.parent.fx.historical_value_str(balance, datetime.now()))

        profit_usd = balance_usd - total_invest





        item1=QTreeWidgetItem([
            _("Current balance"),
            _(str(balance_usd)),
            _(str(balance_bch))])
        self.addTopLevelItem(item1)

        item2 = QTreeWidgetItem([
            _("Profit"),
            _(str(profit_usd)),
            _(str(balance_bch))])
        self.addTopLevelItem(item2)

        item3 = QTreeWidgetItem([
            _("Total received"),
            _(str(total_received)),
            _(str(balance_bch))])
        self.addTopLevelItem(item3)

        item4 = QTreeWidgetItem([
            _("Total sent"),
            _(str(total_sent)),
            _(str(balance_bch))])
        self.addTopLevelItem(item4)
