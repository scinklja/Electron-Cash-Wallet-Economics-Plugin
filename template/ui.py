import decimal

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
        total_received_bch = 0
        total_sent_bch = 0


        for x in c.history():
            value = decimal.Decimal(x["value"]) * 100000000
            value_bch= decimal.Decimal(x["value"])
            timestamp = datetime.fromtimestamp(x["timestamp"])
            investment = self.parent.fx.historical_value(value, timestamp)
            total_invest = total_invest + investment
            if investment > 0:
                total_received = total_received + investment
            if historical_fiat_value is None:
                return
            else:
                total_sent = total_sent + investment
            if value_bch > 0:
                total_received_bch = total_received_bch + value_bch
            else:
                total_sent_bch = total_sent_bch + value_bch

        if len(c.history()) == 0:
            balance = 0
        else:
            balance = decimal.Decimal(c.history()[0]["balance"]) * 100000000

        if len(c.history()) == 0:
            balance_bch = 0
        else:
            balance_bch = decimal.Decimal(c.history()[0]["balance"])


        balance_usd = self.parent.fx.historical_value(balance, datetime.now())

        profit_usd = balance_usd - total_invest





        item1=QTreeWidgetItem([
            _("Current balance"),
            _(str(balance_usd)),
            _(str(balance_bch))])
        self.addTopLevelItem(item1)

        item2 = QTreeWidgetItem([
            _("Profit"),
            _(str(profit_usd)),
            _(str("N/A"))])
        self.addTopLevelItem(item2)

        item3 = QTreeWidgetItem([
            _("Total received"),
            _(str(total_received)),
            _(str(total_received_bch))])
        self.addTopLevelItem(item3)

        item4 = QTreeWidgetItem([
            _("Total sent"),
            _(str(total_sent)),
            _(str(total_sent_bch))])
        self.addTopLevelItem(item4)
