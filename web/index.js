
pywebview = null;

setting = null;

musictable = null;

drawer_imagenothing = null;
drawer_simpletext = null;
drawer_information = null;
drawer_summary = null;
drawer_notesradar = null;
drawer_scoregraph = null;
drawer_scoreinformation = null;

selected_playmode = null;
selected_musicname = null;
selected_difficulty = null;
selected_timestamp = null;

reader_imagenothing = new FileReader();
reader_imagenothing.onloadend = onloadend_imagenothingimage;
reader_imagenothing.onerror = onerror_filereader;
reader_imagenothing.onabort = onabort_filereader;

reader_simpletext = new FileReader();
reader_simpletext.onloadend = onloadend_simpletextimage;
reader_simpletext.onerror = onerror_filereader;
reader_simpletext.onabort = onabort_filereader;

reader_information = new FileReader();
reader_information.onloadend = onloadend_informationimage;
reader_information.onerror = onerror_filereader;
reader_information.onabort = onabort_filereader;

reader_summary = new FileReader();
reader_summary.onloadend = onloadend_summaryimage;
reader_summary.onerror = onerror_filereader;
reader_summary.onabort = onabort_filereader;

reader_notesradar = new FileReader();
reader_notesradar.onloadend = onloadend_notesradarimage;
reader_notesradar.onerror = onerror_filereader;
reader_notesradar.onabort = onabort_filereader;

reader_scoreinformation = new FileReader();
reader_scoreinformation.onloadend = onloadend_scoreinformationimage;
reader_scoreinformation.onerror = onerror_filereader;
reader_scoreinformation.onabort = onabort_filereader;

reader_scoregraph = new FileReader();
reader_scoregraph.onloadend = onloadend_scoregraphimage;
reader_scoregraph.onerror = onerror_filereader;
reader_scoregraph.onabort = onabort_filereader;

imageblobs = {};
imageurls = {};

$(function() {
  $('button.select_tabpage').on('click', onclick_tab);

  $('button#button_save_scoreinformationimage').on('click', onclick_save_scoreinformationimage);
  $('button#button_save_scoregraphimage').on('click', onclick_save_scoregraphimage);

  $('button#button_post_summary').on('click', onclick_post_summary);
  $('button#button_post_notesradar').on('click', onclick_post_notesradar);
  $('button.button_post_scoreinformation').on('click', onclick_post_scoreinformation);

  $('button.button_openfolder_export').on('click', onclick_openfolder_export);
  $('button#button_openfolder_results').on('click', onclick_openfolder_results);
  $('button#button_openfolder_filtereds').on('click', onclick_openfolder_filtereds);
  $('button#button_openfolder_scoreinformations').on('click', onclick_openfolder_scoreinformations);
  $('button#button_openfolder_scorecharts').on('click', onclick_openfolder_scorecharts);

  $('button#button_summary_switch').on('click', onclick_summary_switch);
  $('button#button_summary_setting').on('click', onclick_summary_setting);

  $('button#button_setting_open').on('click', onclick_setting_open);
  $('button#button_export_open').on('click', onclick_export_open);
  $('button#button_confirm_outputcsv').on('click', onclick_confirm_outputcsv);
  $('button#button_execute_outputcsv').on('click', onclick_execute_outputcsv);
  $('button#button_confirm_clearrecent').on('click', onclick_confirm_clearrecent);
  $('button#button_execute_clearrecent').on('click', onclick_execute_clearrecent);

  $('#button_switch_background').on('click', onclick_switch_background);

  $('button#button_recents_save_resultimages').on('click', onclick_recents_save_resultimages);
  $('button#button_recents_save_resultimages_filtered').on('click', onclick_recents_save_resultimages_filtered);
  $('button#button_recents_post_results').on('click', onclick_recents_post_results);
  $('button#button_recents_confirm_uploadcollectionimages').on('click', onclick_recents_confirm_uploadcollectionimages);
  $('button#button_recents_execute_uploadcollectionimages').on('click', onclick_recents_execute_uploadcollectionimages);

  $('select#select_versions').on('change', onchange_scoreselect_version);
  $('input#text_musicname_search').on('input', oninput_scoreselect_musicname);
  $('input[name="musicname_search_playmode"]').on('change', onchange_scoreresult_playmode);
  $('select#select_difficulties').on('change', onchange_scoreresult_difficulty);

  $('button#button_confirm_deletemusicnotebook').on('click', onclick_confirm_deletemusicnotebook);
  $('button#button_execute_deletemusicnotebook').on('click', onclick_execute_deletemusicnotebook);
  $('button#button_confirm_deletescoreresult').on('click', onclick_confirm_deletescoreresult);
  $('button#button_execute_deletescoreresult').on('click', onclick_execute_deletescoreresult);
  $('button#button_confirm_deleteplayresult').on('click', onclick_confirm_deleteplayresult);
  $('button#button_execute_deleteplayresult').on('click', onclick_execute_deleteplayresult);

  $('input#text_discordwebhook_playername').on('input', oninput_discordwebhook_playername);
  $('input#text_discordwebhook_playername').on('change', onchange_discordwebhook_playername);

  $('button#button_discordwebhook_add').on('click', onclick_discordwebhook_add);
  $('button#button_discordwebhook_update').on('click', onclick_discordwebhook_update);
  $('button#button_discordwebhook_activate').on('click', onclick_discordwebhook_activate);
  $('button#button_discordwebhook_deactivate').on('click', onclick_discordwebhook_deactivate);
  $('button#button_discordwebhook_delete').on('click', onclick_discordwebhook_delete);

  $('input[name="notesradar_playmode"]').on('change', onchange_notesradar_playmode);
  $('select#select_notesradar_attributes').on('change', onchange_notesradar_attribute);
  $('input[name="notesradar_tablemode"]').on('change', onchange_notesradar_tablemode);

  $('button#button_best_switch_timestamp').on('click', onclick_best_switch_timestamp);
  $('button#button_best_switch_useoption').on('click', onclick_best_switch_useoption);

  $('button#button_execute_findnewestversionaction').on('click', onclick_execute_findnewestversionaction);

  $('button.dialogclose').on('click', onclick_button_dialogclose);

  switch_displaytab('main', 'information');
  switch_displaytab('control', 'recents');
  switch_displaytab('detail', 'best');
});

window.addEventListener('pywebviewready', initialize);

/**
 * 初期処理
 * 
 * ロード完了時に実行する。Python側から選択肢のリストを取得する。
 */
async function initialize() {
  const fontfamily = $('body').css('font-family');

  Chart.defaults.font.family = fontfamily;

  const result = await pywebview.api.check_latestversion();
  if(result != null) {
    $('div#findnewestversion_message').text(result);
    $('dialog#dialog_findnewestversion')[0].showModal();
  }

  const [width, height] = await pywebview.api.get_imagesize();

  const playmodes = await pywebview.api.get_playmodes();
  const difficulties = await pywebview.api.get_difficulties();
  const attributes = await pywebview.api.get_notesradar_attributes();

  for(const difficulty of difficulties) {
    $('#select_difficulties').append($('<option>')
      .val(difficulty)
      .text(difficulty)
    );
  }

  for(const attribute of attributes) {
    $('#select_notesradar_attributes').append($('<option>')
      .val(attribute)
      .text(attribute)
    );
  }

  const setting = await pywebview.api.get_setting();
  setting_set(setting);

  drawer_imagenothing = new DrawerSimpletext(width, height, fontfamily);
  drawer_simpletext = new DrawerSimpletext(width, height, fontfamily);
  drawer_information = new DrawerInformation(width, height, fontfamily);
  drawer_summary = new DrawerSummary(width, height, fontfamily);
  drawer_notesradar = new DrawerNotesradar(playmodes, width, height);
  drawer_scoreinformation = new DrawerScoreinformation(width, height, fontfamily);
  drawer_scoregraph = new DrawerScoregraph(width, height);

  drawer_imagenothing.draw_text = draw_text;
  drawer_simpletext.draw_text = draw_text;
  drawer_information.draw_text = draw_text;
  drawer_summary.draw_text = draw_text;
  drawer_notesradar.draw_text = draw_text;
  drawer_scoreinformation.draw_text = draw_text;
  drawer_scoregraph.draw_text = draw_text;
  
  await generate_imagenothingimage();
  await generate_loadingimage();

  await pywebview.api.checkresource();

  await load_musictable();

  await pywebview.api.execute_records_processing();
  await pywebview.api.execute_generate_notesradar();

  await generate_infinitasinformatioinimage();
  
  await draw_summary();
  await draw_notesradar();

  switch_displaytab('main', setting.startup_image);

  await set_recentnotebook_results(false);

  pywebview.api.start_capturing();
}

async function generate_imagenothingimage() {
  const blob = await drawer_imagenothing.draw_simple('画像なし');
  const url = URL.createObjectURL(blob);

  imageblobs['imagenothing'] = blob;
  imageurls['imagenothing'] = url;

  $('img#image_information').attr('src', url);
  $('img#image_summary').attr('src', url);
  $('img#image_notesradar').attr('src', url);
  $('img#image_screenshot').attr('src', url);
  $('img#image_scoregraph').attr('src', url);
  $('img#image_scoreinformation').attr('src', url);

  reader_imagenothing.abort();
  reader_imagenothing.readAsDataURL(blob);
}

async function generate_loadingimage() {
  const blob = await drawer_simpletext.draw_message('インフィニタス ローディング', '30秒ごとにローディングの状況をチェックします');
  const url = URL.createObjectURL(blob);

  imageblobs['loading'] = blob;
  imageurls['loading'] = url;
}

async function generate_resourcecheckimage() {
  const blob = await drawer_simpletext.draw_simple('最新データチェック中');
  const url = URL.createObjectURL(blob);

  $('img#image_information').attr('src', url);

  reader_simpletext.abort();
  reader_simpletext.readAsDataURL(blob);
}

async function generate_summaryprocessingimage() {
  const blob = await drawer_simpletext.draw_message('統計データ処理中', 'しばらく時間がかかる場合があります');
  const url = URL.createObjectURL(blob);

  $('img#image_information').attr('src', url);

  reader_simpletext.abort();
  reader_simpletext.readAsDataURL(blob);
}

async function generate_infinitasinformatioinimage() {
  const blob = await drawer_information.draw(musictable);
  const url = URL.createObjectURL(blob);

  imageblobs['infinitasinformation'] = blob;
  imageurls['infinitasinformation'] = url;

  $('img#image_information').attr('src', url);

  reader_information.abort();
  reader_information.readAsDataURL(blob);
}

/**
 * 初期処理完了時のメインタブ変更
 */
function selecttab_main_initial() {
  const startup_tabname = setting['startup_image'];

  $('div.tabpage_main').css('display', 'none');
  $(`div#tabpage_main_${startup_tabname}`).css('display', 'flex');
}

/**
 * Python側からのメッセージ処理

 * @param {*} message メッセージ本文
 */
function communication_message(message, data = null) {
  // // switch文に直したい
  // if(message == 'start_resourcecheck')
  //   generate_resourcecheckimage();
  // if(message == 'start_summaryprocessing')
  //   generate_summaryprocessingimage();
  // if(message == 'switch_displaytab')
  //   switch_displaytab(data.groupname, data.tabname);
  // if(message == 'request_imagereload')
  //   request_imagereload(data.tagid, data.filename);
  // if(message == 'switch_detect_infinitas')
  //   switch_detect_infinitas(data);
  // if(message == 'switch_capturable')
  //   switch_capturable(data);
  // if(message == 'detect_loading')
  //   detect_loading();
  // if(message == 'escape_loading')
  //   escape_loading();
  // if(message == 'update_summary')
  //   draw_summary();
  // if(message == 'update_notesradar')
  //   update_notesradar();
  // if(message == 'update_recentrecords')
  //   set_recentnotebook_results(data);
  // if(message == 'discordwebhook_refresh')
  //   reload_discordwebhook_settings();
  // if(message == 'activescreenshot')
  //   activescreenshot(data);
  // if(message == 'musicselect_upload')
  //   musicselect_upload();
  // if(message == 'discordwebhook_append_log')
  //   discordwebhook_append_logs(data);
  // if(message == 'scoreselect')
  //   select_score(data.musicname, data.playmode, data.difficulty);
  // if(message == 'append_log')
  //   append_log(data);

  switch(message) {
    case 'start_resourcecheck':
      generate_resourcecheckimage();
      break;
    case 'start_summaryprocessing':
      generate_summaryprocessingimage();
      break;
    case 'switch_displaytab':
      switch_displaytab(data.groupname, data.tabname);
      break;
    case 'request_imagereload':
      request_imagereload(data.tagid, data.filename);
      break;
    case 'switch_detect_infinitas':
      switch_detect_infinitas(data);
      break;
    case 'switch_capturable':
      switch_capturable(data);
      break;
    case 'detect_loading':
      detect_loading();
      break;
    case 'escape_loading':
      escape_loading();
      break;
    case 'update_summary':
      draw_summary();
      break;
    case 'update_notesradar':
      update_notesradar();
      break;
    case 'update_recentrecords':
      set_recentnotebook_results(data);
      break;
    case 'discordwebhook_refresh':
      reload_discordwebhook_settings();
      break;
    case 'activescreenshot':
      activescreenshot(data);
      break;
    case 'musicselect_upload':
      musicselect_upload();
      break;
    case 'discordwebhook_append_log':
      discordwebhook_append_logs(data);
      break;
    case 'scoreselect':
      select_score(data.musicname, data.playmode, data.difficulty);
      break;
    case 'append_log':
      append_log(data);
      break;
  }
}

function display_loadingimage() {
  $('img#image_information').attr('src', imageurls['loading']);
  switch_displaytab('main', 'information');

  reader_information.abort();
  reader_information.readAsDataURL(imageblobs['loading']);
}

function detect_loading() {
    display_loadingimage();
}

function escape_loading() {
  $('img#image_information').attr('src', imageurls['infinitasinformation']);

  reader_information.abort();
  reader_information.readAsDataURL(imageblobs['infinitasinformation']);

  switch_displaytab('main', setting.startup_image);
}

/**
 * 対象のタグの画像をリロードする
 * 
 * @param {string} tagid 対象のタグのID
 * @param {string} filename ファイル名
 */
function request_imagereload(tagid, filename) {
  const timestamp = new Date().getTime();
  $(`img#${tagid}`).attr('src', `image/${filename}?${timestamp}`);
}

async function setting_set(setting) {
  globalThis.setting = setting;

  if(setting['debug'])
    $('#display_tabpage_main_log').css('display', 'inline-block');

  if(setting['data_collection'])
    $('#button_recents_confirm_uploadcollectionimages').css('display', 'block');
  else
    $('#button_recents_confirm_uploadcollectionimages').css('display', 'none');

  $('input#text_discordwebhook_playername').val(setting['discord_webhook']['djname']);

  refresh_discordwebhook_settings(setting['discord_webhook']['servers']);
}

/**
 * 全曲データを読み出す
 */
async function load_musictable() {
  musictable = await pywebview.api.get_musictable();

  selected_musicname = null;

  for(const version in musictable['versions']) {
    $('#select_versions').append($('<option>')
      .val(version)
      .text(version)
    );
  }

  for(const musicname in musictable['musics']) {
    const tr = $('<tr>');
    tr.addClass('tableitem musictableitem');

    const td_musicname = $('<td>').text(musicname);
    td_musicname.addClass('music_cell_musicname');
    tr.append(td_musicname);

    const td_version = $('<td>').text(musictable['musics'][musicname]['version']);
    td_version.addClass('music_cell_version');
    tr.append(td_version);
    
    tr.on('click', onclick_musictableitem);
    $('#table_musics').append(tr);
  }
}

/**
 * 最近のリザルトをセットする
 * @param {boolean} selectnewest 最新のリザルトを選択する
 * @param {{}[]} values 最近のリザルトのデータ
 */
async function set_recentnotebook_results(selectnewest) {
  const values = await pywebview.api.get_recentnotebooks();

  const firstselect_timestamp = $('tr.recentresultitem.select_first').find('td.recentresult_cell_timestamp').text();
  const selected_timestamps = [];
  $('tr.recentresultitem.selected').each(function() {
    selected_timestamps.push($(this).find('td.recentresult_cell_timestamp').text());
  });

  $('tr.recentresultitem').remove();

  values.forEach(value => {
    const tr = $('<tr>');
    tr.addClass('tableitem recentresultitem');

    const td_latest = $('<td>').text(value['latest'] ? '☑' : '');
    td_latest.addClass('center cell_check recentresult_cell_latest');
    tr.append(td_latest);

    const td_saved = $('<td>').text(value['saved'] ? '☑' : '');
    td_saved.addClass('center cell_check recentresult_cell_saved');
    tr.append(td_saved);

    const td_filtered = $('<td>').text(value['filtered'] ? '☑' : '');
    td_filtered.addClass('center cell_check recentresult_cell_filtered');
    tr.append(td_filtered);

    const td_displaymusicname = $('<td>').text(typeof value['musicname'] === 'string' ? value['musicname'] : '?????');
    td_displaymusicname.addClass('recentresult_cell_displaymusicname');
    tr.append(td_displaymusicname);

    const td_scoretype = $('<td>').text((typeof value['playmode'] === 'string' && typeof value['difficulty'] === 'string') ? `${value['playmode']}${value['difficulty'][0]}` : '???');
    td_scoretype.addClass('center recentresult_cell_scoretype');
    tr.append(td_scoretype);

    const td_news_cleartype = $('<td>').text(value['news_cleartype'] ? '☑' : '');
    td_news_cleartype.addClass('center cell_check recentresult_cell_news_cleartype');
    tr.append(td_news_cleartype);

    const td_news_djlevel = $('<td>').text(value['news_djlevel'] ? '☑' : '');
    td_news_djlevel.addClass('center cell_check recentresult_cell_news_djlevel');
    tr.append(td_news_djlevel);

    const td_news_score = $('<td>').text(value['news_score'] ? '☑' : '');
    td_news_score.addClass('center cell_check recentresult_cell_news_score');
    tr.append(td_news_score);

    const td_news_misscount = $('<td>').text(value['news_misscount'] ? '☑' : '');
    td_news_misscount.addClass('center cell_check recentresult_cell_news_misscount');
    tr.append(td_news_misscount);

    const td_playmode = $('<td>').text(value['playmode']);
    td_playmode.addClass('recentresult_cell_playmode cell_hidden');
    tr.append(td_playmode);

    const td_musicname = $('<td>').text(value['musicname']);
    td_musicname.addClass('recentresult_cell_musicname cell_hidden');
    tr.append(td_musicname);

    const td_difficulty = $('<td>').text(value['difficulty']);
    td_difficulty.addClass('recentresult_cell_difficulty cell_hidden');
    tr.append(td_difficulty);

    const td_timestamp = $('<td>').text(value['timestamp']);
    td_timestamp.addClass('center recentresult_cell_timestamp cell_hidden');
    tr.append(td_timestamp);

    if(value['timestamp'] == firstselect_timestamp)
      tr.addClass('select_first')
    if(selected_timestamps.includes(value['timestamp']))
      tr.addClass('selected')

    tr.on('click', onclick_recentresultitem);

    $('#table_recents').append(tr);
  });

  if(selectnewest)
    select_newest_recentresult();
}

/**
 * 最新の最近のリザルトを選択する
 */
function select_newest_recentresult() {
  $('tr.recentresultitem.select_first').removeClass('select_first');
  $('tr.recentresultitem.selected').removeClass('selected');

  $('tr.recentresultitem:first').addClass('select_first');
  $('tr.recentresultitem:first').addClass('selected');

  display_scoreresult_and_playresult_from_recents();
}

/**
 * 対象の譜面を選択状態にする
 * 
 * 選曲画面で譜面を認識したときに実行する。
 * @param {string} musicname 曲名
 * @param {string} playmode プレイモード(SP or DP)
 * @param {string} difficulty 譜面難易度
 */
function select_score(musicname, playmode, difficulty) {
  if(!change_selected_score(musicname, playmode, difficulty))
    return;

  $('tr.recentresultitem.select_first').removeClass('select_first');
  $('tr.recentresultitem.selected').removeClass('selected');

  display_scoreresult();
}

/**
 * 最近のリザルトタブから選択された譜面の記録を表示する
 */
function display_scoreresult_and_playresult_from_recents() {
  const targetitem = $('tr.recentresultitem.select_first')

  const playmode = targetitem.children('td.recentresult_cell_playmode').text();
  const musicname = targetitem.children('td.recentresult_cell_musicname').text();
  const difficulty = targetitem.children('td.recentresult_cell_difficulty').text();

  if(playmode.lenth == 0) playmode = null;
  if(musicname.lenth == 0) musicname = null;
  if(difficulty.lenth == 0) difficulty = null;

  if(change_selected_score(musicname, playmode, difficulty))
    display_scoreresult();

  const timestamp = targetitem.children('td.recentresult_cell_timestamp').text();
  display_playresult(timestamp);
}

/**
 * 検索タブから選択された譜面の記録を表示する
 */
function display_scoreresult_from_scoresearch() {
  const selected_playmode_id = $('input[name="musicname_search_playmode"]:checked').attr('id');

  musicname = $('tr.musictableitem.selected .music_cell_musicname').first().text();
  playmode = $(`label[for="${selected_playmode_id}"]`).text();
  difficulty = $('#select_difficulties option:selected').val();

  selected_musicname = musicname.length > 0 ? musicname : null;
  selected_playmode = playmode.length > 0 ? playmode : null;
  selected_difficulty = difficulty.length > 0 ? difficulty : null;

  display_scoreresult();

  selected_timestamp = null;
  
  clear_playresult();
}

/**
 * 対象の譜面を選択状態にする
 * @param {string} musicname 曲名
 * @param {string} playmode プレイモード(SP or DP)
 * @param {string} difficulty 譜面難易度
 * @returns {boolean} 変更の有無
 */
function change_selected_score(musicname, playmode, difficulty) {
  if(musicname == selected_musicname && playmode == selected_playmode && difficulty == selected_difficulty)
    return false;

  $('tr.musictableitem.selected').removeClass('selected');
  const targetmusicitem = $('tr.musictableitem').filter(function() {
    return $(this).children('td.music_cell_musicname').text() == musicname;
  });
  targetmusicitem.addClass('selected');

  const target_playmode_id = $(`label.musicname_search_playmode:contains("${playmode}")`).attr('for');
  $(`input#${target_playmode_id}`).prop('checked', true);

  $('#select_difficulties').val(difficulty);

  selected_playmode = playmode
  selected_musicname = musicname
  selected_difficulty = difficulty

  return true;
}

/**
 * 選択している譜面の情報を検索タブの状態から取得する
 */
function get_selected_score() {
  const selected_playmode_id = $('input[name="musicname_search_playmode"]:checked').attr('id');

  const playmode = $(`label[for="${selected_playmode_id}"]`).text();
  const musicname = $('tr.musictableitem.selected .music_cell_musicname').first().text();
  const difficulty = $('#select_difficulties option:selected').val();

  selected_playmode = playmode.length > 0 ? playmode : null;
  selected_musicname = musicname.length > 0 ? musicname : null;
  selected_difficulty = difficulty.length > 0 ? difficulty : null;
}

/**
 * 選択されている譜面の記録を表示する
 */
async function display_scoreresult() {
  $('table#table_timestamps tr.timestampitem').remove();

  $('span#musicname').text('');
  $('#score_played_count').text('');
  clear_bests();

  if(selected_musicname == null || selected_playmode == null || selected_difficulty == null) {
    $('img#image_scoreinformation').attr('src', imageurls['imagenothing']);
    $('img#image_scoregraph').attr('src', imageurls['imagenothing']);
    return;
  }

  const scoreresult = await pywebview.api.get_scoreresult(selected_musicname, selected_playmode, selected_difficulty);

  if(scoreresult == null) {
    $('img#image_scoreinformation').attr('src', imageurls['imagenothing']);
    $('img#image_scoregraph').attr('src', imageurls['imagenothing']);
    return;
  }

  $('span#musicname').text(selected_musicname);

  const blob_scoreinformation = await drawer_scoreinformation.draw(
    scoreresult,
    selected_playmode,
    selected_musicname,
    selected_difficulty,
  );

  const url_scoreinformation = URL.createObjectURL(blob_scoreinformation);

  update_imageurl('scoreinformation', 'image_scoreinformation', url_scoreinformation);

  reader_scoreinformation.abort();
  reader_scoreinformation.readAsDataURL(blob_scoreinformation);

  if(scoreresult.timestamps != null && scoreresult.timestamps.length > 0) {
    $('#score_played_count').text(scoreresult.timestamps.length);

    const xvalues = [];
    const scores = [];
    const misscounts = [];

    scoreresult.timestamps.reverse().forEach(timestamp => {
      const tr = $('<tr>');
      tr.addClass('tableitem timestampitem');
      if(timestamp == selected_timestamp)
        tr.addClass('selected');
  
      const td_musicname = $('<td>').text(timestamp);
      td_musicname.addClass('timestamp_cell_timestamp');
      tr.append(td_musicname);
  
      tr.on('click', onclick_timestampitem);
      
      $('table#table_timestamps').append(tr);

      const targetresult = scoreresult['history'][timestamp];
      
      const date = timestamp.slice(0, 8);
      const time = timestamp.slice(9, 15);

      const year = date.slice(0, 4);
      const month = date.slice(4, 6);
      const day = date.slice(6, 8);

      const hours = time.slice(0, 2);
      const minutes = time.slice(2, 4);
      const seconds = time.slice(4, 6);

      xvalues.push(new Date(year, month - 1, day, hours, minutes, seconds));
      scores.push(targetresult['score']['value']);
      misscounts.push(targetresult.hasOwnProperty('miss_count') ? targetresult['miss_count']['value'] : null);
    });

    const chartdata = [[], []];
    for(let i = 0; i < xvalues.length; i++) {
      chartdata[0].push({x: xvalues[i], y: scores[i]});
      chartdata[1].push({x: xvalues[i], y: misscounts[i]});
    }

    const xvalue_max = new Date(xvalues[0]);
    const xvalue_min = xvalues[xvalues.length - 1];
    xvalue_max.setDate(xvalue_max.getDate() + 1);

    const xrange = [
      `${xvalue_min.getFullYear()}${String(xvalue_min.getMonth()+1).padStart(2, '0')}${String(xvalue_min.getDate()).padStart(2, '0')}`,
      `${xvalue_max.getFullYear()}${String(xvalue_max.getMonth()+1).padStart(2, '0')}${String(xvalue_max.getDate()).padStart(2, '0')}`,
    ];

    const blob_scoregraph = await drawer_scoregraph.draw(
      chartdata,
      xrange,
      scoreresult['notes'],
      selected_musicname,
      selected_playmode,
      selected_difficulty
    );

    const url_scoregraph = URL.createObjectURL(blob_scoregraph);

    update_imageurl('scoregraph', 'image_scoregraph', url_scoregraph);

    reader_scoregraph.abort();
    reader_scoregraph.readAsDataURL(blob_scoregraph);
  }
  else {
    $('img#image_scoregraph').attr('src', imageurls['imagenothing']);
  }

  if(scoreresult.best != null) {
    display_best_cleartype(scoreresult.best.clear_type);
    display_best_djlevel(scoreresult.best.dj_level);
    display_best_score(scoreresult.best.score);
    display_best_misscount(scoreresult.best.miss_count);
  }
  else {
    clear_bests();
  }
}

/**
 * リザルトの記録表示を全てクリアする
 */
function clear_playresult() {
  $('img#image_screenshot').attr('src', imageurls['imagenothing']);

  $('#playresult_datetime').text('');
  $('#playresult_cleartype').text('');
  $('#playresult_djlevel').text('');
  $('#playresult_score').text('');
  $('#playresult_misscount').text('');
  $('#playresult_options').text('');
}

/**
 * 選択されたリザルトの記録を表示する
 * @param {string} timestamp リザルトのタイムスタンプ
 */
async function display_playresult(timestamp) {
  if(selected_musicname == null || selected_playmode == null || selected_difficulty == null) {
    clear_playresult();
    return;
  }

  if(timestamp.length == 0) return;

  selected_timestamp = timestamp;

  const encodedimage = await pywebview.api.get_resultimage(selected_musicname, selected_playmode, selected_difficulty, timestamp);
  display_encodedimage(encodedimage, 'image_screenshot');

  const playresult = await pywebview.api.get_playresult(selected_musicname, selected_playmode, selected_difficulty, timestamp);

  if(playresult == null) return;

  if(timestamp != null) {
    const t = timestamp;
    const date = `${t.slice(0, 4)}年${t.slice(4, 6)}月${t.slice(6, 8)}日`
    const time = `${t.slice(9, 11)}時${t.slice(11, 13)}分${t.slice(13, 15)}秒`
    $('#playresult_datetime').text(`${date} ${time}`);
  }

  if(playresult.clear_type != null)
    $('#playresult_cleartype').text(playresult.clear_type.value);

  if(playresult.dj_level != null)
    $('#playresult_djlevel').text(playresult.dj_level.value);
  
  if(playresult.score != null)
    $('#playresult_score').text(playresult.score.value);
    
  if(playresult.miss_count != null)
    $('#playresult_misscount').text(playresult.miss_count.value);

  if(playresult.options != null) {
    const options = [
      playresult.options.arrange != null ? playresult.options.arrange : '',
      playresult.options.flip != null ? playresult.options.flip : '',
      playresult.options.assist != null ? playresult.options.assist : '',
      (playresult.options.battle != null && playresult.options.battle) ? 'BATTLE' : '',
    ];
    $('#playresult_options').text(options.join(' '));
  }
  else {
    $('#playresult_options').text('不明');
  }
}

/**
 * インフィニタスの発見状態の切り替え
 * @param {boolean} flag 発見状態
 */
function switch_detect_infinitas(flag) {
  if(flag)
    $('#detect_infinitas').addClass('toggle_on');
  else
    $('#detect_infinitas').removeClass('toggle_on');
}

/**
 * インフィニタスのキャプチャーの可能状態の切り替え
 * @param {boolean} flag キャプチャーの可能状態
 */
function switch_capturable(flag) {
  if(flag)
    $('#capturable').addClass('toggle_on');
  else
    $('#capturable').removeClass('toggle_on');
}

/**
 * タブの切り替え
 * 
 * 対象のタブグループの、選択タブを指定のタブ名にする。
 * @param {str} groupname 対象のタブグループ名
 * @param {str} tabname 対象のタブ名
 */
function switch_displaytab(groupname, tabname) {
  $(`div.tabpage_${groupname}`).css('display', 'none');
  $(`button.select_tabpage_${groupname}`).removeClass('select_tabpage_selected');

  $(`div#tabpage_${groupname}_${tabname}`).css('display', 'flex');
  $(`button#display_tabpage_${groupname}_${tabname}`).addClass('select_tabpage_selected');
}

/**
 * タブを選択
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_tab(e) {
  const id = e.target.id;

  const extracted = id.match(/(?<=display_tabpage_)(.*)/)[0];
  const splitted = extracted.split('_');

  switch_displaytab(splitted[0], splitted[1]);
}

/**
 * 譜面記録画像を保存する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_save_scoreinformationimage(e) {
  if(selected_playmode == null || selected_musicname == null || selected_difficulty == null) return;
  
  if(!await pywebview.api.save_scoreinformationimage(selected_playmode, selected_musicname, selected_difficulty))
    $('dialog#dialog_message_imagesavefailed')[0].showModal();
}

/**
 * 譜面グラフ画像を保存する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_save_scoregraphimage(e) {
  if(selected_playmode == null || selected_musicname == null || selected_difficulty == null) return;

  if(!await pywebview.api.save_scoregraphimage(selected_playmode, selected_musicname, selected_difficulty))
    $('dialog#dialog_message_imagesavefailed')[0].showModal();
}

/**
 * 最近のリザルトを選択
 * @param {ce.Event} e イベントハンドラ
 * @returns 
 */
function onclick_recentresultitem(e) {
  if(!e.ctrlKey && !e.shiftKey) {
    $('tr.recentresultitem.select_first').removeClass('select_first');
    $('tr.recentresultitem.selected').removeClass('selected');
    $(this).addClass('select_first');
    $(this).addClass('selected');
  }
  else {
    if(e.ctrlKey) {
      if($(this).hasClass('select_first'))
        $(this).removeClass('select_first');
      else
        if($('tr.recentresultitem.select_first').length == 0) $(this).addClass('select_first');

      if($(this).hasClass('selected'))
        $(this).removeClass('selected');
      else
        $(this).addClass('selected');
    }
    if(e.shiftKey) {
      const first = $('.recentresultitem.select_first');
      if(first.length <= 0) return;

      $('tr.recentresultitem').removeClass('selected');
      const index_first = $('#table_recents .recentresultitem').index($(first));
      const index_current = $('#table_recents .recentresultitem').index($(this));
      if(index_first < index_current)
        $(this).prevUntil('.select_first').addClass('selected');
      else
        $(this).nextUntil('.select_first').addClass('selected');
      $(this).addClass('selected')
      $(first).addClass('selected')
    }
  }

  if(!$(this).hasClass('select_first')) return;

  display_scoreresult_and_playresult_from_recents();
}

/**
 * 統計をポストする
 * 
 * ブラウザでXのポストのページを開く
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_post_summary(e) {
  pywebview.api.post_summary();
}

/**
 * ノーツレーダーをポストする
 * 
 * ブラウザでXのポストのページを開く
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_post_notesradar(e) {
  pywebview.api.post_notesradar();
}

/**
 * 譜面記録をポストする
 * 
 * ブラウザでXのポストのページを開く
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_post_scoreinformation(e) {
  pywebview.api.post_scoreinformation(
    selected_musicname,
    selected_playmode,
    selected_difficulty,
  );
}

/**
 * エクスポートフォルダを開く
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_openfolder_export(e) {
  if(!await pywebview.api.openfolder_export())
    $('dialog#dialog_message_openfolderfailed')[0].showModal();
}

/**
 * リザルト画像のフォルダを開く
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_openfolder_results(e) {
  if(!await pywebview.api.openfolder_results())
    $('dialog#dialog_message_openfolderfailed')[0].showModal();
}

/**
 * ぼかしの入ったリザルト画像のフォルダを開く
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_openfolder_filtereds(e) {
  if(!await pywebview.api.openfolder_filtereds())
    $('dialog#dialog_message_openfolderfailed')[0].showModal();
}

/**
 * スコア情報フォルダを開く
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_openfolder_scoreinformations(e) {
  if(!await pywebview.api.openfolder_scoreinformations())
    $('dialog#dialog_message_openfolderfailed')[0].showModal();
}

/**
 * 譜面グラフフォルダを開く
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_openfolder_scorecharts(e) {
  if(!await pywebview.api.openfolder_scorecharts())
    $('dialog#dialog_message_openfolderfailed')[0].showModal();
}

/**
 * 最近のリザルトの画像保存ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_recents_save_resultimages(e) {
  const timestamps = [];
  $('tr.recentresultitem.selected').each(function() {
    timestamps.push($(this).find('td.recentresult_cell_timestamp').text());
  });

  pywebview.api.recents_save_resultimages(timestamps);
}

/**
 * 最近のリザルトのぼかしを入れた画像保存ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_recents_save_resultimages_filtered(e) {
  const timestamps = [];
  $('tr.recentresultitem.selected').each(function() {
    timestamps.push($(this).find('td.recentresult_cell_timestamp').text());
  });

  await pywebview.api.recents_save_resultimages_filtered(timestamps);

  const item = $('tr.recentresultitem.select_first').first();
  const encodedimage = await pywebview.api.get_resultimage_filtered(item.children('td.recentresult_cell_timestamp').text());
  display_encodedimage(encodedimage, 'image_screenshot');
}

/**
 * 最近のリザルトのポストボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_recents_post_results(e) {
  const timestamps = [];
  $('tr.recentresultitem.selected').each(function() {
    timestamps.push($(this).find('td.recentresult_cell_timestamp').text());
  });

  pywebview.api.recents_post_results(timestamps);
}

/**
 * カウント方式切替ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_summary_switch(e) {
  await pywebview.api.switch_summarycountmethod();

  const setting = await pywebview.api.get_setting();
  setting_set(setting);

  draw_summary();
}

/**
 * 統計設定ボタンを押す
 * 
 * 設定画面を開いて、統計タブをアクティブにする。
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_summary_setting(e) {
  pywebview.api.openwindow_setting('summary');
}

/**
 * 設定ボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_setting_open(e) {
  operation_disable();
  await pywebview.api.openwindow_setting();
  operation_enable();

  const setting = await pywebview.api.get_setting();
  setting_set(setting);

  draw_summary();
}

/**
 * エクスポートボタンを押す
 * 
 * エクスポート説明表示や、設定を行うウィンドウを表示する。
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_export_open(e) {
  operation_disable();
  await pywebview.api.openwindow_export();
  operation_enable();
}

/**
 * CSV出力を実行するか確認
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_confirm_outputcsv(e) {
  $('dialog#dialog_confirm_outputcsv')[0].showModal();
}

/**
 * CSV出力を実行
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_execute_outputcsv(e) {
  pywebview.api.output_csv();

  $(this).closest('dialog')[0].close();
}

/**
 * 最近のデータのクリアをするか確認
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_confirm_clearrecent(e) {
  $('dialog#dialog_confirm_clearrecent')[0].showModal();
}

/**
 * 最近のデータのクリアを実行
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_execute_clearrecent(e) {
  pywebview.api.clear_recent();

  $(this).closest('dialog')[0].close();
}

/**
 * メインタブの背景色を切り替える
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_switch_background(e) {
  if($('.tabpage_main').css('background-color') == 'rgb(0, 0, 0)')
    $('.tabpage_main').css('background-color', 'white')
  else
    $('.tabpage_main').css('background-color', 'black')
}

/**
 * 設定の保存かキャンセルボタンを押す
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_setting_close(e) {
  $('#setting').css('display', 'none');
}

/**
 * ベスト記録の表示を更新日時表示に切り替える
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_best_switch_timestamp(e) {
  $('.best_useoptions').css('display', 'none');
  $('.best_timestamps').css('display', 'inline-block');
}

/**
 * ベスト記録の表示を使用オプション表示に切り替える
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_best_switch_useoption(e) {
  $('.best_timestamps').css('display', 'none');
  $('.best_useoptions').css('display', 'inline-block');
}

/**
 * 誤認識された画像をクラウドにアップロードするか確認する
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_recents_confirm_uploadcollectionimages(e) {
  const timestamps = [];
  $('tr.recentresultitem.selected').each(function() {
    timestamps.push($(this).find('td.recentresult_cell_timestamp').text());
  });

  if(timestamps.length == 0) return;

  $('dialog#dialog_confirm_uploadcollection')[0].showModal();
}

/**
 * 誤認識された画像をクラウドにアップロードする
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_recents_execute_uploadcollectionimages(e) {
  const timestamps = [];
  $('tr.recentresultitem.selected').each(function() {
    timestamps.push($(this).find('td.recentresult_cell_timestamp').text());
  });

  pywebview.api.recents_upload_collectionimages(timestamps);

  $(this).closest('dialog')[0].close();
}

/**
 * 選択し曲面の記録を全て削除するか確認
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_confirm_deletemusicnotebook(e) {
  if(selected_musicname == null) {
    $('dialog#dialog_message_musicnameselect')[0].showModal();
    return;
  }

  $('dialog#dialog_confirm_deletemusicnotebook')[0].showModal();
}

/**
 * 選択し曲面の記録を全て削除する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_execute_deletemusicnotebook(e) {
  await pywebview.api.delete_musicresult(selected_musicname);

  selected_timestamp = null;

  display_scoreresult();
  clear_playresult();

  $(this).closest('dialog')[0].close();
}

/**
 * 選択した譜面の記録を全て削除するか確認
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_confirm_deletescoreresult(e) {
  if(selected_playmode == null || selected_musicname == null || selected_difficulty == null) {
    $('dialog#dialog_message_scoreselect')[0].showModal();
    return;
  }

  $('dialog#dialog_confirm_deletescoreresult')[0].showModal();
}

/**
 * 選択した譜面の記録を全て削除する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_execute_deletescoreresult(e) {
  await pywebview.api.delete_scoreresult(selected_playmode, selected_musicname, selected_difficulty);

  selected_timestamp = null;
  
  display_scoreresult();
  clear_playresult();

  $(this).closest('dialog')[0].close();
}

/**
 * 選択したタイムスタンプの記録を削除するか確認
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_confirm_deleteplayresult(e) {
  if(selected_timestamp == null) {
    $('dialog#dialog_message_timestampselect')[0].showModal();
    return;
  }

  $('dialog#dialog_confirm_deleteplayresult')[0].showModal();
}

/**
 * 選択したタイムスタンプの記録を削除する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_execute_deleteplayresult(e) {
  await pywebview.api.delete_playresult(selected_playmode, selected_musicname, selected_difficulty, selected_timestamp);

  selected_timestamp = null;

  display_scoreresult();
  clear_playresult();

  $(this).closest('dialog')[0].close();
}

/**
 * 連携投稿のプレイヤー名を変更する
 * @param {ce.Event} e イベントハンドラ
 */
function oninput_discordwebhook_playername(e) {
  pywebview.api.set_playername($('input#text_discordwebhook_playername').val());
}

/**
 * 連携投稿のプレイヤー名を変更する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_discordwebhook_playername(e) {
  pywebview.api.save_playername();
}

/**
 * 絞り込み対象のバージョンを選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_scoreselect_version(e) {
  const version = e.target.value;
  const musicname_pattern = $('input#text_musicname_search').val();

  musicname_search(version, musicname_pattern);
}

/**
 * 絞り込み対象の曲名の文字列を入力する
 * @param {ce.Event} e イベントハンドラ
 */
function oninput_scoreselect_musicname(e) {
  const version = $('select#select_versions').val();
  const musicname_pattern = e.target.value;

  musicname_search(version, musicname_pattern);
}

/**
 * 曲名を選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_musictableitem(e) {
  $('tr.musictableitem.selected').removeClass('selected');
  $(this).addClass('selected');

  display_scoreresult_from_scoresearch();
}

/**
 * プレイモードを選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_scoreresult_playmode(e) {
  display_scoreresult_from_scoresearch();
}

/**
 * 譜面難易度を選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_scoreresult_difficulty(e) {
  display_scoreresult_from_scoresearch();
}

/**
 * 連携投稿の設定を選択する
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_discordwebhookitem(e) {
  $('tr.discordwebhookitem.selected').removeClass('selected');
  $(this).addClass('selected');
}

/**
 * 連携投稿の設定を追加する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_discordwebhook_add(e) {
  operation_disable();

  await pywebview.api.discordwebhook_add();

  operation_enable();

  reload_discordwebhook_settings();
}

/**
 * 連携投稿の設定を更新する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_discordwebhook_update(e) {
  const id = $('tr.discordwebhookitem.selected td.discordwebhook_cell_id').text();

  if(id.length == 0) {
    $('dialog#dialog_message_discordwebhookselect')[0].showModal();
    return;
  }

  operation_disable();

  await pywebview.api.discordwebhook_update(id);

  operation_enable();

  reload_discordwebhook_settings();
}

/**
 * 連携投稿の設定を有効化する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_discordwebhook_activate(e) {
  const id = $('tr.discordwebhookitem.selected td.discordwebhook_cell_id').text();

  if(id.length == 0) {
    $('dialog#dialog_message_discordwebhookselect')[0].showModal();
    return;
  }

  await pywebview.api.discordwebhook_activate(id);

  reload_discordwebhook_settings();
}

/**
 * 連携投稿の設定を無効化する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_discordwebhook_deactivate(e) {
  const id = $('tr.discordwebhookitem.selected td.discordwebhook_cell_id').text();

  if(id.length == 0) {
    $('dialog#dialog_message_discordwebhookselect')[0].showModal();
    return;
  }

  await pywebview.api.discordwebhook_deactivate(id);

  reload_discordwebhook_settings();
}

/**
 * 連携投稿の設定を削除する
 * @param {ce.Event} e イベントハンドラ
 */
async function onclick_discordwebhook_delete(e) {
  const id = $('tr.discordwebhookitem.selected td.discordwebhook_cell_id').text();

  if(id.length == 0) {
    $('dialog#dialog_message_discordwebhookselect')[0].showModal();
    return;
  }

  await pywebview.api.discordwebhook_delete(id);

  reload_discordwebhook_settings();
}

/**
 * ウィンドウの操作を不可にする
 * 
 * 別ウィンドウをモーダルとして開くときに実行する。
 */
function operation_disable() {
  $('body').addClass('unusable');
}

/**
 * ウィンドウの操作を可能にする
 * 
 * モーダルウィンドウを閉じたときに実行する。
 */
function operation_enable() {
  $('body').removeClass('unusable');
}

/**
 * ノーツレーダーのプレイモードを変更する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_notesradar_playmode(e) {
  display_notesradar_total();
  display_notesradar_ranking();
}

/**
 * ノーツレーダーの項目を変更する
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_notesradar_attribute(e) {
  display_notesradar_ranking();
}

/**
 * ノーツレーダーのリスト表示モードを変更する
 * 
 * ノーツレーダー値計算対象の10曲か、点数の上位50譜面を表示するかを切り替える。
 * @param {ce.Event} e イベントハンドラ
 */
function onchange_notesradar_tablemode(e) {
  display_notesradar_ranking();
}

/**
 * タイムスタンプを選択
 * @param {} e 
 */
function onclick_timestampitem(e) {
  $('tr.timestampitem.selected').removeClass('selected');
  $(this).addClass('selected');

  const timestamp = $('tr.timestampitem.selected .timestamp_cell_timestamp').first().text();

  display_playresult(timestamp);
}


/**
 * 最新バージョンが見つかったときの処理を実行する
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_execute_findnewestversionaction(e) {
  pywebview.api.execute_findnewestversionaction();
  $(this).closest('dialog')[0].close();
}

/**
 * インストーラーを起動する
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_execute_openinstaller(e) {
  pywebview.api.open_installer();
}

/**
 * リザルト手帳のサイトを開く
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_execute_openhomepage(e) {
  pywebview.api.open_homepage();
}

/**
 * ダイアログを閉じる
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_button_dialogclose(e) {
  $(this).closest('dialog')[0].close();
}

/**
 * 入力された条件をもとに一致する曲名だけを表示する
 * @param {str} version バージョン名。ALLの場合は全てのバージョンが対象
 * @param {str} musicname_pattern 曲名の条件(部分一致)。なしの場合は全ての曲名が対象
 */
function musicname_search(version, musicname_pattern) {
  // 表示方法を、displayを切り替えるのではなくて要素の全削除と追加のし直しにする
  // 背景色のゼブラが崩れるから
  const version_all = version == 'ALL';
  const musicname_all = musicname_pattern.length == 0;

  let reg = null;
  if(!musicname_all)
    reg = new RegExp(musicname_pattern, 'i');

  $('table#table_musics tr.tableitem').each(function() {
    const version_condition = version_all || $(this).children('td.music_cell_version').text() == version;
    const musicname_condition = musicname_all || reg.test($(this).children('td.music_cell_musicname').text());

    if(version_condition && musicname_condition)
      $(this).removeClass('hidden');
    else
      $(this).addClass('hidden');
  });
}

/**
 * 連携投稿の設定を読み出す
 */
function reload_discordwebhook_settings() {
  pywebview.api.get_discordwebhook_settings().then((values) => {
    refresh_discordwebhook_settings(values);
  });
}

/**
 * スクリーンショットのパスを表示する
 * @param {} path 
 */
function display_screenshot_filepath(path) {
  $('span#path_screenshot').text(path);
}

/**
 * 連携投稿の設定を再表示する
 * @param {*} settings 
 */
function refresh_discordwebhook_settings(settings) {
  $('tr.discordwebhookitem').remove();

  Object.keys(settings).forEach(function(key) {
    const target = settings[key];

    const tr = $('<tr>');
    tr.addClass('tableitem discordwebhookitem');

    const td_id = $('<td>').text(key);
    td_id.addClass('discordwebhook_cell_id');
    tr.append(td_id);

    const td_name = $('<td>').text(target['name']);
    td_name.addClass('discordwebhook_cell_name');
    tr.append(td_name);

    const td_mode = $('<td>');
    if(target['mode'] == 'battle') td_mode.text('M');
    if(target['mode'] == 'score') td_mode.text('SC');
    if(target['mode'] == 'misscount') td_mode.text('MS');
    td_mode.addClass('center discordwebhook_cell_mode');
    tr.append(td_mode);

    const td_musicname = $('<td>');
    if(target['mode'] != 'battle') td_musicname.text(target['targetscore']['musicname']);
    td_musicname.addClass('discordwebhook_cell_musicname');
    tr.append(td_musicname);

    const td_state = $('<td>');
    if(target['state'] == 'active') td_state.text('*');
    if(target['state'] == 'error') td_state.text('--');
    td_state.addClass('center discordwebhook_cell_state');
    tr.append(td_state);

    const td_best = $('<td>');
    if(target['mode'] == 'battle')
      td_best.text('---');
    else
      td_best.text(target['mybest']);
    td_best.addClass('center discordwebhook_cell_best');
    tr.append(td_best);

    tr.on('click', onclick_discordwebhookitem);
    $('#table_discordwebhooks').append(tr);
  });
}

/**
 * 譜面のベスト記録の表示をすべてクリアする
 */
function clear_bests() {
  display_best_cleartype(null);
  display_best_djlevel(null);
  display_best_score(null);
  display_best_misscount(null);
}

function display_best_cleartype(values) {
  if(values != null) {
    if(values.value != null)
      $('#best_cleartype').text(values.value);
    else
      $('#best_cleartype').text('');

    if(values.timestamp != null) {
      const t = values.timestamp;
      $('#best_cleartype_timestamp').text(`${t.slice(0, 4)}年${t.slice(4, 6)}月${t.slice(6, 8)}日`);
    }
    else {
      $('#best_cleartype_timestamp').text('?????');
    }

    if(values.options != null) {
      if(values.options.arrange != null)
        $('#best_cleartype_option').text(values.options.arrange);
      else
        $('#best_cleartype_option').text('---------');
    }
    else {
      $('#best_cleartype_option').text('?????');
    }
  }
  else {
    $('#best_cleartype').text('');
    $('#best_cleartype_option').text('');
    $('#best_cleartype_timestamp').text('');
  }
}

function display_best_djlevel(values) {
  if(values != null) {
    if(values.value != null)
      $('#best_djlevel').text(values.value);
    else
      $('#best_djlevel').text('');

    if(values.timestamp != null) {
      const t = values.timestamp;
      $('#best_djlevel_timestamp').text(`${t.slice(0, 4)}年${t.slice(4, 6)}月${t.slice(6, 8)}日`);
    }
    else {
      $('#best_djlevel_timestamp').text('?????');
    }

    if(values.options != null) {
      if(values.options.arrange != null)
        $('#best_djlevel_option').text(values.options.arrange);
      else
        $('#best_djlevel_option').text('---------');
    }
    else {
      $('#best_djlevel_option').text('?????');
    }
  }
  else {
    $('#best_djlevel').text('');
    $('#best_djlevel_option').text('');
    $('#best_djlevel_timestamp').text('');
  }
}

function display_best_score(values) {
  if(values != null) {
    if(values.value != null)
      $('#best_score').text(values.value);
    else
      $('#best_score').text('');

    if(values.timestamp != null) {
      const t = values.timestamp;
      $('#best_score_timestamp').text(`${t.slice(0, 4)}年${t.slice(4, 6)}月${t.slice(6, 8)}日`);
    }
    else {
      $('#best_score_timestamp').text('?????');
    }

    if(values.options != null) {
      if(values.options.arrange != null)
        $('#best_score_option').text(values.options.arrange);
      else
        $('#best_score_option').text('---------');
    }
    else {
      $('#best_score_option').text('?????');
    }
  }
  else {
    $('#best_score').text('');
    $('#best_score_option').text('');
    $('#best_score_timestamp').text('');
  }
}

function display_best_misscount(values) {
  if(values != null) {
    if(values.value != null)
      $('#best_misscount').text(values.value);
    else
      $('#best_misscount').text('');

    if(values.timestamp != null) {
      const t = values.timestamp;
      $('#best_misscount_timestamp').text(`${t.slice(0, 4)}年${t.slice(4, 6)}月${t.slice(6, 8)}日`);
    }
    else {
      $('#best_misscount_timestamp').text('?????');
    }

    if(values.options != null) {
      if(values.options.arrange != null)
        $('#best_misscount_option').text(values.options.arrange);
      else
        $('#best_misscount_option').text('---------');
    }
    else {
      $('#best_misscount_option').text('?????');
    }
  }
  else {
    $('#best_misscount').text('');
    $('#best_misscount_option').text('');
    $('#best_misscount_timestamp').text('');
  }
}

/**
 * ノーツレーダーの更新
 * 
 * 上位から呼び出される。
 */
function update_notesradar() {
  draw_notesradar();
  display_notesradar_total();
  display_notesradar_ranking();
}

async function draw_summary() {
  if(setting == null) return;

  const values = await pywebview.api.get_summaryvalues();

  if(values == null) return;

  const blob = await drawer_summary.draw(values, setting.summary_countmethod_only);
  const url = URL.createObjectURL(blob)

  update_imageurl('summary', 'image_summary', url);

  reader_summary.abort();
  reader_summary.readAsDataURL(blob);
}

/**
 * ノーツレーダー画像を更新する
 * 
 * 初期処理完了時のほか、更新時にPythonから呼び出される。
 */
async function draw_notesradar() {
  const values = await pywebview.api.get_notesradar_chartvalues();

  const blob = await drawer_notesradar.draw(values);
  const url = URL.createObjectURL(blob)

  update_imageurl('notesradar', 'image_chartnotesradar', url);

  reader_notesradar.abort();
  reader_notesradar.readAsDataURL(blob);
}

function update_imageurl(name, tagid, url) {
  if(imageurls[name] != null)
    URL.revokeObjectURL(imageurls[name]);

  imageurls[name] = url;
  $(`img#${tagid}`).attr('src', url);
}

function onloadend_imagenothingimage(e) {
  if(e.target.result == null) return;

  pywebview.api.upload_imagenothingimage(e.target.result.split(',')[1]);
}

function onloadend_simpletextimage(e) {
  if(e.target.result == null) return;

  pywebview.api.upload_informationimage(e.target.result.split(',')[1]);
}

function onloadend_informationimage(e) {
  if(e.target.result == null) return;

  pywebview.api.upload_informationimage(e.target.result.split(',')[1]);
}

function onloadend_summaryimage(e) {
  if(e.target.result == null) return;

  pywebview.api.upload_summaryimage(e.target.result.split(',')[1]);
}

function onloadend_notesradarimage(e) {
  if(e.target.result == null) return;

  pywebview.api.upload_notesradarimage(e.target.result.split(',')[1]);
}

function onloadend_scoreinformationimage(e) {
  if(e.target.result == null) return;

  pywebview.api.upload_scoreinformationimage(
    e.target.result.split(',')[1],
    selected_playmode,
    selected_musicname,
    selected_difficulty
  );
}

function onloadend_scoregraphimage(e) {
  if(e.target.result == null) return;

  pywebview.api.upload_scoregraphimage(
    e.target.result.split(',')[1],
    selected_playmode,
    selected_musicname,
    selected_difficulty
  );
}

function onerror_filereader(e) {
  console.log('error', e);
}

function onabort_filereader(e) {
  console.log('abort', e);
}

function display_notesradar_total() {
  const selected = $('input[name="notesradar_playmode"]:checked').attr('id');
  const playmode = $(`label[for=${selected}]`).text();
  if(playmode.length > 0) {
    pywebview.api.get_notesradar_total(playmode).then((value) => {
      $('span#notesradar_total').text(Math.floor(value * 100) / 100);
    });
  }
}

function display_notesradar_ranking() {
  const selected_playmode = $('input[name="notesradar_playmode"]:checked').attr('id');
  const selected_tablemode = $('input[name="notesradar_tablemode"]:checked').attr('id');

  if(selected_playmode == null || selected_tablemode == null) return;

  const playmode = $(`label[for=${selected_playmode}]`).text();
  const attribute = $('select#select_notesradar_attributes').val();
  const tablemode = selected_tablemode.match(/(?<=radio_notesradar_tablemode_)(.*)/)[0];

  if(playmode.length > 0 && attribute.length > 0 && tablemode.length > 0) {
    pywebview.api.get_notesradar_ranking(playmode, attribute, tablemode).then((values) => {
      $('table#table_notesradar_ranking tr.notesradaritem').remove();

      if(values == null) return;

      values.forEach((value) => {
        const tr = $('<tr>');
        tr.addClass('tableitem notesradaritem');
    
        const td_latest = $('<td>').text(value['rank']);
        td_latest.addClass('right notesradar_cell_rank');
        tr.append(td_latest);
    
        const td_saved = $('<td>').text(value['musicname']);
        td_saved.addClass('notesradar_cell_musicname');
        tr.append(td_saved);
    
        const td_filtered = $('<td>').text(value['difficulty'][0]);
        td_filtered.addClass('center notesradar_cell_difficulty');
        tr.append(td_filtered);
    
        const td_timestamp = $('<td>').text(value['value'].toFixed(2));
        td_timestamp.addClass('right notesradar_cell_value');
        tr.append(td_timestamp);
    
        $('table#table_notesradar_ranking').append(tr);
      });
    });
  }
}

/**
 * 連携投稿タブ内のログを追加
 * @param {string} text 
 */
function discordwebhook_append_logs(texts) {
  texts.forEach((text) => {
    const li = $('<li>').text(text);
    $('ul#list_discordwebhook_logs').append(li);
  });

  const targetscroll = $('div#scroll_discordwebhook_logs');
  targetscroll.scrollTop(targetscroll[0].scrollHeight);
}

async function activescreenshot(filepath) {
  const encodedimage = await pywebview.api.get_activescreenshot();
  display_encodedimage(encodedimage, 'image_screenshot');
  switch_displaytab('main', 'screenshot');

  display_screenshot_filepath(filepath);
}

async function musicselect_upload() {
  const encodedimage = await pywebview.api.get_activescreenshot();
  display_encodedimage(encodedimage, 'image_screenshot');
  switch_displaytab('main', 'screenshot');
}

function display_encodedimage(encodedimage, tagid) {
  if(encodedimage != null)
    $(`img#${tagid}`).attr('src', `data:image/png;base64,${encodedimage}`);
  else
    $(`img#${tagid}`).attr('src', imageurls['imagenothing']);
}

/**
 * メインタブ内のログを追加
 * @param {string} text 
 */
function append_log(text) {
  const li = $('<li>').text(text);
  $('ul#logs').append(li);

  if($('ul#logs').children().length > 1000) $('ul#logs').children().first().remove();

  const targetscroll = $('div#scroll_logs');
  targetscroll.scrollTop(targetscroll[0].scrollHeight);
}

function draw_text(ctx, text, x, y, args) {
  ctx.save();

  ctx.fillStyle = args.textcolor;
  ctx.shadowColor = args.shadowcolor;
  ctx.shadowBlur = args.fontsize / 5;
  ctx.shadowOffsetX = args.fontsize / 20;
  ctx.shadowOffsetY = args.fontsize / 20;
  ctx.strokeStyle = args.shadowcolor;
  ctx.lineWidth = args.fontsize / 20;
  
  ctx.strokeText(text, x, y, args.maxwidth);
  ctx.fillText(text, x, y, args.maxwidth);

  ctx.restore();
}