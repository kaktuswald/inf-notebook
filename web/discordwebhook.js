$(function() {
  webui.setEventCallback((e) => {
    if(e == webui.event.CONNECTED) initialize();
    if(e == webui.event.DISCONNECTED) console.log('disconnect.');
  });

  $('button.dialogclose').on('click', onclick_dialogclose);
  $('button#button_playernameinputok').on('click', onclick_playernameinputok);
  $('button#button_save').on('click', onclick_save);
  $('button#button_opensitepublic').on('click', onclick_opensitepublic);
  $('button#button_joinevent').on('click', onclick_joinevent);
  $('button#button_joineventinputid').on('click', onclick_joineventinputid);
  $('button#button_eventidinputok').on('click', onclick_eventidinputok);
  $('button#button_opensitejoined').on('click', onclick_opensitejoined);
  $('button#button_leaveevent').on('click', onclick_leaveevent);
  $('button#button_confirmleaveevent').on('click', onclick_confirmleaveevent);
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

  if(['', 'NO NAME'].includes(setting.discord_webhook.playername)) {
    $('input#text_dialogplayername').val(setting.discord_webhook.playername);
    $('dialog#dialog_playernameinput')[0].showModal();
  }

  await get_joineds();
  await get_publics();
}

async function get_publics() {
  $('tr.publicitem').off('click', onclick_publicitem);
  $('tr.publicitem').remove();

  $('span#text_geteventsstatus').text('イベントリスト読込中...');

  const eventresult = JSON.parse(await webui.discordwebhook_downloadevents());
  if(!eventresult) {
    $('span#text_geteventsstatus').text('読込に失敗しました');
    return;
  }

  const publics = JSON.parse(await webui.discordwebhook_getpublishedpublics());

  $('span#text_geteventsstatus')
    .text('')
    .removeClass('message');
  
  Object.keys(publics).forEach(id => {
    const target = publics[id];

    const tr = $('<tr>');
    tr.addClass('tableitem publicitem');
    tr.attr('title', generate_eventtips(target));

    const td_id = $('<td>').text(id);
    td_id.addClass('publicitem_cell_id');
    tr.append(td_id);

    const td_name = $('<td>').text(target.name);
    td_name.addClass('publicitem_cell_name');
    tr.append(td_name);

    const td_siteurl = $('<td>').text(target.siteurl);
    td_siteurl.addClass('publicitem_cell_siteurl');
    tr.append(td_siteurl);

    const td_mode = $('<td>');
    if(target.mode == DiscordwebhookModes.BATTLE)
      td_mode.text('バトル');
    if(target.mode == DiscordwebhookModes.SCORE)
      td_mode.text('スコア大会');
    if(target.mode == DiscordwebhookModes.MISSCOUNT)
      td_mode.text('ミスカウント大会');
    td_mode.addClass('publicitem_cell_mode');
    tr.append(td_mode);

    const td_startdt = $('<td>').text(convert_datetime(target.startdatetime));
    td_startdt.addClass('publicitem_cell_startdatetime');
    tr.append(td_startdt);

    const td_enddt = $('<td>').text(convert_datetime(target.enddatetime));
    td_enddt.addClass('publicitem_cell_enddatetime');
    tr.append(td_enddt);

    const td_status = $('<td>').text(target.status);
    td_status.addClass('publicitem_cell_status');
    tr.append(td_status);

    const td_statuslabel = $('<td>');
    switch(target.status) {
      case DiscordwebhookStatuses.UPCOMING:
        td_statuslabel.text('予告');
        break;
      case DiscordwebhookStatuses.ONGOING:
        td_statuslabel.text('開催中');
        break;
      case DiscordwebhookStatuses.ENDED:
        td_statuslabel.text('終了');
        break;
    }
    td_statuslabel.addClass('publicitem_cell_statuslabel');
    tr.append(td_statuslabel);

    const td_targetscore = $('<td>');
    if(target.mode != DiscordwebhookModes.BATTLE) {
      const targetscore = target.targetscore;
      const text = `[${targetscore.playmode}${targetscore.difficulty[0]}]${targetscore.musicname}`;
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
    tr.attr('title', generate_eventtips(target));

    const td_id = $('<td>').text(id);
    td_id.addClass('joineditem_cell_id');
    tr.append(td_id);

    const td_name = $('<td>').text(target.name);
    td_name.addClass('joineditem_cell_name');
    tr.append(td_name);

    const td_siteurl = $('<td>').text(target.siteurl);
    td_siteurl.addClass('joineditem_cell_siteurl');
    tr.append(td_siteurl);

    const td_mode = $('<td>');
    if(target.mode == DiscordwebhookModes.BATTLE)
      td_mode.text('バトル');
    if(target.mode == DiscordwebhookModes.SCORE)
      td_mode.text('スコア大会');
    if(target.mode == DiscordwebhookModes.MISSCOUNT)
      td_mode.text('ミスカウント大会');
    td_mode.addClass('joineditem_cell_mode');
    tr.append(td_mode);

    const td_startdt = $('<td>').text(convert_datetime(target.startdatetime));
    td_startdt.addClass('joineditem_cell_startdatetime');
    tr.append(td_startdt);

    const td_enddt = $('<td>').text(convert_datetime(target.enddatetime));
    td_enddt.addClass('joineditem_cell_enddatetime');
    tr.append(td_enddt);

    const td_status = $('<td>').text(target.status);
    td_status.addClass('joineditem_cell_status');
    tr.append(td_status);

    const td_statuslabel = $('<td>');
    switch(target.status) {
      case DiscordwebhookStatuses.UPCOMING:
        td_statuslabel.text('予告');
        break;
      case DiscordwebhookStatuses.ONGOING:
        td_statuslabel.text('開催中');
        break;
      case DiscordwebhookStatuses.ENDED:
        td_statuslabel.text('終了');
        break;
    }
    td_statuslabel.addClass('joineditem_cell_statuslabel');
    tr.append(td_statuslabel);

    const td_targetscore = $('<td>');
    if(target.mode != DiscordwebhookModes.BATTLE) {
      const targetscore = target.targetscore;
      const text = `[${targetscore.playmode}${targetscore.difficulty[0]}]${targetscore.musicname}`;
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
 * 
 * @param {*} eventdata 
 * @returns tipsの文字列
 */
function generate_eventtips(eventdata) {
  const tips = [
    `開催者: ${eventdata.authorname}`,
    `サイトURL: ${eventdata.siteurl}`,
    '',
    eventdata.comment,
  ];

  return tips.join('\n');
}

/**
 * ISO 8601式日時文字列から月日時分文字列に変換
 * 
 * @param {str} datetime ISO 8601式の文字列
 * @returns 月日時分の文字列
 */
function convert_datetime(datetime) {
  const localdt = new Date(datetime);

  const month = (localdt.getMonth() + 1).toString().padStart(2, '0');
  const day = localdt.getDate().toString().padStart(2, '0');
  const hour = localdt.getHours().toString().padStart(2, '0');
  const minute = localdt.getMinutes().toString().padStart(2, '0');

  return `${month}/${day} ${hour}:${minute}`;
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
 * ダイアログのプレイヤー名保存ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_playernameinputok(e) {
  webui.discordwebhook_savesetting(JSON.stringify({
    playername: $('input#text_dialogplayername').val(),
  }));

  $('input#text_playername').val($('input#text_dialogplayername').val());
  $(this).closest('dialog')[0].close();
}

/**
 * 設定保存ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_save(e) {
  webui.discordwebhook_savesetting(JSON.stringify({
    playername: $('input#text_playername').val(),
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
 * 公開中のイベントのサイトを開くボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_opensitepublic(e) {
  const target = $('tr.publicitem.selected');
  if(!target.length) return;

  const url = target.find('td.publicitem_cell_siteurl').text();
  if(url && url.startsWith('http'))
    webui.discordwebhook_openurl(url);
}

/**
 * 参加ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_joinevent(e) {
  const target = $('tr.publicitem.selected');
  if(!target.length) return;

  const a = target.find('td.publicitem_cell_status');
  const b = target.find('td.publicitem_cell_status').text();
  if(target.find('td.publicitem_cell_status').text() == DiscordwebhookStatuses.ENDED) {
    $('dialog#dialog_selecteventended')[0].showModal();
    return;
  }

  const id = target.find('td.publicitem_cell_id').text();
  const result = JSON.parse(await webui.discordwebhook_joinevent(id));
  if(!result)
    $('dialog#dialog_joinerror')[0].showModal();
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
  if(!result)
    $('dialog#dialog_joinerror')[0].showModal();
}

/**
 * 参加中のイベントのサイトを開くボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_opensitejoined(e) {
  const target = $('tr.joineditem.selected');
  if(!target.length) return;

  const url = target.find('td.joineditem_cell_siteurl').text();
  if(url && url.startsWith('http'))
    webui.discordwebhook_openurl(url);
}

/**
 * 辞退ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_leaveevent(e) {
  const target = $('tr.joineditem.selected');
  if(!target.length) return;

  if(target.find('td.joineditem_cell_status').text() == DiscordwebhookStatuses.ENDED) {
    $('dialog#dialog_selecteventended')[0].showModal();
    return;
  }

  $('dialog#dialog_confirmleaveevent')[0].showModal();
}

/**
 * 辞退OKボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_confirmleaveevent(e) {
  $(this).closest('dialog')[0].close();

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
