const Events = Object.freeze({
  UPDATE_MEMO: 'update_memo',
});

const Requests = Object.freeze({
  GET_MEMO: 'get_memo',
});

const Statuses = Object.freeze({
  SUCCESS: 'success',
  INVALID: 'invalid',
  FAILED: 'failed',
});

const DataTypes = Object.freeze({
  TEXT_PLAIN: 'text/plain',
  APP_JSON: 'application/json',
  IMAGE_PNG: 'image/png',
  IMAGE_JPG: 'image/jpg',
});

let url = null;
let socket = null;

let musictable = null;
let notesradar = null;

let selected_playtype = null;
let selected_songname = null;
let selected_difficulty = null;

let memo = null;

$(function() {
  webui.setEventCallback((e) => {
    if(e == webui.event.CONNECTED) initialize();
  });

  $('button#button_ok').on('click', onclick_ok);
});

async function initialize() {
  document.body.addEventListener('contextmenu', e => e.stopPropagation(), true);

  musictable = JSON.parse(await webui.getresource_musictable());
  notesradar = JSON.parse(await webui.getresource_notesradar());

  const setting = JSON.parse(await webui.get_setting());
  const port = setting.port;

  url = (await webui.get_url()).replace(port.main, port.socket);

  setInterval(connect, 1000);
}

async function connect() {
  if(socket != null) return;

  socket = new WebSocket(url);

  socket.addEventListener('open', (event) => {
    $('div#setting').css('display', 'none');

    sendmessage(Requests.GET_MEMO);
  });

  socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);

    if('s' in data && data.s === Statuses.SUCCESS) {
      if('r' in data && data.r == Requests.GET_MEMO) {
        const payload = data.p;
        const d = payload.d;
        if(Object.keys(d).length) {
          selected_playtype = d.playtype;
          selected_songname = d.songname;
          selected_difficulty = d.difficulty;

          memo = d.memo;

          display_chartdata();
        }
        else {
          clear_chartdata();
        }
      }
    }

    if('e' in data) {
      if(data.e == Events.UPDATE_MEMO)
        sendmessage(Requests.GET_MEMO);
    }
  });

  socket.addEventListener('error', (event) => {
    socket.close();
  });

  socket.addEventListener('close', (event) => {
    socket = null;

    clear_chartdata();
  });
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

/**
 * 譜面情報をクリアする
 */
function clear_chartdata() {
  $('div#musicname').text('');
  $('div#playmode').text('');
  $('div#difficulty').text('');
  $('div#version').text('');
  $('div#level').text('');

  const textarea = $('textarea#textarea_memo');
  textarea.val('');
  textarea.prop('disabled', true);

  $('button#button_ok').prop('disabled', true);
}

/**
 * 選択譜面の情報を表示する
 * 
 * 選択された譜面の曲名・プレイモード・バージョン・レベルを表示する。
 */
async function display_chartdata() {
  const playmode = selected_playtype.includes('BATTLE') ? 'SP' : selected_playtype;

  let version = null;
  let level = null;
  if(selected_songname in musictable.musics) {
    version = musictable.musics[selected_songname].version;
    if(playmode in musictable.musics[selected_songname]) {
      if(selected_difficulty in musictable.musics[selected_songname][playmode])
        level = musictable.musics[selected_songname][playmode][selected_difficulty];
    }
  }

  $('div#musicname').text(selected_songname);
  $('div#playmode').text(playmode);
  $('div#difficulty').text(selected_difficulty);
  $('div#version').text(version !== null ? version : '');
  $('div#level').text(level !== null ? level : '');

  const textarea = $('textarea#textarea_memo');
  textarea.val(memo);
  textarea.prop('disabled', false);

  $('button#button_ok').prop('disabled', false);
}

function onclick_ok(e) {
  webui.save_memo(
    selected_playtype,
    selected_songname,
    selected_difficulty,
    $('textarea#textarea_memo').val(),
  );
}
