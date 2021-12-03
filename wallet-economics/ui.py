import decimal

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from electroncash.i18n import _
from electroncash.util import profiler
from electroncash_gui.qt.util import MyTreeWidget, MessageBoxMixin, MONOSPACE_FONT, rate_limited
from datetime import datetime
from electroncash.commands import Commands


class Ui(MyTreeWidget, MessageBoxMixin):
    def __init__(self, parent, plugin, wallet_name):
        MyTreeWidget.__init__(self, parent, self.create_menu, [
            _(''),
            _(parent.fx.ccy),
            _(parent.base_unit()),

        ], 0, [], deferred_updates=True)

        self.plugin = plugin
        self.wallet_name = wallet_name

    def create_menu(self):
        pass
        
    @rate_limited(5.0, classlevel=True, ts_after=True) # We rate limit the refresh to no more than once every X seconds, app-wide
    def update(self):
        super().update()

    def on_delete(self):
        pass

    @profiler
    def on_update(self):
        self.clear()
        window = self.parent
        commands = Commands(window.config, window.wallet, window.network, lambda: set_json(True))
        total_historical_fiat_value = 0
        total_received_fiat = 0
        total_sent_fiat = 0
        total_received_sats = 0
        total_sent_sats = 0


        history = commands.history()
        for tx in history:
            value_sats = decimal.Decimal(tx["value"]) * 100000000
            timestamp = datetime.fromtimestamp(tx["timestamp"])
            historical_fiat_value = window.fx.historical_value(value_sats, timestamp)
            if historical_fiat_value is None:
                return

            total_historical_fiat_value = total_historical_fiat_value + historical_fiat_value
            if historical_fiat_value > 0:
                total_received_fiat = total_received_fiat + historical_fiat_value
            else:
                total_sent_fiat = total_sent_fiat + historical_fiat_value
            if value_sats > 0:
                total_received_sats = total_received_sats + value_sats
            else:
                total_sent_sats = total_sent_sats + value_sats

        if len(history) == 0:
            balance_sats = 0
        else:
            balance_sats = decimal.Decimal(history[0]["balance"]) * 100000000



        balance_fiat = window.fx.historical_value(balance_sats, datetime.now())

        profit_fiat = balance_fiat - total_historical_fiat_value

        average_received_BCH_price = total_received_fiat/total_received_sats * 100000000

        average_sent_BCH_price = total_sent_fiat/total_sent_sats * 100000000


        items = []

        item1=QTreeWidgetItem([
            _("Current balance"),
            _(window.fx.ccy_amount_str(balance_fiat, True)),
            _(str(window.format_amount(balance_sats, whitespaces=True)))])
        items.append(item1)

        item2 = QTreeWidgetItem([
            _("Profit"),
            _(window.fx.ccy_amount_str(profit_fiat, True)),
            _(str(" "))])
        items.append(item2)

        item3 = QTreeWidgetItem([
            _("Total received"),
            _(window.fx.ccy_amount_str(total_received_fiat, True)),
            _(str(window.format_amount(total_received_sats, whitespaces=True)))])
        items.append(item3)

        item4 = QTreeWidgetItem([
            _("Total sent"),
            _(window.fx.ccy_amount_str(total_sent_fiat, True)),
            _(str(window.format_amount(total_sent_sats, whitespaces=True)))])
        items.append(item4)

        item5 = QTreeWidgetItem([
            _("Average received BCH price"),
            _(window.fx.ccy_amount_str(average_received_BCH_price, True)),
            _(str(" "))])
        items.append(item5)

        item6 = QTreeWidgetItem([
            _("Average sent BCH price"),
            _(window.fx.ccy_amount_str(average_sent_BCH_price, True)),
            _(str(" "))])
        items.append(item6)
        
        self.addTopLevelItems(items)

        monospaceFont = QFont(MONOSPACE_FONT)
        for item in items:
            for column in [1, 2]:
                item.setFont(column, monospaceFont)
                item.setTextAlignment(column, Qt.AlignRight | Qt.AlignVCenter)
