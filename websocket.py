from socketify import App, OpCode, CompressOptions

def ws_open(ws):
    print('A WebSocket got connected!')
    ws.send("Hello World!", OpCode.TEXT)

def ws_message(ws, message, opcode):
    #Ok is false if backpressure was built up, wait for drain
    ok = ws.send(message, opcode)
    
app = App()    
app.ws("/*", {
    'compression': CompressOptions.SHARED_COMPRESSOR,
    'max_payload_length': 16 * 1024 * 1024,
    'idle_timeout': 12,
    'open': ws_open,
    'message': ws_message,
    'drain': lambda ws: print(f'WebSocket backpressure: {ws.get_buffered_amount()}'),
    'close': lambda ws, code, message: print('WebSocket closed'),
    'subscription': lambda ws, topic, subscriptions, subscriptions_before: print(f'subscribe/unsubscribe on topic {topic} {subscriptions} {subscriptions_before}'),
})
app.any("/", lambda res,req: res.end("Nothing to see here!'"))
app.listen(3000, lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)))
app.run()
