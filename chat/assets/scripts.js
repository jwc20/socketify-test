function get_room(name, on_history, on_message){
    const ws = new WebSocket(`ws://localhost:3000?room=${name}`);
    var status = 'pending';
    const connection = new Promise((resolve) => {
        ws.onopen = function(){
            status = 'connected';
            resolve(true)
        }
        ws.onerror = function(){
            status = 'error';
            resolve(false)
        }   
    });

    ws.onclose = function(){
        status = 'closed';
    }
    ws.onmessage = (event) => {
       const message = JSON.parse(event.data);  
        if(Array.isArray(message)){
            on_history(message)
        } else {
            on_message(message)
        }
    }

    return {
        send(message){
            ws.send(JSON.stringify(message));
        },
        wait_connection(){
            return connection;
        },
        is_connected(){
            return status === 'connected';
        },
        close(){
            ws.close()
        }
    }
}

function get_utc_date(){
    return new Date().toLocaleTimeString('en-US', { hour12:false, hour: '2-digit', minute: '2-digit', timeZone: 'UTC', timeZoneName: 'short' })
}

let current_room = null;
let last_room_name = 'general';

async function send_message(event){
    if(event && event.key?.toLowerCase() !== 'enter') return;
    
    const message = document.querySelector("#chat-message");
    await current_room?.wait_connection();
    if(current_room?.is_connected()){
        current_room.send({
            text: message.value,
            datetime: get_utc_date()
        })
        //clean
        message.value = ''
    } else {
        await open_room(last_room_name)
        send_message();
    }
}

async function open_room(name){
    last_room_name = name;
    current_room?.close()
    
    const chat = document.querySelector('.chat-messages');
    
    const room = get_room(name, (history) => {
        //clear
        chat.innerHTML = '';
        //add messages
        for(let message of history){
            chat.appendChild(format_message(message));
        }
        chat.scroll(0, chat.scrollHeight)
    }, (message) => {
        //add message
        chat.appendChild(format_message(message));

        //trim size
        while(chat.childNodes.length > 100){
            chat.firstChild.remove();
        }
        chat.scroll(0, chat.scrollHeight)
    });
    await room.wait_connection()
    current_room = room;
}

const markdown = new showdown.Converter({simpleLineBreaks: true, openLinksInNewWindow: true, emoji: true, ghMentions: true, tables: true, strikethrough: true, tasklists: true});

function format_message(message){
    const message_element = document.createElement("div");
    message_element.classList.add('chat-message-left'); 
    message_element.classList.add('pb-4');
    
    const header = document.createElement("div");
    const image = new Image(40, 40);
    image.src = message.avatar_url || 'https://example.com/default-avatar.png';
    image.classList.add('rounded-circle');
    image.classList.add('mr-1');
    image.alt = message.name || 'Anonymous';

    const date = document.createElement("div");
    date.classList.add('text-muted', 'small', 'text-nowrap', 'mt-2');
    date.textContent = message.datetime;
    header.appendChild(image);
    header.appendChild(date);

    message_element.appendChild(header);

    const body = document.createElement("div");
    body.classList.add('flex-shrink-1', 'bg-light', 'rounded', 'py-2', 'px-3', 'mr-3');
    
    const author = document.createElement("div")
    author.classList.add('font-weight-bold', 'mb-1');
    author.textContent = message.name || 'Anonymous';
    
    body.appendChild(author);
    const content = document.createElement("div");
    content.innerHTML = markdown.makeHtml(message.text);
    body.appendChild(content);
    
    message_element.appendChild(body);

    return message_element;
}

// Automatically open the general room when the script loads
open_room("general");
