const Events = Object.freeze({
  UPDATE_INFORMATIONIMAGE: 'update_informationimage',
  UPDATE_SUMMARYIMAGE: 'update_summaryimage',
  UPDATE_NOTESRADARIMAGE: 'update_notesradarimage',
  UPDATE_SCREENSHOTIMAGE: 'update_screenshotimage',
  UPDATE_SCOREINFORMATIONIMAGE: 'update_scoreinformationimage',
  UPDATE_SCOREGRAPHIMAGE: 'update_scoregraphimage',
});

const Requests = Object.freeze({
  GET_INFORMATIONIMAGE: 'get_informationimage',
  GET_SUMMARYIMAGE: 'get_summaryimage',
  GET_NOTESRADARIMAGE: 'get_notesradarimage',
  GET_SCREENSHOTIMAGE: 'get_screenshotimage',
  GET_SCOREINFORMATIONIMAGE: 'get_scoreinformationimage',
  GET_SCOREGRAPHIMAGE: 'get_scoregraphimage',
});

const Statuses = Object.freeze({
  SUCCESS: 'success',
  INVALID: 'invalid',
  FAILED: 'failed',
})

const DataTypes = Object.freeze({
  TEXT_PLAIN: 'text/plain',
  APP_JSON: 'application/json',
  IMAGE_PNG: 'image/png',
  IMAGE_JPG: 'image/jpg',
})

let url = "ws://localhost:8765"

let socket = null;

async function connect() {
  if(socket != null) return;

  socket = new WebSocket(url);

  socket.addEventListener('open', (event) => {
    $('div#setting').css('display', 'none');
    getrequest();
  });

  socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);

    if('s' in data && data['s'] === Statuses.SUCCESS) {
      const payload = data['p']
      if('t' in payload && payload['t'] === DataTypes.IMAGE_PNG) {
        const binary = atob(payload['d']);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++)
          bytes[i] = binary.charCodeAt(i);

        const blob = new Blob([bytes], {type: payload['t']});
        const url = URL.createObjectURL(blob);
        $('img#image').attr('src', url);
      }
    }

    if('e' in data) {
      if(data['e'] == Events.UPDATE_INFORMATIONIMAGE) {
        if($('body#information').length)
          sendmessage(Requests.GET_INFORMATIONIMAGE);
      }

      if(data['e'] == Events.UPDATE_SUMMARYIMAGE) {
        if($('body#summary').length)
          sendmessage(Requests.GET_SUMMARYIMAGE);
      }

      if(data['e'] == Events.UPDATE_NOTESRADARIMAGE) {
        if($('body#notesradar').length)
          sendmessage(Requests.GET_NOTESRADARIMAGE);
      }

      if(data['e'] == Events.UPDATE_SCREENSHOTIMAGE) {
        if($('body#screenshot').length)
          sendmessage(Requests.GET_SCREENSHOTIMAGE);
      }

      if(data['e'] == Events.UPDATE_SCOREINFORMATIONIMAGE) {
        if($('body#scoreinformation').length)
          sendmessage(Requests.GET_SCOREINFORMATIONIMAGE);
      }

      if(data['e'] == Events.UPDATE_SCOREGRAPHIMAGE) {
        if($('body#scoregraph').length)
          sendmessage(Requests.GET_SCOREGRAPHIMAGE);
      }
    }
  });

  socket.addEventListener('error', (event) => {
    socket.close();
  });

  socket.addEventListener('close', (event) => {
    socket = null;

    $('img#image').removeAttr('src');
    $('div#setting').css('display', 'flex');
  });
}

function getrequest() {
  if($('body#information').length)
    sendmessage(Requests.GET_INFORMATIONIMAGE);
  
  if($('body#summary').length)
    sendmessage(Requests.GET_SUMMARYIMAGE);
  
  if($('body#notesradar').length)
    sendmessage(Requests.GET_NOTESRADARIMAGE);
  
  if($('body#screenshot').length)
    sendmessage(Requests.GET_SCREENSHOTIMAGE);
  
  if($('body#scoreinformation').length)
    sendmessage(Requests.GET_SCOREINFORMATIONIMAGE);

  if($('body#scoregraph').length)
    sendmessage(Requests.GET_SCOREGRAPHIMAGE);
}

function sendmessage(request, payload = null) {
  let message = null;
  
  if(payload !== null) {
    message = {
      'r': request,
      'p': payload,
    };
  }
  else {
    message = {
      'r': request,
    };
  }

  socket.send(JSON.stringify(message));
}

$(function() {
  const cssValue = getComputedStyle($(':root')[0]).getPropertyValue('--ws-url').trim();
  if(cssValue.length)
    url = cssValue.replace(/^["']|["']$/g, '');

  $('span#url').text(url);

  setInterval(connect, 1000);
});
