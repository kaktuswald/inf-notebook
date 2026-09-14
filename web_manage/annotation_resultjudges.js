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
    $('input#text_pgreat').val(label.pgreat);
    $('input#text_great').val(label.great);
    $('input#text_good').val(label.good);
    $('input#text_bad').val(label.bad);
    $('input#text_poor').val(label.poor);
    $('input#check_ignore').prop('checked', label.ignore == true);
  }
  else {
    $('input#text_pgreat').val(null);
    $('input#text_great').val(null);
    $('input#text_good').val(null);
    $('input#text_bad').val(null);
    $('input#text_poor').val(null);
    $('input#check_ignore').prop('checked', false);
  }

  recognitionresult = JSON.parse(await webui.get_recognitionresult(targetkey));
  if(recognitionresult !== null) {
    $('span#text_pgreat').text(recognitionresult.pgreat);
    $('span#text_great').text(recognitionresult.great);
    $('span#text_good').text(recognitionresult.good);
    $('span#text_bad').text(recognitionresult.bad);
    $('span#text_poor').text(recognitionresult.poor);
  }
  else {
    $('span#text_pgreat').empty();
    $('span#text_great').empty();
    $('span#text_good').empty();
    $('span#text_bad').empty();
    $('span#text_poor').empty();
  }
}

/**
 * ラベルの上書きを実行
 * @param {} e
 */
async function onclick_labeloverwrite(e) {
  const targetkey = $('tr.keyitem.selected .cell_key').first().text();

  values = {
    'pgreat': $('input#text_pgreat').val(),
    'great': $('input#text_great').val(),
    'good': $('input#text_good').val(),
    'bad': $('input#text_bad').val(),
    'poor': $('input#text_poor').val(),
  }

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
  $('input#text_pgreat').val(recognitionresult.pgreat);
  $('input#text_great').val(recognitionresult.great);
  $('input#text_good').val(recognitionresult.good);
  $('input#text_bad').val(recognitionresult.bad);
  $('input#text_poor').val(recognitionresult.poor);
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
  const keyfilter = $('input#text_keyfilter').val();

  keys = JSON.parse(await webui.get_collectionkeys(JSON.stringify({
    'only_notannotation': only_notannotation,
    'only_ignore': only_ignore,
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
