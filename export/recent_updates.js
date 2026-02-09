// 「最近」として表示する履歴の範囲 (単位:時間)
const timeWindow = 12;

// 更新のあるリザルトのみに表示を絞るか
const showUpdatedOnly = true;

const Events = Object.freeze({
  UPDATE_RECENTRECORDS: 'update_recentrecords',
});

const Requests = Object.freeze({
  GET_MUSICTABLE: 'get_musictable',
  GET_RECENTRECORDS: 'get_recentrecords',
});

const Statuses = Object.freeze({
  SUCCESS: 'success',
  INVALID: 'invalid',
  FAILED: 'failed',
})

let url = null;
let socket = null;
let musictable = null;
let looprequest = null;

async function connect() {
    if(socket != null) return;

    socket = new WebSocket(url);

    socket.addEventListener('open', (event) => {
        sendmessage(Requests.GET_MUSICTABLE);
    });

    socket.addEventListener('message', (event) => {
        try {
            let data = JSON.parse(event.data);
            if('e' in data) {
                if(data['e'] == Events.UPDATE_RECENTRECORDS) {
                    sendmessage(Requests.GET_RECENTRECORDS);
                }
            }

            if('s' in data && data['s'] == Statuses.SUCCESS) {
                if (data.r == Requests.GET_MUSICTABLE) {
                    musictable = data.p.d;
                    $("#setting").css("display", "none");
                    $("#content").css("display", "block");
                    sendmessage(Requests.GET_RECENTRECORDS);
                } else if (data.r == Requests.GET_RECENTRECORDS) {
                    applyData(data.p.d);
                }
            }
        } catch(e) {
            console.error(e);
        }
    });

    socket.addEventListener('error', (event) => {
        console.error(event);
        socket.close();
    });

    socket.addEventListener('close', (event) => {
        socket = null;
    });
}

function applyData(data) {
    let out = "<div></div><div class='header'>Music</div><div class='header'>Lamp</div><div class='header'>Score</div><div class='header'>BP</div>";
    let timestamps = data["timestamps"];

    // 履歴の足切り日時の文字列を yyyymmdd-hhmmss 形式で取得
    let now = new Date();
    let threshold = new Date(now.getTime() - timeWindow * 60 * 60 * 1000);
    let yyyy = threshold.getFullYear().toString();
    let mm = (threshold.getMonth() + 1).toString().padStart(2, '0');
    let dd = threshold.getDate().toString().padStart(2, '0');
    let hh = threshold.getHours().toString().padStart(2, '0');
    let min = threshold.getMinutes().toString().padStart(2, '0');
    let ss = threshold.getSeconds().toString().padStart(2, '0');
    let timestamp_threshold = yyyy + mm + dd + '-' + hh + min + ss;

    timestamps.filter(ts => ts > timestamp_threshold).sort((a, b) => b.localeCompare(a)).forEach(function(ts){
        let entry = data["results"][ts];

        if (showUpdatedOnly && !entry["update_clear_type"] && !entry["update_dj_level"] && !entry["update_score"] && !entry["update_miss_count"]) {
            return;
        }

        let difficulty = entry["difficulty"];
        let playtype = entry["playtype"];
        let title = entry["music"];
        let playspeed = entry["playspeed"];
        let lamp = entry["update_clear_type"];
        let score = entry["update_score"];
        let bp = entry["update_miss_count"];
        let options = entry["option"];
        
        let level = null;
        try {
            if (playtype == "DP") {
                level = musictable["musics"][title]["DP"][difficulty];
            } else {
                // DBの難易度はSP準拠
                level = musictable["musics"][title]["SP"][difficulty];
            }
        } catch(e) {
        }

        // DB系のプレイオプションを反映
        let db_options = "";
        if (playtype === "DP BATTLE") {
            playtype = 'DP'
            if (options.indexOf("A-SCR")<0){
                db_options = "皿あり";
            }
            if ((options.indexOf("MIR/OFF")>=0) || (options.indexOf("OFF/MIR")>=0)){
                db_options += 'DBM'
            }
            else if (options.indexOf("OFF/OFF")>=0){
                db_options += 'DB'
            }
            else if (options.indexOf("RAN/RAN")>=0){
                db_options += 'DBR'
            }
            else if (options.indexOf("S-RAN/S-RAN")>=0){
                db_options += 'DBSR'
            }
            else if (options.indexOf("H-RAN/H-RAN")>=0){
                db_options += 'DBHR'
            }
        }

        title = `${title} (${playtype + difficulty.slice(0,1)})`
        if (playspeed) {
            title = `<span class="plain">(x${playspeed})</span> ${title}` 
        }
        if (db_options != ""){
            title = `<span class="plain">(${db_options})</span> ${title}`;
        }


        out += `<div class="level">${level === null ? '' : '☆' + level}</div>`
        out += `<div class="title ${difficulty}">${title}</div>`
        out += `<div class="lamp ${lamp}">${lamp === null ? '' : lamp}</div>`
        out += `<div class="score">${score === null ? '' : "+" + score}</div>`;
        out += `<div class="miss_count">${bp === null ? '' : bp}</div>`;
    });
    $('#result').html(out);
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

window.addEventListener('DOMContentLoaded', function() {
    const cssValue = getComputedStyle($(':root')[0]).getPropertyValue('--ws-url').trim();
    if(cssValue.length)
        url = cssValue.replace(/^["']|["']$/g, '');
    $('span#url').text(url);

    looprequest = setInterval(connect, 5000);
});
