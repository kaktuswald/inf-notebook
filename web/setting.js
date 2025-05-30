let setting = null;

$(function() {
  $('button.select_tabpage').on('click', onclick_tab);

  $('button#button_save').on('click', onclick_button_save);
  $('button#button_close').on('click', onclick_button_close);

  switch_displaytab('blank');
});

window.addEventListener('pywebviewready', initialize);

/**
 * 初期処理
 * 
 * ロード完了時に実行する。
 */
async function initialize() {
  setting = await pywebview.api.get_setting();
  globalThis.setting = setting;
  
  $('#check_newrecord_only').prop('checked', setting['newrecord_only']);
  $('#check_play_sound').prop('checked', setting['play_sound']);
  $('#check_autosave').prop('checked', setting['autosave']);
  $('#check_autosave_filtered').prop('checked', setting['autosave_filtered']);
  $('#check_filter_compact').prop('checked', setting['filter_compact']);
  $('#check_savefilemusicname_right').prop('checked', setting['savefilemusicname_right']);

  $('#text_hotkey_active_screenshot').val(setting['hotkeys']['active_screenshot']);
  $('#text_hotkey_upload_musicselect').val(setting['hotkeys']['upload_musicselect']);

  if(!setting['summary_countmethod_only'])
    $('#radio_summary_countmethod_sum').prop('checked', true);
  else
    $('#radio_summary_countmethod_only').prop('checked', true);

  $('#check_display_result').prop('checked', setting['display_result']);
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

  const tabname = await pywebview.api.get_starttab();
  if(tabname == null)
    switch_displaytab('general');
  else
    switch_displaytab(tabname);
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

  const portmain = Number($('input#text_portmain').val());
  const portsocket = Number($('input#text_portsocket').val());

  const portsetting = {
    'main': Number.isInteger(portmain) ? portmain : setting['port']['main'],
    'socket': Number.isInteger(portsocket) ? portsocket : setting['port']['socket'],
  }

  await pywebview.api.save({
    'newrecord_only': $('#check_newrecord_only').prop('checked'),
    'play_sound': $('#check_play_sound').prop('checked'),
    'autosave': $('#check_autosave').prop('checked'),
    'autosave_filtered': $('#check_autosave_filtered').prop('checked'),
    'filter_compact': $('#check_filter_compact').prop('checked'),
    'savefilemusicname_right': $('#check_savefilemusicname_right').prop('checked'),
    'hotkeys': {
      'active_screenshot': $('#text_hotkey_active_screenshot').val(),
      'upload_musicselect': $('#text_hotkey_upload_musicselect').val(),
    },
    'summary_countmethod_only': $('#radio_summary_countmethod_only').prop('checked'),
    'display_result': $('#check_display_result').prop('checked'),
    'imagesave_path': $('#text_imagesave_path').val(),
    'startup_image': startup_image,
    'hashtags': $('#text_hashtags').val(),
    'data_collection': $('#check_data_collection').prop('checked'),
    'port': {
      'main': $('input#text_portmain').val(),
      'socket': $('input#text_portsocket').val(),
    },
    'summaries': summaries,
  });

  pywebview.api.close();
}

/**
 * 閉じるボタンを押す
 * 
 * ウィンドウを閉じる。
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_button_close(e) {
  pywebview.api.close();
}
