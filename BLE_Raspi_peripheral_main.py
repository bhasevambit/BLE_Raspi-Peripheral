from pybleno import *
import signal
# Pコマンド(BLE Write )向けCharacteristicモジュールのP_Characteristicクラスをインポート
from P_Characteristic import P_Characteristic
# Sコマンド(BLE Notify)向けCharacteristicモジュールのS_Characteristicクラスをインポート
from S_Characteristic import S_Characteristic

import time  # 0.2秒ウェイト向けのtimeライブラリのインポート

# --- モジュール間グローバル変数使用のためのインポート ---
import global_value as g
# --------------------------------------------------------

# --- No generate bytecode cache ---
import sys
sys.dont_write_bytecode = True
# ----------------------------------


# BLE通信 各種設定値
SERVICE_NAME = 'BLE_TEST'
SERVICE_UUID = 'cdf7b788-df74-4a8e-86df-209297d273ee'
# Sコマンド(BLE Notify)向けCharacteristic UUIDの設定
S_COMMAND_CHARACTERISTIC_UUID = 'f0542e2b-9288-4675-9498-8a1d95cccc80'
# Pコマンド(BLE Write )向けCharacteristic UUIDの設定
P_COMMAND_CHARACTERISTIC_UUID = '7bf9252c-3ed7-4d9e-9c00-83b256e9f04e'


print('================================================')
print('=== BLE Communication by pyBleno ===')
print('================================================')
print('')
print('BLE Notify and BLE Write START ...>>>')
print('')


def onStateChange(state):
    print('on -> stateChange: ' + state)

    if (state == 'poweredOn'):
        bleno.startAdvertising(name=SERVICE_NAME, service_uuids=[SERVICE_UUID])
    else:
        bleno.stopAdvertising()


def onAdvertisingStart(error):
    print('on -> advertisingStart: ' +
          ('error ' + error if error else 'success'))

    if not error:
        bleno.setServices([
            BlenoPrimaryService({
                'uuid': SERVICE_UUID,
                'characteristics': [
                    # S_Characteristicモジュール内のS_Characteristicクラスから生成したインスタンスオブジェクト(=characteristicsクラスを継承)
                    s_Characteristic,
                    # P_Characteristicモジュール内のP_Characteristicクラスから生成したインスタンスオブジェクト(=characteristicsクラスを継承)
                    p_Characteristic
                ]
            })
        ])


# ================
# === main処理 ===
# ================
if __name__ == '__main__':
    bleno = Bleno()  # pyblenoモジュール内のBlenoクラスからインスタンスオブジェクト(=bleno)を生成
    # S_Characteristicモジュール内のS_Characteristicクラスからインスタンスオブジェクト(=s_Characteristic)を生成
    s_Characteristic = S_Characteristic(S_COMMAND_CHARACTERISTIC_UUID)
    # P_Characteristicモジュール内のP_Characteristicクラスからインスタンスオブジェクト(=p_Characteristic)を生成
    p_Characteristic = P_Characteristic(P_COMMAND_CHARACTERISTIC_UUID)

    bleno.on('stateChange', onStateChange)  # BLE onState開始準備
    bleno.on('advertisingStart', onAdvertisingStart)  # BLE Advertise開始準備

    bleno.start()  # BLE処理開始

    # # ====================================================
    # # ==== PコマンドWrite値に応じたサウンドカード制御 ====
    # # ====================================================
    # [INFO:] Pコマンドでのサウンドカード制御については、P_Characteristicモジュール内のonWriteRequestメソッドにて実行される

    # # ======================================================================
    # # ==== BMX055センサ値を元にした方位角(0〜359)の0.2秒周期 SコマンドNotify通知 ====
    # # ======================================================================
    g.Notify_FLAG = 0  # モジュール間グローバルの初期化

    while True:  # BLE Notifyの周期実行
        # インスタンスオブジェクト(=s_Characteristic)のSコマンドnotify_messageメソッドの実行
        s_Characteristic.notify_message(g.Notify_FLAG)
        time.sleep(0.2)  # 0.2秒のウェイト
