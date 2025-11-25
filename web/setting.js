let setting = null;

$(function() {
  webui.setEventCallback((e) => {
    if(e == webui.event.CONNECTED) initialize();
    if(e == webui.event.DISCONNECTED) console.log('disconnect.');
  });

  $('button.select_tabpage').on('click', onclick_tab);

  $('#check_filter_overlay').on('change', onchange_check_filteroverlay);
  $('button.button_browse_file').on('click', onclick_browse_file);
  $('button.button_browse_directory').on('click', onclick_browse_directory);
  
  $('button#button_save').on('click', onclick_button_save);
  $('button#button_close').on('click', onclick_button_close);

  switch_displaytab('blank');
});

/**
 * 初期処理
 * 
 * ロード完了時に実行する。
 */
async function initialize() {
  document.body.addEventListener('contextmenu', e => e.stopPropagation(), true);

  const setting = JSON.parse(await webui.get_setting());
  globalThis.setting = setting;
  
  $('#check_newrecord_only').prop('checked', setting['newrecord_only']);
  $('#check_play_sound').prop('checked', setting['play_sound']);
  $('#check_autosave').prop('checked', setting['autosave']);
  $('#check_autosave_filtered').prop('checked', setting['autosave_filtered']);
  $('#check_filter_compact').prop('checked', setting['filter_compact']);
  $('#check_filter_overlay').prop('checked', setting['filter_overlay']['use']);
  ['rival', 'loveletter', 'rivalname'].forEach(key => {
    $(`#text_overlayimage${key}_path`).val(setting['filter_overlay'][key]['imagefilepath']);
    $(`#text_overlayimage${key}_offsetx`).val(setting['filter_overlay'][key]['offset'][0]);
    $(`#text_overlayimage${key}_offsety`).val(setting['filter_overlay'][key]['offset'][1]);
    $(`#text_overlayimage${key}_scalefactor`).val(setting['filter_overlay'][key]['scalefactor']);
  });

  $('#check_savefilemusicname_right').prop('checked', setting['savefilemusicname_right']);

  $('#text_hotkey_active_screenshot').val(setting['hotkeys']['active_screenshot']);
  $('#text_hotkey_select_summary').val(setting['hotkeys']['select_summary']);
  $('#text_hotkey_select_notesradar').val(setting['hotkeys']['select_notesradar']);
  $('#text_hotkey_select_screenshot').val(setting['hotkeys']['select_screenshot']);
  $('#text_hotkey_select_scoreinformation').val(setting['hotkeys']['select_scoreinformation']);
  $('#text_hotkey_select_scoregraph').val(setting['hotkeys']['select_scoregraph']);
  $('#text_hotkey_upload_musicselect').val(setting['hotkeys']['upload_musicselect']);

  if(!setting['summary_countmethod_only'])
    $('#radio_summary_countmethod_sum').prop('checked', true);
  else
    $('#radio_summary_countmethod_only').prop('checked', true);

  $('#check_display_result').prop('checked', setting['display_result']);
  $('#check_resultimage_filtered').prop('checked', setting['resultimage_filtered']);

  $('#text_imagesave_path').val(setting['imagesave_path']);

  $('#radio_startup_image_notesradar').prop('checked', setting['startup_image'] == 'notesradar');
  $('#radio_startup_image_summary').prop('checked', setting['startup_image'] == 'summary');

  $('#text_hashtags').val(setting['hashtags']);
  $('#check_data_collection').prop('checked', setting['data_collection']);

  $('input#text_portmain').val(setting['port']['main']);
  $('input#text_portsocket').val(setting['port']['socket']);

  $('div.summary_group_playmode').each(function() {
    const playmode = $(this).children('div.summary_playmode').text();
    if(!setting['summaries'].hasOwnProperty(playmode)) return true;

    $(this).find('div.summary_levelblock div.summary_group_level').each(function() {
      const level = $(this).children('div.summary_level').text();
      if(!setting['summaries'][playmode].hasOwnProperty(level)) return true;

      if(setting['summaries'][playmode][level].hasOwnProperty('cleartypes')) {
        $(this).find('div.summary_itemblock div.cleartype').each(function() {
          const key = $(this).children('label').text();
          if(setting['summaries'][playmode][level]['cleartypes'].includes(key))
            $(this).children('input').prop('checked', true);
        });
      }

      if(setting['summaries'][playmode][level].hasOwnProperty('djlevels')) {
        $(this).find('div.summary_itemblock div.djlevel').each(function() {
          const key = $(this).children('label').text();
          if(setting['summaries'][playmode][level]['djlevels'].includes(key))
            $(this).children('input').prop('checked', true);
        });
      }
    });
  });

  switch_filteroverlayenabled();
  
  const params = new URLSearchParams(window.location.search);
  if(!params.has('tab')) {
    switch_displaytab('general');
  }
  else {
    const tabname = params.get('tab')
    switch_displaytab(tabname);
  }
}

/**
 * タブの切り替え
 * 
 * 選択タブを指定のタブ名にする。
 * @param {str} tabname 対象のタブ名
 */
function switch_displaytab(tabname) {
  $('div.tabpage').css('display', 'none');
  $('button.select_tabpage').removeClass('select_tabpage_selected');

  $(`div#tabpage_${tabname}`).css('display', 'flex');
  $(`button#display_tabpage_${tabname}`).addClass('select_tabpage_selected');
}

/**
 * ライバル欄画像貼り付け設定の有効/無効の切替
 */
function switch_filteroverlayenabled(e) {
  const v = $('#check_filter_overlay').prop('checked');

  $('div.box_filter_overlay input').prop('disabled', !v);
  $('div.box_filter_overlay button').prop('disabled', !v);
}

/**
 * タブを選択
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_tab(e) {
  const id = e.target.id;

  const extracted = id.match(/(?<=display_tabpage_)(.*)/)[0];
  const splitted = extracted.split('_');

  switch_displaytab(splitted[0]);
}

/**
 * ライバル欄画像貼り付け設定が変更された
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_check_filteroverlay(e) {
  switch_filteroverlayenabled();
}

/**
 * ファイルを選択する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_browse_file(e) {
  const targetelement = $(e.target).prev();
  const selected = JSON.parse(await webui.browse_file(
    targetelement.val().replaceAll('\\', '/'),
    JSON.stringify([['Image file', '*.png']]),
  ));

  if(selected == null) return;

  const normalized = selected.replaceAll('/', '\\');
  targetelement.val(normalized);
}

/**
 * フォルダを選択する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_browse_directory(e) {
  const targetelement = $(e.target).prev();
  const selected = JSON.parse(await webui.browse_directory(
    targetelement.val().replaceAll('\\', '/'),
  ));

  if(selected == null) return;

  const normalized = selected.replaceAll('/', '\\');
  targetelement.val(normalized);
}

/**
 * 設定の保存かキャンセルボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_button_save(e) {
  const startupimage_selectedid = $('input[name="startup_image"]:checked').attr('id');
  const startup_image = startupimage_selectedid.match(/(?<=radio_startup_image_)(.*)/)[0];

  const summaries = {};
  $('div.summary_group_playmode').each(function() {
    const playmode = $(this).children('div.summary_playmode').text();

    summaries[playmode] = {}

    $(this).find('div.summary_levelblock div.summary_group_level').each(function() {
      const level = $(this).children('div.summary_level').text();

      summaries[playmode][level] = {
        'cleartypes': [],
        'djlevels': [],
      };

      $(this).find('div.summary_itemblock div.cleartype').each(function() {
        const key = $(this).children('label').text();
        if($(this).children('input').prop('checked'))
          summaries[playmode][level]['cleartypes'].push(key);
      });

      $(this).find('div.summary_itemblock div.djlevel').each(function() {
        const key = $(this).children('label').text();
        if($(this).children('input').prop('checked'))
          summaries[playmode][level]['djlevels'].push(key);
      });
    });
  });

  await webui.save_setting(JSON.stringify({
    'newrecord_only': $('#check_newrecord_only').prop('checked'),
    'play_sound': $('#check_play_sound').prop('checked'),
    'autosave': $('#check_autosave').prop('checked'),
    'autosave_filtered': $('#check_autosave_filtered').prop('checked'),
    'filter_compact': $('#check_filter_compact').prop('checked'),
    'filter_overlay': {
      'use': $('#check_filter_overlay').prop('checked'),
      'rival': {
        'imagefilepath': $('#text_overlayimagerival_path').val(),
        'offset': [
          $('#text_overlayimagerival_offsetx').val(),
          $('#text_overlayimagerival_offsety').val(),
        ],
        'scalefactor': $('#text_overlayimagerival_scalefactor').val(),
      },
      'loveletter': {
        'imagefilepath': $('#text_overlayimageloveletter_path').val(),
        'offset': [
          $('#text_overlayimageloveletter_offsetx').val(),
          $('#text_overlayimageloveletter_offsety').val(),
        ],
        'scalefactor': $('#text_overlayimageloveletter_scalefactor').val(),
      },
      'rivalname': {
        'imagefilepath': $('#text_overlayimagerivalname_path').val(),
        'offset': [
          $('#text_overlayimagerivalname_offsetx').val(),
          $('#text_overlayimagerivalname_offsety').val(),
        ],
        'scalefactor': $('#text_overlayimagerivalname_scalefactor').val(),
      },
    },
    'savefilemusicname_right': $('#check_savefilemusicname_right').prop('checked'),
    'hotkeys': {
      'active_screenshot': $('#text_hotkey_active_screenshot').val(),
      'select_summary': $('#text_hotkey_select_summary').val(),
      'select_notesradar': $('#text_hotkey_select_notesradar').val(),
      'select_screenshot': $('#text_hotkey_select_screenshot').val(),
      'select_scoreinformation': $('#text_hotkey_select_scoreinformation').val(),
      'select_scoregraph': $('#text_hotkey_select_scoregraph').val(),
      'upload_musicselect': $('#text_hotkey_upload_musicselect').val(),
    },
    'summary_countmethod_only': $('#radio_summary_countmethod_only').prop('checked'),
    'display_result': $('#check_display_result').prop('checked'),
    'resultimage_filtered': $('#check_resultimage_filtered').prop('checked'),
    'imagesave_path': $('#text_imagesave_path').val(),
    'startup_image': startup_image,
    'hashtags': $('#text_hashtags').val(),
    'data_collection': $('#check_data_collection').prop('checked'),
    'port': {
      'main': $('input#text_portmain').val(),
      'socket': $('input#text_portsocket').val(),
    },
    'summaries': summaries,
  }));

  window.parent.postMessage("setting_close", "*");
}

/**
 * 閉じるボタンを押す
 * 
 * ウィンドウを閉じる。
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_button_close(e) {
  window.parent.postMessage("setting_close", "*");
}
