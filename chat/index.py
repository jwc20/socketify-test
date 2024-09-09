from socketify import App, sendfile, CompressOptions, OpCode
import json
from datetime import datetime

app = App()

def get_welcome_message(room):
    return {
    "username": "@cirospaciari/socketify.py",
    "html_url": "https://www.github.com/cirospaciari/socketify.py",
    "avatar_url": "https://raw.githubusercontent.com/cirospaciari/socketify.py/main/misc/big_logo.png",
    "datetime": "",
    "name": "socketify.py",
    "text": f"Welcome to chat room #{room} :heart: be nice! :tada:"
}

RoomsHistory = {
    "general": [get_welcome_message("general")],
    "open-source": [get_welcome_message("open-source")],
    "reddit": [get_welcome_message("reddit")]
}

async def home(res, req):
    await sendfile(res, req, "./index.html")

async def ws_upgrade(res, req, socket_context):
    key = req.get_header("sec-websocket-key")
    protocol = req.get_header("sec-websocket-protocol")
    extensions = req.get_header("sec-websocket-extensions")
    room = req.get_query("room")
    if RoomsHistory.get(room, None) is None:
        return res.write_status(403).end("invalid room")

    user_data = {
        "room": room,
        "username": f"User_{datetime.now().timestamp()}",
        "name": "Anonymous",
        "avatar_url": "https://example.com/default-avatar.png"
    }
    res.upgrade(key, protocol, extensions, socket_context, user_data)

def ws_open(ws):
    user_data = ws.get_user_data()
    room = user_data.get("room", "general")
    ws.subscribe(room)

    history = RoomsHistory.get(room, [])
    if history:
        ws.send(json.dumps(history), OpCode.TEXT)

def ws_message(ws, message, opcode):
    try:
        message_data = json.loads(message)
        text = message_data.get('text', None)
        if text and len(text) < 1024 and message_data.get('datetime', None):
            user_data = ws.get_user_data()
            room = user_data.get("room", "general")
        
            message_data.update(user_data)
            history = RoomsHistory.get(room, [])
            if history:
                history.append(message_data)
                if len(history) > 100:
                    history = history[-100:]
            
            ws.publish(room, json.dumps(message_data), OpCode.TEXT)

    except:
        pass

app.get("/", home)
app.static("/assets", "./assets")

app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 64 * 1024,
        "idle_timeout": 12,
        "open": ws_open,
        "message": ws_message,
        "upgrade": ws_upgrade
    },
)

app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()
