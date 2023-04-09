from pybleno import Characteristic
import array
import struct
import sys
import traceback

import os  # .iniファイル配置ディレクトリのフルパス取得のために、osモジュールをインポート
import configparser  # .iniファイルからの変数読込みのために、configparserモジュールをインポート
from subprocess import call  # amixerコマンド実行のために、subprocessモジュールからcallメソッドをインポート


class P_Characteristic(Characteristic):

    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read', 'write'],
            'value': None
        })

        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None

    def onReadRequest(self, offset, callback):
        print('P_Characteristic - %s - onReadRequest: value = %s' %
              (self['uuid'], [hex(c) for c in self._value]))
        callback(Characteristic.RESULT_SUCCESS, self._value[offset:])

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data

        print('P_Characteristic - %s - onWriteRequest: value = %s' %
              (self['uuid'], [hex(c) for c in self._value]))

        if self._updateValueCallback:
            print('P_Characteristic - onWriteRequest: notifying')

            self._updateValueCallback(self._value)

        callback(Characteristic.RESULT_SUCCESS)

        # ====================================================
        # ==== PコマンドWrite値に応じたサウンドカード制御 ====
        # ====================================================

        # --- SETTINGS.iniファイルからの設定値読込み ---
        inifile = configparser.SafeConfigParser()

        # 本Pythonコード配置ディレクトリの絶対パスを取得 (=SETTINGS.iniの配置ディレクトリ)
        DirNAME_abs = os.path.dirname(os.path.abspath(__file__))
        print('SETTINGS.ini PATH = %s' % (DirNAME_abs))
        # systemdによるサービス自動実行にあたり、SETTINGS.iniファイルのフルパスでの指定が必須
        inifile.read('%s/SETTINGS.ini' % (DirNAME_abs))

        print('# SETTINGS.ini の設定読込み')
        Front_SC_No = inifile.get('DEFAULT', 'Front_SoundCard_No')
        Rear_SC_No = inifile.get('DEFAULT', 'Rear_SoundCard_No')
        P_00_Front_Vol = inifile.get('DEFAULT', 'P_00_Front_Volume')
        P_00_Rear_Vol = inifile.get('DEFAULT', 'P_00_Rear_Volume')
        P_01_Front_Vol = inifile.get('DEFAULT', 'P_01_Front_Volume')
        P_01_Rear_Vol = inifile.get('DEFAULT', 'P_01_Rear_Volume')
        P_02_Front_Vol = inifile.get('DEFAULT', 'P_02_Front_Volume')
        P_02_Rear_Vol = inifile.get('DEFAULT', 'P_02_Rear_Volume')
        P_03_Front_Vol = inifile.get('DEFAULT', 'P_03_Front_Volume')
        P_03_Rear_Vol = inifile.get('DEFAULT', 'P_03_Rear_Volume')

        print('Front_SC_No = %s' % (Front_SC_No))
        print('Rear_SC_No = %s' % (Rear_SC_No))
        print('P_00_Front_Vol = %s' % (P_00_Front_Vol))
        print('P_00_Rear_Vol = %s' % (P_00_Rear_Vol))
        print('P_01_Front_Vol = %s' % (P_01_Front_Vol))
        print('P_01_Rear_Vol = %s' % (P_01_Rear_Vol))
        print('P_02_Front_Vol = %s' % (P_02_Front_Vol))
        print('P_02_Rear_Vol = %s' % (P_02_Rear_Vol))
        print('P_03_Front_Vol = %s' % (P_03_Front_Vol))
        print('P_03_Rear_Vol = %s' % (P_03_Rear_Vol))
        # ----------------------------------------------

        p_cmd_value_bin = data
        print('P_Command value(binary) = %s' %
              (p_cmd_value_bin))  # PコマンドWrite値のバイナリ表示

        p_cmd_value = int.from_bytes(
            p_cmd_value_bin,
            byteorder='little')  # PコマンドWrite値の10進数変換
        print('P_Command value(decimal) = %s' %
              (p_cmd_value))  # PコマンドWrite値の10進数値表示

        # ==== 重要なポイント====
        # root権限でのシステムワイドなpulseaudioデーモンとの競合を避けるために、amixerコマンドは、piユーザ権限での実行としている
        # =======================
        if p_cmd_value == 0:  # 00：前後両方のサウンドカードをミュート
            call(["sudo",
                  "-u",
                  "pi",
                  "amixer",
                  "-c",
                  str(Front_SC_No),
                  "sset",
                  "Speaker",
                  str(P_00_Front_Vol) + "%",
                  "unmute"])
            call(["sudo",
                  "-u",
                  "pi",
                  "amixer",
                  "-c",
                  str(Rear_SC_No),
                  "sset",
                  "Speaker",
                  str(P_00_Rear_Vol) + "%",
                  "unmute"])
        elif p_cmd_value == 1:  # 01：前方のサウンドカードから出力
            call(["sudo",
                  "-u",
                  "pi",
                  "amixer",
                  "-c",
                  str(Front_SC_No),
                  "sset",
                  "Speaker",
                  str(P_01_Front_Vol) + "%",
                  "unmute"])
            call(["sudo",
                  "-u",
                  "pi",
                  "amixer",
                  "-c",
                  str(Rear_SC_No),
                  "sset",
                  "Speaker",
                  str(P_01_Rear_Vol) + "%",
                  "unmute"])
        elif p_cmd_value == 2:  # 02：後方のサウンドカードから出力
            call(["sudo",
                  "-u",
                  "pi",
                  "amixer",
                  "-c",
                  str(Front_SC_No),
                  "sset",
                  "Speaker",
                  str(P_02_Front_Vol) + "%",
                  "unmute"])
            call(["sudo",
                  "-u",
                  "pi",
                  "amixer",
                  "-c",
                  str(Rear_SC_No),
                  "sset",
                  "Speaker",
                  str(P_02_Rear_Vol) + "%",
                  "unmute"])
        elif p_cmd_value == 3:  # 03：前後両方のサウンドカードから出力
            call(["sudo",
                  "-u",
                  "pi",
                  "amixer",
                  "-c",
                  str(Front_SC_No),
                  "sset",
                  "Speaker",
                  str(P_03_Front_Vol) + "%",
                  "unmute"])
            call(["sudo",
                  "-u",
                  "pi",
                  "amixer",
                  "-c",
                  str(Rear_SC_No),
                  "sset",
                  "Speaker",
                  str(P_03_Rear_Vol) + "%",
                  "unmute"])
        # ----------------------------
