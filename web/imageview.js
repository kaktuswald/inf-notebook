const socket = new WebSocket('ws://localhost:8765/');

$(function() {
  socket.addEventListener('open', (event) => {
  });

  socket.addEventListener('message', (event) => {
    if(event.data == 'update_information') {
      const timestamp = new Date().getTime();
      $('img#image_information').attr('src', `image/information.png?${timestamp}`);
    }

    if(event.data == 'update_screenshot') {
      const timestamp = new Date().getTime();
      $('img#image_screenshot').attr('src', `image/screenshot.png?${timestamp}`);
    }

    if(event.data == 'update_summary') {
      const timestamp = new Date().getTime();
      $('img#image_summary').attr('src', `image/summary.png?${timestamp}`);
    }

    if(event.data == 'update_notesradar') {
      const timestamp = new Date().getTime();
      $('img#image_notesradar').attr('src', `image/notesradar.png?${timestamp}`);
    }

    if(event.data == 'update_scoreinformation') {
      const timestamp = new Date().getTime();
      $('img#image_scoreinformation').attr('src', `image/scoreinformation.png?${timestamp}`);
    }

    if(event.data == 'update_scoregraph') {
      const timestamp = new Date().getTime();
      $('img#image_scoregraph').attr('src', `image/scoregraph.png?${timestamp}`);
    }
  });

  socket.addEventListener('error', (event) => {
  });

  socket.addEventListener('close', (event) => {
  });
});
