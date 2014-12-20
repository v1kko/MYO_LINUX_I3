import websocket
import thread
import time
import subprocess
import signal
import sys
import json


class Myo():
    
    def __init__(self, unlocked=True ):
        self.unlocked = unlocked
        self.synced = False
        self.initialized = False
        self.myo = 0

    def send(self, message):
        ws.send(json.dumps(message));



    def on_message(self, ws, message):

        m = json.loads(message)

        if self.initialized == False and self.synced == True:
            lp = "none" if self.unlocked else "default"
            message = ["command", {"command": "set_locking_policy", "type": lp }]
            self.send(message)
            self.initialized = True


        if self.synced == False and m[1]['type'] != 'arm_synced':
            return

        if m[0] == 'event':
            m = m[1]
            if m['type'] == 'pose':
                if m['pose'] == "wave_in":
                    subprocess.Popen(['i3', 'workspace', 'next'])
                if m['pose'] == "wave_out":
                    subprocess.Popen(['i3', 'workspace', 'previous'])

                print message
            if m['type'] == 'arm_synced' and self.synced == False:
                print "#MYO SYNCED"
                self.synced = True
                self.myo = m
                print message
            if m['type'] == 'arm_unsynced' and m['myo'] == self.myo:
                print "MYO UNSYNCED"
                self.synced = False
                self.initialized = False
                print message





def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
        ws.close()
signal.signal(signal.SIGINT, signal_handler)

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    print "#SYNC MYO BEFORE STARTING"

if __name__ == "__main__":
    myo_com = Myo(True)
    cmd = ["ssh", "windows", "-L10138:localhost:10138"]
    subprocess.Popen(cmd, shell = False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #LOLOL UGLY HACK
    time.sleep(3)

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:10138/myo/3",
                              on_message = myo_com.on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
