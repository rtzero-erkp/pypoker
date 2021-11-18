from websocket import create_connection
ws = create_connection("ws://localhost:5000/poker/texas-holdem")
ws.send("Hello, linyk3")
result = ws.recv()
print(result)
ws.close()
