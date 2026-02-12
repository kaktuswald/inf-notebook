let url = null;
let socket = null;
let musictable = null;
let looprequest = null;

async function connect() {
    console.log("connecting...");
    if(socket != null) return;

    socket = new WebSocket(url);

    socket.addEventListener('open', (event) => {
        console.log("websocket opened.");
        socket.send(JSON.stringify({ "r" : "get_musictable" }));
    });

    socket.addEventListener('message', (event) => {
        console.log("message received.");
        try {
            let data = JSON.parse(event.data);
            if (data.s == 'success') {
                if (data.r == 'get_musictable') {
                    musictable = data.p.d;

                    // 楽曲リストをロードできたら、履歴表示を開始
                    $("#setting").css("display", "none");
                    $("#content").css("display", "block");

                    socket.send(JSON.stringify({ "r" : "get_scoreresult" }));
                }

                if (data.r == 'get_scoreresult') {
                    if (musictable === null) return;

                    applyData(data.p.d);
                }
            }

            if ('e' in data && data.e == 'update_scoreresult')
                socket.send(JSON.stringify({ "r" : "get_scoreresult" }));
        } catch(e) {
            console.log(e);
        }
    });

    socket.addEventListener('error', (event) => {
        console.log("websocket error:");
        console.log(event);
        socket.close();
    });

    socket.addEventListener('close', (event) => {
        console.log("websocket closed.");
        socket = null;

        $('div#content').css('display', 'none');
        $('div#setting').css('display', 'flex');
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

window.addEventListener('DOMContentLoaded', function() {
    const cssValue = getComputedStyle($(':root')[0]).getPropertyValue('--ws-url').trim();
    if(cssValue.length)
        url = cssValue.replace(/^["']|["']$/g, '');
    $('span#url').text(url);

    looprequest = setInterval(connect, 1000);
});
