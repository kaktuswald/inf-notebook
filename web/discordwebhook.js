let musics = null;

$(function() {
  webui.setEventCallback((e) => {
    if(e == webui.event.CONNECTED) initialize();
    if(e == webui.event.DISCONNECTED) console.log('disconnect.');
  });

  $('input[name="mode"]').on('change', onchange_mode);

  $('select#select_versions').on('change', onchange_version);
  $('input#text_musicname_search').on('input', oninput_musicname);

  $('button#button_ok').on('click', onclick_ok);
  $('button#button_cancel').on('click', onclick_cancel);
});

function a(id) {
  $('input#text_settingname').val(id);
}

/**
 * 初期処理
 * 
 * ロード完了時に実行する。Python側から選択肢のリストを取得する。
 */
async function initialize() {
  const musictable = JSON.parse(await webui.get_musictable());
  musics = musictable['musics'];

  for(const version in musictable['versions']) {
    $('#select_versions').append($('<option>')
        .val(version)
        .text(version)
    );
  }

  for(const musicname in musictable['musics']) {
    const tr = $('<tr>');
    tr.addClass('tableitem musicnameitem');

    const td_musicname = $('<td>').text(musicname);
    td_musicname.addClass('musicname_cell_musicname');
    tr.append(td_musicname);

    const td_version = $('<td>').text(musictable['musics'][musicname]['version']);
    td_version.addClass('musicname_cell_version');
    tr.append(td_version);

    tr.on('click', onclick_musicnameitem);
    $('#table_musicnames').append(tr);
  }

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

  const params = new URLSearchParams(window.location.search);
  if(!params.has('id')) return;

  const id = params.get('id')

  const values = JSON.parse(await webui.discordwebhook_getsetting(id));

  if(values == null) {
    $('input#text_settingname').val(generate_randomsettingname());
    return;
  }

  $('input#text_settingname').val(values['name']);
  $('input#text_url').val(values['url']);
  $(`input#radio_mode_${values['mode']}`).prop('checked', true);
  $(`input#radio_filter_${values['filter']}`).prop('checked', true);

  if(values['targetscore'] == null) return;

  $('select#select_versions').removeClass('unusable');
  $('text#text_musicname_search').removeClass('unusable');
  $('table#table_musicnames').removeClass('unusable');
  $('select#select_playmodes').removeClass('unusable');
  $('select#select_difficulties').removeClass('unusable');

  $('tr.musicnameitem').each(function() {
    if($(this).children('td.musicname_cell_musicname').text() == values['targetscore'] ['musicname'])
      $(this).addClass('selected');
  });

  $('span#selected_musicname').text(values['targetscore']['musicname']);

  $('select#select_playmodes').val(values['targetscore'] ['playmode']);
  $('select#select_difficulties').val(values['targetscore'] ['difficulty']);
}

/**
 * モードを選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_mode(e) {
  const selected_mode = $('input[name="mode"]:checked').attr('id');
  const mode = selected_mode.match(/(?<=radio_mode_)(.*)/)[0];

  if(mode == "battle") {
    $('select#select_versions').addClass('unusable');
    $('input#text_musicname_search').addClass('unusable');
    $('table#table_musicnames').addClass('unusable');
    $('select#select_playmodes').addClass('unusable');
    $('select#select_difficulties').addClass('unusable');
  }
  else {
    $('select#select_versions').removeClass('unusable');
    $('input#text_musicname_search').removeClass('unusable');
    $('table#table_musicnames').removeClass('unusable');
    $('select#select_playmodes').removeClass('unusable');
    $('select#select_difficulties').removeClass('unusable');
  }
}

/**
 * 絞り込み対象のバージョンを選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_version(e) {
  const version = e.target.value;
  const musicname_pattern = $('input#text_musicname_search').val();

  musicname_search(version, musicname_pattern);
}

/**
 * 絞り込み対象の曲名の文字列を入力する
 * @param {ce.Event} e イベントハンドラ
 */
function oninput_musicname(e) {
  const version = $('select#select_versions').val();
  const musicname_pattern = e.target.value;

  musicname_search(version, musicname_pattern);
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
 * OKボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_ok(e) {
  const settingname = $('input#text_settingname').val();

  if(settingname.length == 0) {
    $('span#message').text('名称を入力してください。');
    return;
  }

  if(settingname.length > 256) {
    $('span#message').text('名称を短くしてください。');
    return;
  }

  const url = $('input#text_url').val();

  if(url.length == 0) {
    $('span#message').text('URLを入力してください。');
    return;
  }

  if(url.length > 256) {
    $('span#message').text('URLを短くしてください。');
    return;
  }

  const modeid = $('input[name="mode"]:checked').attr('id');
  const mode = modeid.match(/(?<=radio_mode_)(.*)/)[0];

  if(mode == null) {
    $('span#message').text('モードを選択してください。');
    return;
  }

  const filterid = $('input[name="filter"]:checked').attr('id');
  const filter = filterid.match(/(?<=radio_filter_)(.*)/)[0];

  if(filter == null) {
    $('span#message').text('フィルター設定を選択してください。');
    return;
  }

  let targetscore = null;
  if(mode != 'battle') {
    const musicname = $('tr.musicnameitem.selected .musicname_cell_musicname').first().text();
  
    if(musicname.length == 0) {
      $('span#message').text('対象曲を選択してください。');
      return;
    }
  
    const playmode = $('#select_playmodes option:selected').val();
    const difficulty = $('#select_difficulties option:selected').val();

    if(!Object.keys(musics[musicname][playmode]).includes(difficulty)) {
      $('span#message').text(`${playmode} の ${musicname} に ${difficulty} はありません。`);
      return;
    }

    targetscore = {
      'musicname': musicname,
      'playmode': playmode,
      'difficulty': difficulty,
    }
  }

  $('span#message').text('');

  await webui.discordwebhook_updatesetting(JSON.stringify({
    'name': settingname,
    'url': url,
    'mode': mode,
    'filter': filter,
    'targetscore': targetscore,
  }));

  window.parent.postMessage("discordwebhook_close", "*");
}

/**
 * キャンセルボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_cancel(e) {
  window.parent.postMessage("discordwebhook_close", "*");
}

/**
 * ランダムな設定名を生成する
 * @param {int} length ランダム文字列の長さ
 * @returns 生成された文字列
 */
function generate_randomsettingname(length = 4) {
  const characters = Array.from({length}, () => 
    String.fromCharCode(65 + Math.floor(Math.random() * 26))
  );

  return `Server-${characters.join('')}`;
}

/**
 * 入力された条件をもとに一致する曲名だけを表示する
 * @param {str} version バージョン名。ALLの場合は全てのバージョンが対象
 * @param {str} musicname_pattern 曲名の条件(部分一致)。なしの場合は全ての曲名が対象
 */
function musicname_search(version, musicname_pattern) {
  const version_all = version == 'ALL';
  const musicname_all = musicname_pattern.length == 0;

  let reg = null;
  if(!musicname_all)
    reg = new RegExp(musicname_pattern, 'i');

  $('table#table_musicnames tr.musicnameitem').each(function() {
    const version_condition = version_all || $(this).children('td.musicname_cell_version').text() == version;
    const musicname_condition = musicname_all || reg.test($(this).children('td.musicname_cell_musicname').text());

    if(version_condition && musicname_condition)
      $(this).removeClass('hidden');
    else
      $(this).addClass('hidden');
  });
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
