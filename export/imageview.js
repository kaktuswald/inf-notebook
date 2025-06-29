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
    if(event.data instanceof Blob) {
        const blob = new Blob([event.data], {type: 'image/png'});
        const url = URL.createObjectURL(blob);
        $('img#image').attr('src', url);

        return;
    }

    if(typeof event.data === 'string') {
      if(event.data == 'update_information') {
        if($('body#information').length)
          socket.send('get_informationimage');
      }

      if(event.data == 'update_summary') {
        if($('body#summary').length)
          socket.send('get_summaryimage');
      }

      if(event.data == 'update_notesradar') {
        if($('body#notesradar').length)
          socket.send('get_notesradarimage');
      }

      if(event.data == 'update_screenshot') {
        if($('body#screenshot').length)
          socket.send('get_screenshotimage');
      }

      if(event.data == 'update_scoreinformation') {
        if($('body#scoreinformation').length)
          socket.send('get_scoreinformationimage');
      }

      if(event.data == 'update_scoregraph') {
        if($('body#scoregraph').length)
          socket.send('get_scoregraphimage');
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
    socket.send('get_informationimage');
  
  if($('body#summary').length)
    socket.send('get_summaryimage');
  
  if($('body#notesradar').length)
    socket.send('get_notesradarimage');
  
  if($('body#screenshot').length)
    socket.send('get_screenshotimage');
  
  if($('body#scoreinformation').length)
    socket.send('get_scoreinformationimage');

  if($('body#scoregraph').length)
    socket.send('get_scoregraphimage');
}

$(function() {
  const cssValue = getComputedStyle($(':root')[0]).getPropertyValue('--ws-url').trim();
  if(cssValue.length)
    url = cssValue.replace(/^["']|["']$/g, '');

  $('span#url').text(url);

  setInterval(connect, 1000);
});
