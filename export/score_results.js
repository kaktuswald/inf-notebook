const Events = Object.freeze({
  UPDATE_SCORERESULT: 'update_scoreresult',
  UPDATE_RECENTRECORDS: 'update_recentrecords',
});

const Requests = Object.freeze({
  GET_MUSICTABLE: 'get_musictable',
  GET_SCORERESULT: 'get_scoreresult',
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
                if(data['e'] == Events.UPDATE_SCORERESULT || data['e'] == Events.UPDATE_RECENTRECORDS) {
                    sendmessage(Requests.GET_SCORERESULT);
                }
            }

            if('s' in data && data['s'] == Statuses.SUCCESS) {
                if (data.r == Requests.GET_MUSICTABLE) {
                    musictable = data.p.d;
                    $("#setting").css("display", "none");
                    $("#content").css("display", "block");
                    sendmessage(Requests.GET_SCORERESULT);
                } else if (data.r == Requests.GET_SCORERESULT) {
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

function optionToString(options){
    if (options === null) {
        return "???";
    }
    let out = [];
    if (options.arrange !== null) {
        out.push(options.arrange);
    }
    if (options.flip !== null) {
        out.push(options.flip);
    }
    if (options.battle) {
        out.push("BATTLE");
    }
    if (options.assist !== null) {
        out.push(options.assist);
    }
    return out.join(",");
}

function applyData(data) {
    if (!data["result"]) {
        return;
    }
    let timestamps = data["result"]["timestamps"];
    let title = data["music"]["musicname"];
    let difficulty = data["music"]["difficulty"];
    let playtype = data["music"]["playtype"];
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

    $("#title").html(`☆${level} ${title} (${playtype == 'DP BATTLE' ? 'DB' : playtype}${difficulty.slice(0,1)})`);
    
    let best_score = "???";
    let best_score_opt = "???";
    if (data["result"]["best"]["score"] !== undefined) {
        best_score = data["result"]["best"]["score"]["value"];
        best_score_opt = optionToString(data["result"]["best"]["score"]["options"]);        
    }
    let best_bp = "???";
    let best_bp_opt = "???";
    if (data["result"]["best"]["miss_count"] !== undefined) {
        best_bp = data["result"]["best"]["miss_count"]["value"];
        best_bp_opt = optionToString(data["result"]["best"]["miss_count"]["options"]);
    }
    let best_html = "";
    best_html += `<div class="score">best(score)</div><div class="score value">${best_score}</div><div class="options">${best_score_opt}</div>`;
    best_html += `<div class="bp">best(bp)</div><div class="bp value">${best_bp}</div><div class="options">${best_bp_opt}</div>`;
    $('#best').html(best_html);

    let out = "";
    timestamps.sort((a, b) => b.localeCompare(a)).forEach(function(ts){
        let entry = data["result"]["history"][ts];
        
        let date = ts.slice(0,4) + '-' + ts.slice(4,6) + '-' + ts.slice(6,8);
        let lamp = entry["clear_type"]["value"];
        let rank = entry["dj_level"]["value"];
        let score = entry["score"]["value"];
        let playspeed = entry["playspeed"] ? `x${entry["playspeed"]}` : "";
        let opt = optionToString(entry["options"]);
        let bp = entry["miss_count"]["value"];
        if (bp === null) {
            bp = "???";
        }

        // テーブルに追加
        out += `<div class="date">${date}</div>`;
        out += `<div><span class="${lamp}">　</span></div>`;
        out += `<div class="rank ${rank}">${rank}</div>`;
        out += `<div class="score value">${score}</div>`;
        out += `<div class="bp value">${bp}</div>`;
        out += `<div class="plain">${playspeed}</div>`;
        out += `<div class="options">${opt}</div>`;

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

    looprequest = setInterval(connect, 1000);
});
