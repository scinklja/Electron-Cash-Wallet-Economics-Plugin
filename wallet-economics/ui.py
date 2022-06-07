import decimal

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from electroncash.i18n import _
from electroncash.util import profiler
from electroncash_gui.qt.util import MyTreeWidget, MONOSPACE_FONT, rate_limited
from datetime import datetime
from electroncash.commands import Commands
from electroncash.util import PrintError


class Ui(MyTreeWidget):
    def __init__(self, parent, plugin, wallet_name):
        MyTreeWidget.__init__(self, parent, self.create_menu, [], 0, [], deferred_updates=True)

        self.plugin = plugin
        self.wallet_name = wallet_name


    def refresh_headers(self):
        headers = [
            (''),
            _(self.parent.fx.ccy),
            _(self.parent.base_unit()),
            _("Transactions")
        ]
        self.update_headers(headers)

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
        if not self.parent.fx.show_history() or not self.parent.fx.is_enabled():
            self.update_headers(["Unable to retrieve historical fiat data. Please enable 'Show history rates' and set 'Fiat currency' in Tools>Preferences>Fiat."])
            return


        self.refresh_headers()
        window = self.parent
        commands = Commands(window.config, window.wallet, window.network, lambda: set_json(True))
        total_historical_fiat_value = 0
        total_received_fiat = 0
        total_sent_fiat = 0
        total_received_sats = 0
        total_sent_sats = 0
        number_received_tx = 0
        number_sent_tx = 0


        history = commands.history()
        for tx in history:
            value_sats = decimal.Decimal(tx["value"]) * 100000000
            timestamp = tx["timestamp"]
            date = datetime.fromtimestamp(timestamp) if timestamp != 0 else datetime.now()  #unconfirmed transactions have timestamp 0   
            historical_fiat_value = window.fx.historical_value(value_sats, date)
            if historical_fiat_value is None:
                self.update_headers(["Unable to retrieve historical fiat data. Please change 'Fiat currency' in Tools>Preferences>Fiat."])
                return

            total_historical_fiat_value = total_historical_fiat_value + historical_fiat_value
            if historical_fiat_value > 0:
                total_received_fiat = total_received_fiat + historical_fiat_value
            else:
                total_sent_fiat = total_sent_fiat + historical_fiat_value
            if value_sats > 0:
                total_received_sats = total_received_sats + value_sats
                number_received_tx += 1
            else:
                total_sent_sats = total_sent_sats + value_sats
                number_sent_tx += 1

        if len(history) == 0:
            balance_sats = 0
        else:
            balance_sats = decimal.Decimal(history[0]["balance"]) * 100000000



        balance_fiat = window.fx.historical_value(balance_sats, datetime.now())

        profit_fiat = balance_fiat - total_historical_fiat_value

        if total_received_sats == 0:
            average_received_BCH_price = None
        else:
            average_received_BCH_price = total_received_fiat/total_received_sats * 100000000

        if total_sent_sats == 0:
            average_sent_BCH_price = None
        else:
            average_sent_BCH_price = total_sent_fiat/total_sent_sats * 100000000


        items = []

        item1=QTreeWidgetItem([
            _("Current balance"),
            _(window.fx.ccy_amount_str(balance_fiat, True)),
            _(str(window.format_amount(balance_sats, whitespaces=True))),
            ("")])
        items.append(item1)

        item2 = QTreeWidgetItem([
            _("Profit"),
            _(window.fx.ccy_amount_str(profit_fiat, True)),
            (""),
            ("")])
        items.append(item2)

        item3 = QTreeWidgetItem([
            _("Total received"),
            _(window.fx.ccy_amount_str(total_received_fiat, True)),
            _(str(window.format_amount(total_received_sats, whitespaces=True))),
            _(str(number_received_tx))])
        items.append(item3)

        item4 = QTreeWidgetItem([
            _("Total sent"),
            _(window.fx.ccy_amount_str(total_sent_fiat, True)),
            _(str(window.format_amount(total_sent_sats, whitespaces=True))),
            _(str(number_sent_tx))])
        items.append(item4)

        item5 = QTreeWidgetItem([
            _("Average received BCH price"),
            _(window.fx.ccy_amount_str(average_received_BCH_price, True) if average_received_BCH_price is not None else "N/A"),
            (""),
            ("")])
        items.append(item5)

        item6 = QTreeWidgetItem([
            _("Average sent BCH price"),
            _(window.fx.ccy_amount_str(average_sent_BCH_price, True) if average_sent_BCH_price is not None else "N/A"),
            (""),
            ("")])
        items.append(item6)
        
        self.addTopLevelItems(items)

        monospaceFont = QFont(MONOSPACE_FONT)
        for item in items:
            for column in [1, 2, 3]:
                item.setFont(column, monospaceFont)
                item.setTextAlignment(column, Qt.AlignRight | Qt.AlignVCenter)
