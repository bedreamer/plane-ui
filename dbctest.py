# -*- coding: utf-8 -*-
# author: lijie
import cantools

from pprint import pprint
db = cantools.database.load_file('/Users/lijie/workspace/plane-ui/DFLZM_S50EV_EV&PTCAN_BMS_CAN_V1.0.9L9_20180515.dbc')
for message in db.messages:
    for signal in message.signals:
        print(signal.name, signal.initial)
