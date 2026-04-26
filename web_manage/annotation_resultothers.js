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
  $('input#check_onlyignore').on('change', display_keytable);
  $('select#select_tabfilter').on('change', display_keytable);
  $('input#text_keyfilter').on('input', display_keytable);

  $('input#text_keyfilter').on('click', onclick_filter);
});

/**
 * 初期処理
 * 
 * ロード完了時に実行する。
 */
async function initialize() {
  document.body.addEventListener('contextmenu', e => e.stopPropagation(), true);

  const tabs = JSON.parse(await webui.get_tabs());
  for(const tab of tabs) {
    $('select#select_tab').append($('<option>')
      .val(tab)
      .text(tab)
    );

    $('select#select_tabfilter').append($('<option>')
      .val(tab)
      .text(tab)
    );
  }

  $('select#select_rankbefore').append($('<option>')
    .val('-')
    .text('-')
  );

  for(let rank = 1; rank <= 6; rank++) {
    $('select#select_rankbefore').append($('<option>')
      .val(rank)
      .text(rank)
    );
    
    $('select#select_ranknow').append($('<option>')
      .val(rank)
      .text(rank)
    );
    
    $('select#select_rankposition').append($('<option>')
      .val(rank)
      .text(rank)
    );
  }

  const attributes = JSON.parse(await webui.get_attributes());
  for(const attribute of attributes) {
    $('select#select_radarattribute').append($('<option>')
      .val(attribute)
      .text(attribute)
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
    $('select#select_tab').val(label.tab);
    $('select#select_rankbefore').val(label.rankbefore);
    $('select#select_ranknow').val(label.ranknow);
    $('select#select_rankposition').val(label.rankposition);
    $('select#select_radarattribute').val(label.radarattribute);
    $('input#text_radarchartvalue').val(label.radarchartvalue);
    $('input#text_radarvalue').val(label.radarvalue);

    if(label.radarupdated == null)
      $('select#select_radarupdated').val('不明');
    else
      $('select#select_radarupdated').val(label.radarupdated ? 'あり' : 'なし');

    $('input#check_ignore').prop('checked', Object.hasOwn(label, 'ignore') && label.ignore);
  }
  else {
    $('select#select_tab').val(null);
    $('select#select_rankbefore').val(null);
    $('select#select_ranknow').val(null);
    $('select#select_rankposition').val(null);
    $('select#select_radarattribute').val(null);
    $('input#text_radarchartvalue').val(null);
    $('input#text_radarvalue').val(null);
    $('select#select_radarupdated').val(null);
    $('input#check_ignore').prop('checked', false);
  }

  recognitionresult = JSON.parse(await webui.get_recognitionresult(targetkey));
  if(recognitionresult != null) {
    $('span#text_resulttab').text(recognitionresult.tab);
    $('span#text_resultrankbefore').text(recognitionresult.rankbefore);
    $('span#text_resultranknow').text(recognitionresult.ranknow);
    $('span#text_resultrankposition').text(recognitionresult.rankposition);
    $('span#text_resultradarattribute').text(recognitionresult.radarattribute);
    $('span#text_resultradarchartvalue').text(recognitionresult.radarchartvalue);
    $('span#text_resultradarvalue').text(recognitionresult.radarvalue);

    if(recognitionresult.radarupdated == null)
      $('span#text_resultradarupdated').text('不明')
    else
      $('span#text_resultradarupdated').text(recognitionresult.radarupdated ? 'あり' : 'なし');
  }
  else {
    $('span#text_resulttab').empty();
  }
}

/**
 * ラベルの上書きを実行
 * @param {} e
 */
async function onclick_labeloverwrite(e) {
  const targetkey = $('tr.keyitem.selected .cell_key').first().text();

  const radarupdatedselected = $('select#select_radarupdated').val();
  let radarupdated;
  if(radarupdatedselected == '不明')
    radarupdated = null;
  else
    radarupdated = radarupdatedselected == 'あり' ? true : false;

  values = {
    'tab': $('select#select_tab').val(),
    'rankbefore': $('select#select_rankbefore').val(),
    'ranknow': $('select#select_ranknow').val(),
    'rankposition': $('select#select_rankposition').val(),
    'radarattribute': $('select#select_radarattribute').val(),
    'radarchartvalue': $('input#text_radarchartvalue').val(),
    'radarvalue': $('input#text_radarvalue').val(),
    'radarupdated': radarupdated,
  };

  if($('input#check_ignore').prop('checked'))
    values.ignore = true;

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
  $('select#select_tab').val(recognitionresult.tab);
  $('select#select_rankbefore').val(recognitionresult.rankbefore);
  $('select#select_ranknow').val(recognitionresult.ranknow);
  $('select#select_rankposition').val(recognitionresult.rankposition);
  $('select#select_radarattribute').val(recognitionresult.radarattribute);
  $('input#text_radarchartvalue').val(recognitionresult.radarchartvalue);
  $('input#text_radarvalue').val(recognitionresult.radarvalue);

  if(recognitionresult.radarupdated == null)
    $('select#select_radarupdated').val('不明');
  else
    $('select#select_radarupdated').val(recognitionresult.radarupdated ? 'あり' : 'なし');
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
  const only_ignore = $('input#check_onlyignore').prop('checked');
  const tabfilter = $('select#select_tabfilter').val();
  const keyfilter = $('input#text_keyfilter').val();

  keys = JSON.parse(await webui.get_collectionkeys(JSON.stringify({
    'only_notannotation': only_notannotation,
    'only_ignore': only_ignore,
    'tabfilter': tabfilter.length ? tabfilter : null,
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
