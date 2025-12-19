$(function() {
  webui.setEventCallback((e) => {
    if(e == webui.event.CONNECTED) initialize();
    if(e == webui.event.DISCONNECTED) console.log('disconnect.');
  });

  $('button.dialogclose').on('click', onclick_dialogclose);

  $('button#button_delete').on('click', onclick_delete);
  $('button#button_confirmdelete').on('click', onclick_confirmdelete);
  $('button#button_close').on('click', onclick_close);
});

/**
 * 初期処理
 */
async function initialize() {
  document.body.addEventListener('contextmenu', e => e.stopPropagation(), true);

  $('span#message').text('イベントリスト読込中...');

  const eventresult = JSON.parse(await webui.discordwebhook_downloadevents());
  if(!eventresult) {
    $('span#message').text('読込に失敗しました');
    return;
  }

  $('span#message').text('読込完了');
}

/**
 * ダイアログを閉じるボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_dialogclose(e) {
  $(this).closest('dialog')[0].close();
}

/**
 * 削除ボタンを押す
 * 
 * 削除確認ウィンドウを表示する。
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_delete(e) {
  const eventid = $('input#text_eventid').val();
  if(eventid.length == 0) {
    $('span#message').text('イベントIDを入力してください。');
    return null;
  }

  const deletecode = $('input#text_deletecode').val();
  if(deletecode.length == 0) {
    $('span#message').text('削除コードを入力してください。');
    return null;
  }

  $('dialog#dialog_confirmdelete')[0].showModal();
}

/**
 * 削除OKボタンを押す
 * 
 * 削除処理を実行する。
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_confirmdelete(e) {
  const eventid = $('input#text_eventid').val();
  const deletecode = $('input#text_deletecode').val();

  $(this).closest('dialog')[0].close();

  $('button#button_delete').prop('disabled', true);
  $('button#button_close').prop('disabled', true);

  $('span#message').text('削除しています...');

  const result = JSON.parse(await webui.discordwebhook_delete(eventid, deletecode));

  if(!result)
    $('span#message').text('削除完了');
  else
    $('span#message').text(result);

  $('button#button_delete').prop('disabled', false);
  $('button#button_close').prop('disabled', false);
}

/**
 * 閉じるボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_close(e) {
  window.parent.postMessage("discordwebhook_close", "*");
}
