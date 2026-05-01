recognitionresult = null;

$(function() {
  webui.setEventCallback((e) => {
    if(e == webui.event.CONNECTED) initialize();
    if(e == webui.event.DISCONNECTED) console.log('disconnect.');
  });

  $('button#button_labeloverwrite').on('click', onclick_labeloverwrite);
  $('button#button_citationrecog').on('click', onclick_citationrecog);
  $('button#button_delete').on('click', onclick_delete);

  $('input#check_onlynotannotation').on('change', display_keytable);
  $('input#check_onlyundefinedsongname').on('change', display_keytable);
  $('input#check_onlyundefinedversion').on('change', display_keytable);
  $('input#check_onlyignore').on('change', display_keytable);
  $('input#text_songnamefilter').on('input', display_keytable);
  $('input#text_keyfilter').on('input', display_keytable);

  $('input#text_songnamefilter').on('click', onclick_filter);
  $('input#text_keyfilter').on('click', onclick_filter);
});

/**
 * 初期処理
 * 
 * ロード完了時に実行する。
 */
async function initialize() {
  document.body.addEventListener('contextmenu', e => e.stopPropagation(), true);

  const playmodes = JSON.parse(await webui.get_playmodes());
  for(const playmode of playmodes) {
    $('select#select_playmode').append($('<option>')
      .val(playmode)
      .text(playmode)
    );
  }

  const versions = JSON.parse(await webui.get_versions());
  const flatted_versions = versions.flatMap(item => item.split('&'));
  for(const version of flatted_versions) {
    $('select#select_version').append($('<option>')
      .val(version)
      .text(version)
    );
  }

  const difficulties = JSON.parse(await webui.get_difficulties());
  for(const difficulty of difficulties) {
    $('select#select_difficulty').append($('<option>')
      .val(difficulty)
      .text(difficulty)
    );
  }

  const cleartypes = JSON.parse(await webui.get_cleartypes());
  for(const cleartype of cleartypes) {
    $('select#select_cleartype').append($('<option>')
      .val(cleartype)
      .text(cleartype)
    );
  }

  const djlevels = JSON.parse(await webui.get_djlevels());
  for(const djlevel of djlevels) {
    $('select#select_djlevel').append($('<option>')
      .val(djlevel)
      .text(djlevel)
    );
  }

  const levels = JSON.parse(await webui.get_levels());
  for(const level of levels) {
    $('select#select_levelbeginner').append($('<option>')
      .val(level)
      .text(level)
    );

    $('select#select_levelnormal').append($('<option>')
      .val(level)
      .text(level)
    );
    $('select#select_levelhyper').append($('<option>')
      .val(level)
      .text(level)
    );
    $('select#select_levelanother').append($('<option>')
      .val(level)
      .text(level)
    );
    $('select#select_levelleggendaria').append($('<option>')
      .val(level)
      .text(level)
    );
  }

  display_keytable();
}

/**
 * キーを選択
 * @param {} e
 */
async function onclick_keyitem(e) {
  $('tr.keyitem.selected').removeClass('selected');
  $(this).addClass('selected');

  const targetkey = $('tr.keyitem.selected .cell_key').first().text();

  const image = JSON.parse(await webui.get_images(targetkey));
  if(image !== null)
    $('img#image').attr('src', `data:image/png;base64,${image}`);
  else
    $('img#image').attr('src', null);

  const label = JSON.parse(await webui.get_labels(targetkey));
  if(label !== null) {
    $('select#select_playmode').val(label.playmode);
    $('select#select_version').val(label.version);
    $('select#select_songnametype').val(label.songnametype);
    $('input#text_songname').val(label.songname);
    $('select#select_difficulty').val(label.difficulty);
    $('input#check_nohasscoredata').prop('checked', label.nohasscoredata == true);
    $('select#select_cleartype').val(label.cleartype);
    $('select#select_djlevel').val(label.djlevel);
    $('input#text_score').val(label.score);
    $('input#text_misscount').val(label.misscount);
    $('select#select_levelbeginner').val(label.level_beginner);
    $('select#select_levelnormal').val(label.level_normal);
    $('select#select_levelhyper').val(label.level_hyper);
    $('select#select_levelanother').val(label.level_another);
    $('select#select_levelleggendaria').val(label.level_leggendaria);
    $('input#check_ignore').prop('checked', label.ignore == true);
    $('input#check_after260312').prop('checked', label.after260312 == true);
  }
  else {
    $('select#select_playmode').val(null);
    $('select#select_version').val(null);
    $('select#select_songnametype').val(null);
    $('input#text_songname').val(null);
    $('select#select_difficulty').val(null);
    $('input#check_nohasscoredata').prop('checked', false);
    $('select#select_cleartype').val(null);
    $('select#select_djlevel').val(null);
    $('input#text_score').val(null);
    $('input#text_misscount').val(null);
    $('select#select_levelbeginner').val(null);
    $('select#select_levelnormal').val(null);
    $('select#select_levelhyper').val(null);
    $('select#select_levelanother').val(null);
    $('select#select_levelleggendaria').val(null);
    $('input#check_ignore').prop('checked', false);
    $('input#check_after260312').prop('checked', true);
  }

  recognitionresult = JSON.parse(await webui.get_recognitionresult(targetkey));
  if(recognitionresult !== null) {
    $('span#text_resultlevelbeginner').text(recognitionresult.levels.BEGINNER ? recognitionresult.levels.BEGINNER : '');
    $('span#text_resultlevelnormal').text(recognitionresult.levels.NORMAL ? recognitionresult.levels.NORMAL : '');
    $('span#text_resultlevelhyper').text(recognitionresult.levels.HYPER ? recognitionresult.levels.HYPER : '');
    $('span#text_resultlevelanother').text(recognitionresult.levels.ANOTHER ? recognitionresult.levels.ANOTHER : '');
    $('span#text_resultlevelleggendaria').text(recognitionresult.levels.LEGGENDARIA ? recognitionresult.levels.LEGGENDARIA : '');

    $('span#text_resultplaymode').text(recognitionresult.playmode);
    $('span#text_resultversion').text(recognitionresult.version);
    $('span#text_resultsongname').text(recognitionresult.songname);
    $('span#text_resultdifficulty').text(recognitionresult.difficulty);
    $('span#text_hasscoredata').text(recognitionresult.hasscoredata ? 'あり' : 'なし');
    $('span#text_resultcleartype').text(recognitionresult.cleartype);
    $('span#text_resultdjlevel').text(recognitionresult.djlevel);
    $('span#text_resultscore').text(recognitionresult.score);
    $('span#text_resultmisscount').text(recognitionresult.misscount);
  }
  else {
    $('span#text_resultlevelbeginner').empty();
    $('span#text_resultlevelnormal').empty();
    $('span#text_resultlevelhyper').empty();
    $('span#text_resultlevelanother').empty();
    $('span#text_resultlevelleggendaria').empty();

    $('span#text_resultplaymode').empty();
    $('span#text_resultversion').empty();
    $('span#text_resultsongname').empty();
    $('span#text_resultdifficulty').empty();
    $('span#text_hasscoredata').empty();
    $('span#text_resultcleartype').empty();
    $('span#text_resultdjlevel').empty();
    $('span#text_resultscore').empty();
    $('span#text_resultmisscount').empty();
  }
}

/**
 * ラベルの上書きを実行
 * @param {} e
 */
async function onclick_labeloverwrite(e) {
  const targetkey = $('tr.keyitem.selected .cell_key').first().text();

  values = {
    'playmode': $('select#select_playmode').val(),
    'difficulty': $('select#select_difficulty').val(),
    'level_beginner': $('select#select_levelbeginner').val(),
    'level_normal': $('select#select_levelnormal').val(),
    'level_hyper': $('select#select_levelhyper').val(),
    'level_another': $('select#select_levelanother').val(),
    'level_leggendaria': $('select#select_levelleggendaria').val(),
    'version': $('select#select_version').val(),
    'songnametype': $('select#select_songnametype').val(),
    'songname': $('input#text_songname').val(),
    'nohasscoredata': $('input#check_nohasscoredata').prop('checked'),
    'cleartype': $('select#select_cleartype').val(),
    'djlevel': $('select#select_djlevel').val(),
    'score': $('input#text_score').val(),
    'misscount': $('input#text_misscount').val(),
  }

  if($('input#check_ignore').prop('checked'))
    values.ignore = true;

  if($('input#check_after260312').prop('checked'))
    values.after260312 = true;

  await webui.set_labels(
    targetkey,
    JSON.stringify(values),
  );
}

/**
 * 認識結果を引用
 * @param {} e
 */
async function onclick_citationrecog(e) {
  $('select#select_playmode').val(recognitionresult.playmode);
  $('select#select_version').val(recognitionresult.version);

  if(recognitionresult.version != 'INFINITAS' && recognitionresult.difficulty != 'LEGGENDARIA')
    $('select#select_songnametype').val('ARCADE')
  if(recognitionresult.version == 'INFINITAS')
    $('select#select_songnametype').val('INFINITAS')
  if(recognitionresult.difficulty == 'LEGGENDARIA')
    $('select#select_songnametype').val('LEGGENDARIA')

  $('input#text_songname').val(recognitionresult.songname);
  $('select#select_difficulty').val(recognitionresult.difficulty);
  $('input#check_nohasscoredata').prop('checked', recognitionresult.hasscoredata != true);
  $('select#select_cleartype').val(recognitionresult.cleartype);
  $('select#select_djlevel').val(recognitionresult.djlevel);
  $('input#text_score').val(recognitionresult.score);
  $('input#text_misscount').val(recognitionresult.misscount);
  $('select#select_levelbeginner').val(recognitionresult.levels.BEGINNER);
  $('select#select_levelnormal').val(recognitionresult.levels.NORMAL);
  $('select#select_levelhyper').val(recognitionresult.levels.HYPER);
  $('select#select_levelanother').val(recognitionresult.levels.ANOTHER);
  $('select#select_levelleggendaria').val(recognitionresult.levels.LEGGENDARIA);

  $('input#text_songname')
    .focus()
    .select();
}

/**
 * 画像とラベルの削除
 * @param {} e
 */
async function onclick_delete(e) {
  const targetkey = $('tr.keyitem.selected .cell_key').first().text();

  await webui.delete_keyandlabel(targetkey);
  
  display_keytable();
}

/**
 * フィルタを選択
 * @param {} e
 */
async function onclick_filter(e) {
  $(this).select();
}

/**
 * キー一覧を表示する
 * @param {} e
 */
async function display_keytable() {
  $('tr.keyitem').off('click', onclick_keyitem);
  $('tr.keyitem').remove();

  const only_notannotation = $('input#check_onlynotannotation').prop('checked');
  const only_undefinedsongname = $('input#check_onlyundefinedsongname').prop('checked');
  const only_undefinedversion = $('input#check_onlyundefinedversion').prop('checked');
  const only_ignore = $('input#check_onlyignore').prop('checked');
  const songnamefilter = $('input#text_songnamefilter').val();
  const keyfilter = $('input#text_keyfilter').val();

  keys = JSON.parse(await webui.get_collectionkeys(JSON.stringify({
    'only_notannotation': only_notannotation,
    'only_undefinedsongname': only_undefinedsongname,
    'only_undefinedversion': only_undefinedversion,
    'only_ignore': only_ignore,
    'songnamefilter': songnamefilter.length ? songnamefilter : null,
    'keyfilter': keyfilter.length ? keyfilter : null,
  })));
  for(const key of keys) {
    const tr = $('<tr>')
      .addClass('tableitem keyitem');

    const td = $('<td>').text(key)
      .addClass('cell_key');
    
    tr.append(td);
    
    tr.on('click', onclick_keyitem);
    $('table#table_keys').append(tr);
  }
}
