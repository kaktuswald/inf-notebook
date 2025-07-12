let musics = null;

$(function() {
  webui.setEventCallback((e) => {
    if(e == webui.event.CONNECTED) initialize();
    if(e == webui.event.DISCONNECTED) console.log('disconnect.');
  });

  const defaultlimit = new Date();
  defaultlimit.setHours(defaultlimit.getHours() + 8);
  defaultlimit.setMinutes(defaultlimit.getMinutes() - defaultlimit.getTimezoneOffset());

  const limitstring = defaultlimit.toISOString().slice(0, 16);
  $('input#date_limit').attr('min', limitstring);
  $('input#date_limit').val(limitstring);

  $('button.dialogclose').on('click', onclick_dialogclose);

  $('input[name="mode"]').on('change', onchange_mode);

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

  const musictable = JSON.parse(await webui.get_musictable());

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

  $('input#text_settingname').val(generate_randomsettingname());
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
    $('select#select_versions').addClass('unusable');
    $('input#text_musicname_search').addClass('unusable');
    $('table#table_musicnames').addClass('unusable');
    $('select#select_playmodes').addClass('unusable');
    $('select#select_difficulties').addClass('unusable');
  }
  else {
    $('input#check_private').prop('disabled', false);
    $('select#select_versions').removeClass('unusable');
    $('input#text_musicname_search').removeClass('unusable');
    $('table#table_musicnames').removeClass('unusable');
    $('select#select_playmodes').removeClass('unusable');
    $('select#select_difficulties').removeClass('unusable');
  }
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
 * ランダムな設定名を生成する
 * @param {int} length ランダム文字列の長さ
 * @returns 生成された文字列
 */
function generate_randomsettingname(length = 8) {
  const characters = Array.from({length}, () => 
    String.fromCharCode(65 + Math.floor(Math.random() * 26))
  );

  return `Event-${characters.join('')}`;
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
  const settingname = $('input#text_settingname').val();

  if(settingname.length == 0) {
    $('span#message').text('名称を入力してください。');
    return null;
  }

  if(settingname.length > 256) {
    $('span#message').text('名称を短くしてください。');
    return null;
  }

  const private = $('input#check_private').is(':checked');

  const url = $('input#text_url').val();

  if(url.length == 0) {
    $('span#message').text('URLを入力してください。');
    return null;
  }

  if(url.length > 256) {
    $('span#message').text('URLを短くしてください。');
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

  const limit = new Date($('input#date_limit').val());
  const now = new Date();
  const daydifference = (limit - now) / (1000 * 60 * 60 * 24);
  if(mode == 'battle' && daydifference >= 1) {
    $('span#message').text('バトルイベントは1日以上の期間は設定できません。');
    return null;
  }
  if(daydifference >= 21) {
    $('span#message').text('21日以上の期間は設定できません。');
    return null;
  }

  const limitstring = limit.toISOString();

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
    'name': settingname,
    'private': private,
    'url': url,
    'mode': mode,
    'limit': limitstring,
    'targetscore': targetscore,
  };
}
