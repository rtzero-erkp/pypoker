from websocket import create_connection

def client_handle():
    ws = create_connection('wss://192.168.199.220:5000/poker/texas-holdem')

    # ws = create_connection('ws://192.168.199.220:5000/poker/texas-holdem')
    # ws = create_connection('ws://172.0.0.1:5000/poker/texas-holdem')
    # ws = create_connection('ws://0.0.0.0:5000/poker/texas-holdem')
    # ws = create_connection('ws://127.0.0.1:5000/poker/texas-holdem')
    # ws = create_connection('ws://127.0.0.1:5001/poker/texas-holdem')
    while True:
        if ws.connected:
            ws.send('hi,i am ws client')
            result = ws.recv()
            print(f"client received:{result}")
            # ws.close()

if __name__ == "__main__":
    client_handle()