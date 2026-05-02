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
  $('input#check_onlyfullcombo').on('change', display_keytable);
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

  const difficulties = JSON.parse(await webui.get_difficulties());
  for(const difficulty of difficulties) {
    $('select#select_difficulty').append($('<option>')
      .val(difficulty)
      .text(difficulty)
    );
  }

  const levels = JSON.parse(await webui.get_levels());
  for(const level of levels) {
    $('select#select_level').append($('<option>')
      .val(level)
      .text(level)
    );
  }

  const graphtypes = JSON.parse(await webui.get_graphtypes());
  for(const graphtype of graphtypes) {
    $('select#select_graphtype').append($('<option>')
      .val(graphtype)
      .text(graphtype)
    );
  }

  const options = JSON.parse(await webui.get_options());
  for(const option of options.arrange) {
    $('select#select_optionarrange').append($('<option>')
      .val(option)
      .text(option)
    );
  }
  for(const option of options.arrange_dp) {
    $('select#select_optionarrange1p').append($('<option>')
      .val(option)
      .text(option)
    );
    $('select#select_optionarrange2p').append($('<option>')
      .val(option)
      .text(option)
    );
  }
  for(const option of options.arrange_sync) {
    $('select#select_optionarrangesync').append($('<option>')
      .val(option)
      .text(option)
    );
  }
  for(const option of options.flip) {
    $('select#select_optionflip').append($('<option>')
      .val(option)
      .text(option)
    );
  }
  for(const option of options.assist) {
    $('select#select_optionassist').append($('<option>')
      .val(option)
      .text(option)
    );
  }

  const cleartypes = JSON.parse(await webui.get_cleartypes());
  for(const cleartype of cleartypes) {
    $('select#select_cleartypebest').append($('<option>')
      .val(cleartype)
      .text(cleartype)
    );

    $('select#select_cleartypecurrent').append($('<option>')
      .val(cleartype)
      .text(cleartype)
    );
  }

  const djlevels = JSON.parse(await webui.get_djlevels());
  for(const djlevel of djlevels) {
    $('select#select_djlevelbest').append($('<option>')
      .val(djlevel)
      .text(djlevel)
    );

    $('select#select_djlevelcurrent').append($('<option>')
      .val(djlevel)
      .text(djlevel)
    );
  }

  const graphtargets = JSON.parse(await webui.get_graphtargets());
  for(const graphtarget of graphtargets) {
    $('select#select_graphtarget').append($('<option>')
      .val(graphtarget)
      .text(graphtarget)
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

  const images = JSON.parse(await webui.get_images(targetkey));
  if(images !== null) {
    if(images.informations !== null)
      $('img#image_informations').attr('src', `data:image/png;base64,${images.informations}`);
    else
      $('img#image_informations').attr('src', null);
    if(images.details !== null)
      $('img#image_details').attr('src', `data:image/png;base64,${images.details}`);
    else
      $('img#image_details').attr('src', null);
  }

  const labels = JSON.parse(await webui.get_labels(targetkey));
  if(labels !== null) {
    if(images !== null && images.informations !== null) {
      $('fieldset#fieldset_labelinformations').prop('disabled', false);

      $('select#select_playmode').val(labels.informations.playmode);
      $('select#select_difficulty').val(labels.informations.difficulty);
      $('select#select_level').val(labels.informations.level);
      $('input#text_notes').val(labels.informations.notes);
      $('input#text_songname').val(labels.informations.songname);

      $('input#check_informationsignore').prop('checked', labels.informations.ignore == true);
    }
    else {
      $('fieldset#fieldset_labelinformations').prop('disabled', true);

      clearinput_informations();
    }

    if(images !== null && images.details !== null) {
      $('fieldset#fieldset_labeldetails').prop('disabled', false);
      
      $('select#select_graphtype').val(labels.details.graphtype);

      $('input#check_optionbattle').prop('checked', labels.details.option_battle == true);
      $('input#check_optionallscratch').prop('checked', labels.details.option_allscratch == true);
      $('input#check_optionregularspeed').prop('checked', labels.details.option_regularspeed == true);

      $('select#select_optionarrange').val(labels.details.option_arrange);

      if(labels.details.option_arrange_dp !== null) {
        const parts = labels.details.option_arrange_dp.split('/');
        $('select#select_optionarrange1p').val(parts[0]);
        $('select#select_optionarrange2p').val(parts[1]);
      }
      else {
        $('select#select_optionarrange1p').val(null);
        $('select#select_optionarrange2p').val(null);
      }

      $('select#select_optionarrangesync').val(labels.details.option_arrange_sync);

      $('select#select_optionflip').val(labels.details.option_flip);
      $('select#select_optionassist').val(labels.details.option_assist);

      $('select#select_cleartypebest').val(labels.details.cleartype_best);
      $('select#select_djlevelbest').val(labels.details.djlevel_best);
      $('input#text_scorebest').val(labels.details.score_best);
      $('input#text_misscountbest').val(labels.details.misscount_best);
      $('select#select_cleartypecurrent').val(labels.details.cleartype_current);
      $('select#select_djlevelcurrent').val(labels.details.djlevel_current);
      $('input#text_scorecurrent').val(labels.details.score_current);
      $('input#text_misscountcurrent').val(labels.details.misscount_current);
      $('input#check_cleartypenew').prop('checked', labels.details.cleartype_new == true);
      $('input#check_djlevelnew').prop('checked', labels.details.djlevel_new == true);
      $('input#check_scorenew').prop('checked', labels.details.score_new == true);
      $('input#check_misscountnew').prop('checked', labels.details.misscount_new == true);

      $('select#select_graphtarget').val(labels.details.graphtarget);

      $('input#check_detailsignore').prop('checked', labels.details.ignore == true);
    }
    else {
      $('fieldset#fieldset_labeldetails').prop('disabled', true);

      clearinput_details();
    }
  }
  else {
    clearinput_informations();
    clearinput_details();
  }

  recognitionresult = JSON.parse(await webui.get_recognitionresult(targetkey));
  if(recognitionresult !== null && recognitionresult.informations !== null) {
    $('span#text_resultplaymode').text(recognitionresult.informations.playmode);
    $('span#text_resultdifficulty').text(recognitionresult.informations.difficulty);
    $('span#text_resultlevel').text(recognitionresult.informations.level);
    $('span#text_resultnotes').text(recognitionresult.informations.notes);
    $('span#text_resultsongname').text(recognitionresult.informations.songname);
  }
  else {
    $('span#text_resultplaymode').empty();
    $('span#text_resultdifficulty').empty();
    $('span#text_resultlevel').empty();
    $('span#text_resultnotes').empty();
    $('span#text_resultsongname').empty();
  }

  if(recognitionresult !== null && recognitionresult.details !== null) {
    $('span#text_resultgraphtype').text(recognitionresult.details.graphtype);

    if(recognitionresult.details.options) {
      $('span#text_resultoptionbattle').text(recognitionresult.details.options.battle ? 'BATTLE' : '');
      $('span#text_resultoptionallscratch').text(recognitionresult.details.options.allscratch ? 'ALL-SCR' : '');
      $('span#text_resultoptionregularspeed').text(recognitionresult.details.options.regularspeed ? 'REGUL-SPEED' : '');
      $('span#text_resultoptionarrange').text(recognitionresult.details.options.arrange);
      $('span#text_resultoptionflip').text(recognitionresult.details.options.flip);
      $('span#text_resultoptionassist').text(recognitionresult.details.options.assist);
    }
    else {
      clear_options();
    }

    if(recognitionresult.details.cleartype) {
      $('span#text_resultcleartypebest').text(recognitionresult.details.cleartype.best);
      $('span#text_resultcleartypecurrent').text(recognitionresult.details.cleartype.current);
      $('span#text_resultcleartypenew').text(recognitionresult.details.cleartype.is_new ? 'NEW': '');
    }
    else {
      clear_cleartype();
    }
    
    if(recognitionresult.details.djlevel) {
      $('span#text_resultdjlevelbest').text(recognitionresult.details.djlevel.best);
      $('span#text_resultdjlevelcurrent').text(recognitionresult.details.djlevel.current);
      $('span#text_resultdjlevelnew').text(recognitionresult.details.djlevel.is_new ? 'NEW': '');
    }
    else {
      clear_djlevel();
    }
    
    if(recognitionresult.details.score) {
      $('span#text_resultscorebest').text(recognitionresult.details.score.best);
      $('span#text_resultscorecurrent').text(recognitionresult.details.score.current);
      $('span#text_resultscorenew').text(recognitionresult.details.score.is_new ? 'NEW': '');
    }
    else {
      clear_score();
    }
    
    if(recognitionresult.details.misscount) {
      $('span#text_resultmisscountbest').text(recognitionresult.details.misscount.best);
      $('span#text_resultmisscountcurrent').text(recognitionresult.details.misscount.current);
      $('span#text_resultmisscountnew').text(recognitionresult.details.misscount.is_new ? 'NEW': '');
    }
    else {
      clear_misscount();
    }

    $('span#text_resultgraphtarget').text(recognitionresult.details.graphtarget);
  }
  else {
    $('span#text_resultgraphtype').empty();
    clear_options();
    clear_cleartype();
    clear_djlevel();
    clear_score();
    clear_misscount();
    $('span#text_resultgraphtarget').empty();
  }
}

function clear_options() {
  $('span#text_resultoptionbattle').empty();
  $('span#text_resultoptionallscratch').empty();
  $('span#text_resultoptionregularspeed').empty();
  $('span#text_resultoptionarrange').empty();
  $('span#text_resultoptionflip').empty();
  $('span#text_resultoptionassist').empty();
}

function clear_cleartype() {
  $('span#text_resultcleartypebest').empty();
  $('span#text_resultcleartypecurrent').empty();
  $('span#text_resultcleartypenew').empty();
}

function clear_djlevel() {
  $('span#text_resultdjlevelbest').empty();
  $('span#text_resultdjlevelcurrent').empty();
  $('span#text_resultdjlevelnew').empty();
}

function clear_score() {
  $('span#text_resultscorebest').empty();
  $('span#text_resultscorecurrent').empty();
  $('span#text_resultscorenew').empty();
}

function clear_misscount() {
  $('span#text_resultmisscountbest').empty();
  $('span#text_resultmisscountcurrent').empty();
  $('span#text_resultmisscountnew').empty();
}

function clearinput_informations() {
  $('select#select_playmode').val(null);
  $('select#select_difficulty').val(null);
  $('select#select_level').val(null);
  $('input#text_notes').val(null);
  $('input#text_songname').val(null);
}

function clearinput_details() {
  $('select#select_graphtype').val(null);
  $('input#check_optionbattle').prop('checked', false);
  $('input#check_optionallscratch').prop('checked', false);
  $('input#check_optionregularspeed').prop('checked', false);
  $('select#select_optionarrange').val(null);
  $('select#select_optionarrange1p').val(null);
  $('select#select_optionarrange2p').val(null);
  $('select#select_optionarrangesync').val(null);
  $('select#select_optionflip').val(null);
  $('select#select_optionassist').val(null);
  $('select#select_cleartypebest').val(null);
  $('select#select_djlevelbest').val(null);
  $('input#text_scorebest').val(null);
  $('input#text_misscountbest').val(null);
  $('select#select_cleartypecurrent').val(null);
  $('select#select_djlevelcurrent').val(null);
  $('input#text_scorecurrent').val(null);
  $('input#text_misscountcurrent').val(null);
  $('select#select_cleartypenew').val(null);
  $('select#select_djlevelnew').val(null);
  $('input#text_scorenew').val(null);
  $('input#text_misscountnew').val(null);
  $('select#select_graphtarget').val(null);
}

/**
 * ラベルの上書きを実行
 * @param {} e
 */
async function onclick_labeloverwrite(e) {
  const targetkey = $('tr.keyitem.selected .cell_key').first().text();

  let informations = null;
  if(!$('fieldset#fieldset_labelinformations').prop('disabled')) {
    informations = {
      'playmode': $('select#select_playmode').val(),
      'difficulty': $('select#select_difficulty').val(),
      'level': $('select#select_level').val(),
      'notes': $('input#text_notes').val(),
      'songname': $('input#text_songname').val(),
    }

    if($('input#check_informationsignore').prop('checked'))
      informations.ignore = true;
  }

  let details = null;
  if(!$('fieldset#fieldset_labeldetails').prop('disabled')) {
    details = {
      'graphtype': $('select#select_graphtype').val(),
      'option_battle': $('input#check_optionbattle').prop('checked'),
      'option_allscratch': $('input#check_optionallscratch').prop('checked'),
      'option_regularspeed': $('input#check_optionregularspeed').prop('checked'),
      'option_arrange': $('select#select_optionarrange').val(),
      'option_arrange_dp': `${$('select#select_optionarrange1p').val()}/${$('select#select_optionarrange2p').val()}`,
      'option_arrange_sync': $('select#select_optionarrangesync').val(),
      'option_flip': $('select#select_optionflip').val(),
      'option_assist': $('select#select_optionassist').val(),
      'cleartype_best': $('select#select_cleartypebest').val(),
      'cleartype_current': $('select#select_cleartypecurrent').val(),
      'cleartype_new': $('input#check_cleartypenew').prop('checked'),
      'djlevel_best': $('select#select_djlevelbest').val(),
      'djlevel_current': $('select#select_djlevelcurrent').val(),
      'djlevel_new': $('input#check_djlevelnew').prop('checked'),
      'score_best': $('input#text_scorebest').val(),
      'score_current': $('input#text_scorecurrent').val(),
      'score_new': $('input#check_scorenew').prop('checked'),
      'misscount_best': $('input#text_misscountbest').val(),
      'misscount_current': $('input#text_misscountcurrent').val(),
      'misscount_new': $('input#check_misscountnew').prop('checked'),
      'graphtarget': $('select#select_graphtarget').val(),
    }

    if($('input#check_detailsignore').prop('checked'))
      details.ignore = true;
  }

  values = {
    'informations': informations,
    'details': details,
  }

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
  if(recognitionresult !== null && recognitionresult.informations !== null) {
    $('fieldset#fieldset_labelinformations').prop('disabled', false);

    $('select#select_playmode').val(recognitionresult.informations.playmode);
    $('select#select_difficulty').val(recognitionresult.informations.difficulty);
    $('select#select_level').val(recognitionresult.informations.level);
    $('input#text_notes').val(recognitionresult.informations.notes);
    $('input#text_songname').val(recognitionresult.informations.songname);

    $('input#text_songname')
      .focus()
      .select();
  }
  else {
    $('fieldset#fieldset_labelinformations').prop('disabled', true);

    $('select#select_playmode').val(null);
    $('select#select_difficulty').val(null);
    $('select#select_level').val(null);
    $('input#text_notes').val(null);
    $('input#text_songname').val(null);
  }

  if(recognitionresult !== null && recognitionresult.details !== null) {
    $('fieldset#fieldset_labeldetails').prop('disabled', false);
    
    if(recognitionresult.details.options) {
      $('select#select_graphtype').val(recognitionresult.details.graphtype);

      $('input#check_optionbattle').prop('checked', recognitionresult.details.options.battle);
      $('input#check_optionallscratch').prop('checked', recognitionresult.details.options.allscratch);
      $('input#check_optionregularspeed').prop('checked', recognitionresult.details.options.regularspeed);

      $('select#select_optionarrange').val(recognitionresult.details.options.arrange);

      if(recognitionresult.details.options.arrange !== null && recognitionresult.details.options.arrange.includes('/')) {
        const parts = recognitionresult.details.optionarrange.split('/');
        $('select#select_optionarrange1p').val(parts[0]);
        $('select#select_optionarrange2p').val(parts[1]);
      }
      else {
        $('select#select_optionarrange1p').val(null);
        $('select#select_optionarrange2p').val(null);
      }

      $('select#select_optionarrangesync').val(recognitionresult.details.options.arrange);

      $('select#select_optionflip').val(recognitionresult.details.options.flip);
      $('select#select_optionassist').val(recognitionresult.details.options.assist);
    }
    else {
      $('input#check_optionbattle').prop('checked', false);
      $('input#check_optionallscratch').prop('checked', false);
      $('input#check_optionregularspeed').prop('checked', false);
      $('select#select_optionarrange').val(null);
      $('select#select_optionarrange1p').val(null);
      $('select#select_optionarrange2p').val(null);
      $('select#select_optionarrangesync').val(null);
      $('select#select_optionflip').val(null);
      $('select#select_optionassist').val(null);
    }

    if(recognitionresult.details.cleartype) {
      $('select#select_cleartypebest').val(recognitionresult.details.cleartype.best);
      $('select#select_cleartypecurrent').val(recognitionresult.details.cleartype.current);
      $('input#check_cleartypenew').prop('checked', recognitionresult.details.cleartype.is_new);
    }
    else {
      $('select#select_cleartypebest').val(null);
      $('select#select_cleartypecurrent').val(null);
      $('select#select_cleartypenew').val(null);
    }

    if(recognitionresult.details.djlevel) {
      $('select#select_djlevelbest').val(recognitionresult.details.djlevel.best);
      $('select#select_djlevelcurrent').val(recognitionresult.details.djlevel.current);
      $('input#check_djlevelnew').prop('checked', recognitionresult.details.djlevel.is_new);
    }
    else {
      $('select#select_djlevelbest').val(null);
      $('select#select_djlevelcurrent').val(null);
      $('select#select_djlevelnew').val(null);
    }

    if(recognitionresult.details.score) {
      $('input#text_scorebest').val(recognitionresult.details.score.best);
      $('input#text_scorecurrent').val(recognitionresult.details.score.current);
      $('input#check_scorenew').prop('checked', recognitionresult.details.score.is_new);
    }
    else {
      $('input#text_scorebest').val(null);
      $('input#text_scorecurrent').val(null);
      $('input#text_scorenew').val(null);
    }

    if(recognitionresult.details.misscount) {
      $('input#text_misscountbest').val(recognitionresult.details.misscount.best);
      $('input#text_misscountcurrent').val(recognitionresult.details.misscount.current);
      $('input#check_misscountnew').prop('checked', recognitionresult.details.misscount.is_new);
    }
    else {
      $('input#text_misscountbest').val(null);
      $('input#text_misscountcurrent').val(null);
      $('input#text_misscountnew').val(null);
    }

    $('select#select_graphtarget').val(recognitionresult.details.graphtarget);
  }
  else {
    $('fieldset#fieldset_labeldetails').prop('disabled', true);

    $('select#select_graphtype').val(null);
    $('input#check_optionbattle').prop('checked', false);
    $('input#check_optionallscratch').prop('checked', false);
    $('input#check_optionregularspeed').prop('checked', false);
    $('select#select_optionarrange').val(null);
    $('select#select_optionarrange1p').val(null);
    $('select#select_optionarrange2p').val(null);
    $('select#select_optionarrangesync').val(null);
    $('select#select_optionflip').val(null);
    $('select#select_optionassist').val(null);
    $('select#select_cleartypebest').val(null);
    $('select#select_cleartypecurrent').val(null);
    $('select#select_cleartypenew').val(null);
    $('select#select_djlevelbest').val(null);
    $('select#select_djlevelcurrent').val(null);
    $('select#select_djlevelnew').val(null);
    $('input#text_scorebest').val(null);
    $('input#text_scorecurrent').val(null);
    $('input#text_scorenew').val(null);
    $('input#text_misscountbest').val(null);
    $('input#text_misscountcurrent').val(null);
    $('input#text_misscountnew').val(null);
    $('select#select_graphtarget').val(null);
  }
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
  const only_fullcombo = $('input#check_onlyfullcombo').prop('checked');
  const only_ignore = $('input#check_onlyignore').prop('checked');
  const songnamefilter = $('input#text_songnamefilter').val();
  const keyfilter = $('input#text_keyfilter').val();

  keys = JSON.parse(await webui.get_collectionkeys(JSON.stringify({
    'only_notannotation': only_notannotation,
    'only_undefinedsongname': only_undefinedsongname,
    'only_fullcombo': only_fullcombo,
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
