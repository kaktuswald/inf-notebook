let musics = null;

$(function() {
  webui.setEventCallback((e) => {
    if(e == webui.event.CONNECTED) initialize();
    if(e == webui.event.DISCONNECTED) console.log('disconnect.');
  });

  const defaultstartdt = new Date();
  defaultstartdt.setMinutes(defaultstartdt.getMinutes() - defaultstartdt.getTimezoneOffset());
  const startdtstring = defaultstartdt.toISOString().slice(0, 16);

  const defaultenddt = new Date();
  defaultenddt.setMinutes(defaultenddt.getMinutes() - defaultenddt.getTimezoneOffset());
  defaultenddt.setHours(defaultenddt.getHours() + 8);
  const enddtstring = defaultenddt.toISOString().slice(0, 16);

  const defaultpublishdt = new Date();
  defaultpublishdt.setMinutes(defaultpublishdt.getMinutes() - defaultpublishdt.getTimezoneOffset());
  const publishdtstring = defaultpublishdt.toISOString().slice(0, 16);

  $('input#date_start').attr('min', startdtstring);
  $('input#date_start').val(startdtstring);
  $('input#date_end').attr('min', enddtstring);
  $('input#date_end').val(enddtstring);
  $('input#date_publish').attr('max', startdtstring);
  $('input#date_publish').val(publishdtstring);

  $('button.dialogclose').on('click', onclick_dialogclose);

  $('input[name="mode"]').on('change', onchange_mode);

  $('input#date_start').on('change', onchange_datestart);

  $('input#check_private').on('change', onchange_private);

  $('select#select_versions').on('change', onchange_version);
  $('input#text_musicname_search').on('input', oninput_musicname);

  $('button#button_test').on('click', onclick_test);
  $('button#button_register').on('click', onclick_register);
  $('button#button_confirmregister').on('click', onclick_confirmregister);
  $('button#button_close').on('click', onclick_close);
});

/**
 * 初期処理
 * 
 * ロード完了時に実行する。Python側から選択肢のリストを取得する。
 */
async function initialize() {
  document.body.addEventListener('contextmenu', e => e.stopPropagation(), true);

  const setting = JSON.parse(await webui.get_setting());
  $('input#text_authorname').val(setting.discord_webhook.playername);

  const musictable = JSON.parse(await webui.getresource_musictable());

  for(const version in musictable['versions']) {
    $('#select_versions').append($('<option>')
      .val(version)
      .text(version)
    );
  }

  musics = musictable['musics']

  set_musicnames();

  const playmodes = JSON.parse(await webui.get_playmodes());
  for(const playmode of playmodes) {
      $('#select_playmodes').append($('<option>')
        .val(playmode)
        .text(playmode)
      );
  }

  const difficulties = JSON.parse(await webui.get_difficulties());
  for(const difficulty of difficulties) {
      $('#select_difficulties').append($('<option>')
        .val(difficulty)
        .text(difficulty)
      );
  }
}

/**
 * ダイアログを閉じるボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_dialogclose(e) {
  $(this).closest('dialog')[0].close();
}

/**
 * モードを選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_mode(e) {
  const selected_mode = $('input[name="mode"]:checked').attr('id');
  const mode = selected_mode.match(/(?<=radio_mode_)(.*)/)[0];

  if(mode == "battle") {
    $('input#check_private').prop('checked', true);
    $('input#check_private').prop('disabled', true);
    $('input#date_publish').prop('disabled', true);
    $('select#select_versions').addClass('unusable');
    $('input#text_musicname_search').addClass('unusable');
    $('table#table_musicnames').addClass('unusable');
    $('select#select_playmodes').addClass('unusable');
    $('select#select_difficulties').addClass('unusable');
  }
  else {
    $('input#check_private').prop('disabled', false);
    $('input#date_publish').prop('disabled', $('input#check_private').is(':checked'));
    $('select#select_versions').removeClass('unusable');
    $('input#text_musicname_search').removeClass('unusable');
    $('table#table_musicnames').removeClass('unusable');
    $('select#select_playmodes').removeClass('unusable');
    $('select#select_difficulties').removeClass('unusable');
  }
}

/**
 * 期間開始を変更する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_datestart(e) {
  const startdt = new Date($('input#date_start').val());
  startdt.setMinutes(startdt.getMinutes() - startdt.getTimezoneOffset());

  const publishdtmax = startdt.toISOString().slice(0, 16);

  startdt.setHours(startdt.getHours() + 8);
  const enddt = startdt.toISOString().slice(0, 16);

  $('input#date_end').attr('min', enddt);
  $('input#date_end').val(enddt);

  $('input#date_publish').attr('max', publishdtmax);
  // $('input#date_publish').val(string);
}

/**
 * 非公開設定を変更する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_private(e) {
  $('input#date_publish').prop('disabled', $('input#check_private').is(':checked'));
}

async function set_musicnames() {
  $('tr.musicnameitem').off('click', onclick_musicnameitem);
  $('tr.musicnameitem').remove();

  const version = $('select#select_versions').val();
  const musicname_pattern = $('input#text_musicname_search').val();

  const version_all = version == 'ALL';

  let reg = null;
  if(musicname_pattern.length)
    reg = new RegExp(musicname_pattern, 'i');

  for(const musicname in musics) {
    if(!version_all && musics[musicname].version != version)
      continue;
    if(reg !== null && !reg.test(musicname))
      continue;

    const tr = $('<tr>');
    tr.addClass('tableitem musicnameitem');

    const td_musicname = $('<td>').text(musicname);
    td_musicname.addClass('musicname_cell_musicname');
    tr.append(td_musicname);

    const td_version = $('<td>').text(musics[musicname]['version']);
    td_version.addClass('musicname_cell_version');
    tr.append(td_version);

    tr.on('click', onclick_musicnameitem);
    $('#table_musicnames').append(tr);
  }
}

/**
 * 絞り込み対象のバージョンを選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_version(e) {
  set_musicnames();
}

/**
 * 絞り込み対象の曲名の文字列を入力する
 * @param {ce.Event} e イベントハンドラ
 */
function oninput_musicname(e) {
  set_musicnames();
}

/**
 * 曲名を選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_musicnameitem(e) {
  $('tr.musicnameitem.selected').removeClass('selected');
  $(this).addClass('selected');

  $('span#selected_musicname').text($(this).find('td.musicname_cell_musicname').text());
}

/**
 * 投稿テストボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_test(e) {
  const input = get_input();

  if(input === null) return;

  $('button#button_register').prop('disabled', true);
  $('button#button_test').prop('disabled', true);
  $('button#button_close').prop('disabled', true);
  $('span#message').text('投稿テストしています...');

  const ret = JSON.parse(await webui.discordwebhook_testpost(JSON.stringify(input)));

  $('button#button_test').prop('disabled', false);
  $('button#button_close').prop('disabled', false);
  $('span#message').text('');

  if(ret != null) {
    $('textarea#faildtestpostmessage').val(ret);
    $('dialog#dialog_failedtestpost')[0].showModal();
    return;
  }

  $('span#message').text('投稿テストに成功しました。');
  $('button#button_register').prop('disabled', false);
}

/**
 * 登録ボタンを押す
 * 
 * 登録確認ウィンドウを表示する。
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_register(e) {
  $('dialog#dialog_confirmregister')[0].showModal();
}

/**
 * 登録OKボタンを押す
 * 
 * 登録処理を実行する。
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_confirmregister(e) {
  const input = get_input();

  if(input === null) return;

  $(this).closest('dialog')[0].close();

  $('button#button_register').prop('disabled', true);
  $('button#button_test').prop('disabled', true);
  $('button#button_close').prop('disabled', true);

  $('span#message').text('登録しています...');

  const result = await webui.discordwebhook_register(JSON.stringify(input));
  const id = JSON.parse(result);

  $('button#button_close').prop('disabled', false);
  $('span#message').text('');

  if(id === null) {
    $('dialog#dialog_failedregister')[0].showModal();
    return;
  }

  $('span#message').text(`登録完了 ID: ${id}`);

  if($('input#check_downloadid').prop('checked')) {
    const blob = new Blob([id], { text: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const link = $('<a>')
      .attr('href', url)
      .attr('download', `ID-${new Date().toLocaleString()}.txt`)
    link[0].click();
  }
}

/**
 * 閉じるボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_close(e) {
  window.parent.postMessage("discordwebhook_close", "*");
}

/**
 * 検索タブから選択された譜面の情報を表示する
 */
function check_selectscore() {
  const musicname = $('tr.musicnameitem.selected .musicname_cell_musicname').first().text();
  const playmode = $('#select_playmodes option:selected').val();
  const difficulty = $('#select_difficulties option:selected').val();

  if(!Object.keys(musics[musicname][playmode]).includes(difficulty)) {
    $('span#message').text(`${playmode} の ${musicname} に ${difficulty} はありません。`);
    return null;
  }

  $('span#message').text('');

  return [playmode, difficulty, musicname];
}

/**
 * 入力された設定値を取得する。
 * @returns 
 */
function get_input() {
  const checkinput = function(label, text, maxwidth, allowblank) {
    if(text.length == 0) {
      if(allowblank)
        return true;

      $('span#message').text(`${label}を入力してください。`);
      return false;
    }
  
    const canvas = new OffscreenCanvas(1000, 1000);
    const ctx = canvas.getContext('2d');
    ctx.font = $('table').css('font');
    const textwidth = ctx.measureText(text).width;
    if(textwidth > maxwidth) {
      $('span#message').text(`${label}を短くしてください。`);
      return false;
    }
  
    return true;
  }

  const eventname = $('input#text_eventname').val();
  if(!checkinput('イベント名', eventname, 125, false))
    return null;

  const authorname = $('input#text_authorname').val();
  if(!checkinput('開催者名', authorname, 75, false))
    return null;

  const comment = $('input#text_comment').val();
  if(!checkinput('コメント', comment, 324, true))
    return null;

  const siteurl = $('input#text_siteurl').val();
  if(!checkinput('サイトURL', siteurl, 374, true))
    return null;

  if(siteurl.length > 0 && !siteurl.startsWith('https://')) {
    $('span#message').text('サイトURLはセキュアなページURLを入力してください。');
    return null;
  }

  const posturl = $('input#text_posturl').val();
  if(!checkinput('DiscordウェブフックURL', posturl, 800, false))
    return null;

  if(!posturl.startsWith('https://discord.com/api/webhooks/')) {
    $('span#message').text('DiscordウェブフックURLはDiscordの発行するウェブフックURLを入力してください。');
    return null;
  }

  const modeid = $('input[name="mode"]:checked').attr('id');
  if(modeid == null) {
    $('span#message').text('モードを選択してください。');
    return null;
  }

  const mode = modeid.match(/(?<=radio_mode_)(.*)/)[0];
  if(mode == null) {
    $('span#message').text('モードを選択してください。');
    return null;
  }

  const startdtstring = new Date($('input#date_start').val()).toISOString();

  const enddt = new Date($('input#date_end').val());
  const nowdt = new Date();
  const daydifference = (enddt - nowdt) / (1000 * 60 * 60 * 24);
  if(mode == 'battle' && daydifference >= 1) {
    $('span#message').text('バトルイベントは1日以上の期間は設定できません。');
    return null;
  }
  if(daydifference >= 21) {
    $('span#message').text('21日以上の期間は設定できません。');
    return null;
  }

  const enddtstring = enddt.toISOString();

  const private = $('input#check_private').is(':checked');

  var publishdtstring = null;
  if(!private) {
    const startdt = new Date($('input#date_start').val());
    const publishdt = new Date($('input#date_publish').val());
    if(publishdt > startdt) {
      $('span#message').text('開始日時より後の公開開始日時は設定できません。');
      return null;
    }

    publishdtstring = new Date($('input#date_publish').val()).toISOString();
  }

  let targetscore = null;
  if(mode != 'battle') {
    const musicname = $('tr.musicnameitem.selected .musicname_cell_musicname').first().text();
  
    if(musicname.length == 0) {
      $('span#message').text('対象曲を選択してください。');
      return null;
    }
  
    const playmode = $('#select_playmodes option:selected').val();
    const difficulty = $('#select_difficulties option:selected').val();

    if(!Object.keys(musics[musicname][playmode]).includes(difficulty)) {
      $('span#message').text(`${playmode} の ${musicname} に ${difficulty} はありません。`);
      return null;
    }

    targetscore = {
      'playmode': playmode,
      'musicname': musicname,
      'difficulty': difficulty,
    }
  }

  $('span#message').text('');

  return {
    'name': eventname,
    'authorname': authorname,
    'comment': comment,
    'siteurl': siteurl,
    'posturl': posturl,
    'mode': mode,
    'private': private,
    'publishdatetime': publishdtstring,
    'startdatetime': startdtstring,
    'enddatetime': enddtstring,
    'targetscore': targetscore,
  };
}
