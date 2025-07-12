$(function() {
  webui.setEventCallback((e) => {
    if(e == webui.event.CONNECTED) initialize();
    if(e == webui.event.DISCONNECTED) console.log('disconnect.');
  });

  $('button.dialogclose').on('click', onclick_dialogclose);
  $('button#button_save').on('click', onclick_save);
  $('button#button_joinevent').on('click', onclick_joinevent);
  $('button#button_joineventinputid').on('click', onclick_joineventinputid);
  $('button#button_eventidinputok').on('click', onclick_eventidinputok);
  $('button#button_leaveevent').on('click', onclick_leaveevent);
  $('button#button_close').on('click', onclick_close);
});

/**
 * 初期処理
 * 
 * ロード完了時に実行する。
 */
async function initialize() {
  document.body.addEventListener('contextmenu', e => e.stopPropagation(), true);

  const setting = JSON.parse(await webui.get_setting());
  $('input#text_playername').val(setting.discord_webhook.playername);
  $(`input#radio_filter_${setting.discord_webhook.filter}`).prop('checked', true);

  await get_joineds();
  await get_publics();
}

async function get_publics() {
  $('tr.publicitem').off('click', onclick_publicitem);
  $('tr.publicitem').remove();

  const publics = JSON.parse(await webui.discordwebhook_getpublics());
  Object.keys(publics).forEach(id => {
    const target = publics[id];

    const tr = $('<tr>');
    tr.addClass('tableitem publicitem');

    const td_id = $('<td>').text(id);
    td_id.addClass('publicitem_cell_id');
    tr.append(td_id);

    const td_name = $('<td>').text(target.name);
    td_name.addClass('publicitem_cell_name');
    tr.append(td_name);

    const td_mode = $('<td>');
    if(target.mode == 'battle')
      td_mode.text('バトル');
    if(target.mode == 'score')
      td_mode.text('スコア大会');
    if(target.mode == 'misscount')
      td_mode.text('ミスカウント大会');
    td_mode.addClass('publicitem_cell_mode');
    tr.append(td_mode);

    const localdt = new Date(target.limit);
    const year = localdt.getFullYear();
    const month = localdt.getMonth() + 1;
    const day = localdt.getDate();
    const hour = localdt.getHours();
    const minute = localdt.getMinutes();
    const td_limit = $('<td>').text(`${year}/${month}/${day} ${hour}:${minute}`);
    td_limit.addClass('publicitem_cell_limit');
    tr.append(td_limit);

    const td_targetscore = $('<td>');
    if(target.mode != 'battle') {
      const targetscore = target.targetscore;
      const text = `${targetscore.musicname}[${targetscore.playmode}${targetscore.difficulty[0]}]`;
      td_targetscore.text(text);
    }
    else {
      td_targetscore.text('-');
    }
    td_targetscore.addClass('publicitem_cell_targetscore');
    tr.append(td_targetscore);

    tr.on('click', onclick_publicitem);
    $('#table_publics').append(tr);
  });
}

async function get_joineds() {
  $('tr.joineditem').off('click', onclick_joineditem);
  $('tr.joineditem').remove();

  const joined = JSON.parse(await webui.discordwebhook_getjoineds());
  Object.keys(joined).forEach(id => {
    const target = joined[id];

    const tr = $('<tr>');
    tr.addClass('tableitem joineditem');

    const td_id = $('<td>').text(id);
    td_id.addClass('joineditem_cell_id');
    tr.append(td_id);

    const td_name = $('<td>').text(target.name);
    td_name.addClass('joineditem_cell_name');
    tr.append(td_name);

    const td_mode = $('<td>');
    if(target.mode == 'battle')
      td_mode.text('バトル');
    if(target.mode == 'score')
      td_mode.text('スコア大会');
    if(target.mode == 'misscount')
      td_mode.text('ミスカウント大会');
    td_mode.addClass('joineditem_cell_mode');
    tr.append(td_mode);

    const localdt = new Date(target.limit);
    const year = localdt.getFullYear();
    const month = localdt.getMonth() + 1;
    const day = localdt.getDate();
    const hour = localdt.getHours();
    const minute = localdt.getMinutes();
    const td_limit = $('<td>').text(`${year}/${month}/${day} ${hour}:${minute}`);
    td_limit.addClass('publicitem_cell_limit');
    tr.append(td_limit);

    const td_targetscore = $('<td>');
    if(target.mode != 'battle') {
      const targetscore = target.targetscore;
      const text = `${targetscore.musicname}[${targetscore.playmode}${targetscore.difficulty[0]}]`;
      td_targetscore.text(text);
    }
    else {
      td_targetscore.text('-');
    }
    td_targetscore.addClass('joineditem_cell_targetscore');
    tr.append(td_targetscore);

    const td_mybest = $('<td>').text(target.mybest != null ? target.mybest : '');
    td_mybest.addClass('joineditem_cell_mybest');
    tr.append(td_mybest);

    tr.on('click', onclick_joineditem);
    $('#table_joineds').append(tr);
  });
}

/**
 * Python側からのメッセージ処理

 * @param {*} message メッセージ本文
 */
function communication_message(message, data = null) {
  switch(message) {
    case 'discordwebhook_refresh':
      get_joineds();
      break;
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
 * 設定保存ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_save(e) {
  webui.discordwebhook_savesetting(JSON.stringify({
    playername: $('input#text_playername').val(),
    filter: $('input[name="filter"]:checked').attr('id').match(/[^_]+$/)[0],
  }));

  $('dialog#dialog_savecomplete')[0].showModal();
}

/**
 * 公開されたイベントを選択する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_publicitem(e) {
  $('tr.publicitem.selected').removeClass('selected');
  $(this).addClass('selected');
}

/**
 * 参加中のイベントを選択する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_joineditem(e) {
  $('tr.joineditem.selected').removeClass('selected');
  $(this).addClass('selected');
}

/**
 * 参加ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_joinevent(e) {
  const target = $('tr.publicitem.selected');
  if(!target.length) return;

  const id = target.find('td.publicitem_cell_id').text();
  await webui.discordwebhook_joinevent(id);
}

/**
 * ID指定で参加ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_joineventinputid(e) {
  $('input#text_eventid').val('');
  $('dialog#dialog_idinput')[0].showModal();
}

/**
 * 登録のイベントIDを指定してOKボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_eventidinputok(e) {
  $(this).closest('dialog')[0].close();

  const inputid = $('input#text_eventid').val();
  if(!inputid.length) return;

  const result = JSON.parse(await webui.discordwebhook_joinevent(inputid));
  if(!result) {
    $('dialog#dialog_idnotfound')[0].showModal();
    return;
  }
}

/**
 * 辞退ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_leaveevent(e) {
  const target = $('tr.joineditem.selected');
  if(!target.length) return;

  const id = target.find('td.joineditem_cell_id').text();
  await webui.discordwebhook_leaveevent(id);
}

/**
 * 閉じるボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_close(e) {
  window.parent.postMessage("discordwebhook_close", "*");
}
