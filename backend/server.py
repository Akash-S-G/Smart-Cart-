from websocket_server import WebsocketServer

def new_client(client, server):
    print("ESP32 connected")

def message_received(client, server, message):
    print("Received from ESP32:", message)
    # You can forward this to Flask-SocketIO if needed

server = WebsocketServer(host='0.0.0.0', port=8765)
server.set_fn_new_client(new_client)
server.set_fn_message_received(message_received)
server.run_forever()