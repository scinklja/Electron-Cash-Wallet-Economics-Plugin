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
        window = self.parent
        commands = Commands(window.config, window.wallet, window.network, lambda: set_json(True))
        total_historical_fiat_value = 0
        total_received = 0
        total_sent = 0
        total_received_sats = 0
        total_sent_sats = 0


        for tx in commands.history():
            value_sats = decimal.Decimal(tx["value"]) * 100000000
            timestamp = datetime.fromtimestamp(tx["timestamp"])
            historical_fiat_value = self.parent.fx.historical_value(value_sats, timestamp)
            if historical_fiat_value is None:
                return

            total_historical_fiat_value = total_historical_fiat_value + historical_fiat_value
            if historical_fiat_value > 0:
                total_received = total_received + historical_fiat_value
            else:
                total_sent = total_sent + historical_fiat_value
            if value_sats > 0:
                total_received_sats = total_received_sats + value_sats
            else:
                total_sent_sats = total_sent_sats + value_sats

        if len(commands.history()) == 0:
            balance = 0
        else:
            balance = decimal.Decimal(commands.history()[0]["balance"]) * 100000000



        balance_fiat = self.parent.fx.historical_value(balance, datetime.now())

        profit_fiat = balance_fiat - total_historical_fiat_value





        item1=QTreeWidgetItem([
            _("Current balance"),
            _(str(balance_fiat)),
            _(str(self.parent.format_amount(balance, whitespaces=True)))])
        self.addTopLevelItem(item1)

        item2 = QTreeWidgetItem([
            _("Profit"),
            _(str(profit_fiat)),
            _(str("N/A"))])
        self.addTopLevelItem(item2)

        item3 = QTreeWidgetItem([
            _("Total received"),
            _(str(total_received)),
            _(str(self.parent.format_amount(total_received_sats, whitespaces=True)))])
        self.addTopLevelItem(item3)

        item4 = QTreeWidgetItem([
            _("Total sent"),
            _(str(total_sent)),
            _(str(self.parent.format_amount(total_sent_sats, whitespaces=True)))])
        self.addTopLevelItem(item4)
