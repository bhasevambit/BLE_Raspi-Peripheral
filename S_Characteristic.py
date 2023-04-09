from pybleno import Characteristic

# --- モジュール間グローバル変数使用のためのインポート ---
import global_value as g
# --------------------------------------------------------

import socket  # BMX055センサ制御プログラムからのメッセージTCP受信のために、socketモジュールをインポート


class S_Characteristic(Characteristic):

    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['notify'],
            'value': None
        })

        self._value = str(0).encode()
        self._updateValueCallback = None

    # BLEセントラル側からBLE Notifyリクエスト受信時に実行(発火)
    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('S_Characteristic - onSubscribe')

        self._updateValueCallback = updateValueCallback

        print('--- Now, BLE Notify START ---')

        g.Notify_FLAG = 1  # BLE Notify開始を受け、モジュール間グローバル変数g.Notify_FLAGを上げる

    def onUnsubscribe(self):  # BLEセントラル側からBLE Notify停止リクエスト受信時に実行(発火)
        print('S_Characteristic - onUnsubscribe')

        self._updateValueCallback = None

        print('--- BLE Notify STOP ---')

        g.Notify_FLAG = 0  # BLE Notify停止を受け、モジュール間グローバル変数g.Notify_FLAGを下げる

    def notify_message(self, notify_flag):  # main関数からの呼び出しを受けて実行(発火)
        # === notify_flagが上がっている場合のみSコマンドメッセージの発出を行う ===
        if notify_flag == 1:

            # ----------------------------------------------------------------------------------------------
            # ----- BMX055センサ値を元にした方位角(0〜359)含むC言語ファームウェアメッセージ値のTCP受信 -----
            # ----------------------------------------------------------------------------------------------

            # --- TCP待受設定(TCPサーバ有効化) ---
            # TCP ListenするIPアドレスを指定 (今回のSコマンドではlocalhost(=127.0.0.1)を指定)
            HOST_NAME = "127.0.0.1"
            PORT = 7777  # TCP ListenするTCPポート番号を指定 (今回のSコマンドでは7777を指定)

            # socketクラスから生成したインスタンスオブジェクト(=socketクラスを継承).
            # インスタンスオブジェクト生成にあたり、address famili=AF_INET(=IPv4), socket
            # type=SOCK_STREAM(=TCP)を指定
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            # 「socket-in-use exception」回避のための設定(と推測) [MEMO:] 参考コードにおける詳細経緯確認要
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST_NAME, PORT))  # bindメソッドにより、ソケットにIPアドレスとポート番号を割り当てる
            s.listen(0)  # listenメソッドにより、ソケットを接続待機状態とする
            # ------------------------------------

            # --- TCPクライアントからの接続要求・データ受信 ---
            # クライアントからの接続要求を受けて、接続確立するために、acceptメソッドを使用.
            # 接続確立時、返り値であるソケットオブジェクトをcleinetsocketに、相手方IPアドレスをaddress変数に格納する
            clientsocket, address = s.accept()
            # ソケットオブジェクトcleinetsocketのreceメソッドを用いて、ソケットから送られたデータを受信(bufsizeは256byte設定).
            # 加えて、返り値である受信データのバイトオブジェクトをTcp_rcv_Message変数に格納する
            Tcp_rcv_Message = clientsocket.recv(256)
            print('TCP Receive Data(byte object) = %s' %
                  (Tcp_rcv_Message))  # 受信データ(バイトオブジェクト)の標準出力表示
            print('TCP Receive Data(UTF-8) = %s' %
                  (Tcp_rcv_Message.decode("utf-8")))  # 受信データ(UTF-8)の標準出力表示
            # -------------------------------------------------

            # --- BLE NotifyによるSコマンドメッセージ送信 ---
            # TCP受信した方位角含むメッセージ値(UTF-8)をS_Command_Messageに格納
            S_Command_Message = Tcp_rcv_Message.decode("utf-8")

            # Sコマンドメッセージの標準出力表示(for Terminal Monitering)
            print(
                'Sending notification with value : ' +
                str(S_Command_Message))
            notificationBytes = str(S_Command_Message).encode()
            self._updateValueCallback(
                data=notificationBytes)  # BLE NotifyによるSコマンドメッセージの発出
            # -----------------------------------------------
