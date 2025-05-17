const csssetting_default  = {
  'recent': {
      'size': '46',
      'color': '#808080',
      'shadow-color': '#000000',
      'NORMAL': '#157aea',
      'HYPER': '#eaea15',
      'ANOTHER': '#ea1515',
      'BEGINNER': '#15ea25',
      'LEGGENDARIA': '#af20b0',
      'overviews': {
          'played_count': {
              'display': true,
              'color': '#c0c0ff'
          },
          'score': {
              'display': false,
              'color': '#c0c0ff'
          },
          'misscount': {
              'display': false,
              'color': '#c0c0ff'
          },
          'updated_score': {
              'display': false,
              'color': '#c0c0ff'
          },
          'updated_misscount': {
              'display': false,
              'color': '#c0c0ff'
          },
          'clear': {
              'display': false,
              'color': '#c0c0ff'
          },
          'failed': {
              'display': false,
              'color': '#c0c0ff'
          },
      },
  },
  'summary': {
      'color': '#808080',
      'shadow-color': '#000000',
      'date color': '#c0c0ff',
      'SP': {
          'checked': true,
          'difficulties': {
              'checked': ['ANOTHER'],
              'clear_types': [],
              'dj_levels': ['A', 'AA', 'AAA']
          },
          'levels': {
              'checked': [],
              'clear_types': [],
              'dj_levels': []
          }
      },
      'DP': {
          'checked': true,
          'difficulties': {
              'checked': ['ANOTHER'],
              'clear_types': [],
              'dj_levels': ['A', 'AA', 'AAA']
          },
          'levels': {
              'checked': [],
              'clear_types': [],
              'dj_levels': []
          },
      },
  },
};

playmodes = null;
difficulties = null;
levels = null;
cleartypes = null;
dljevels = null;

csssetting = null;

$(function() {
  $('button.select_tabpage').on('click', onclick_tab);

  $('button#clipboardcopy_exportpath').on('click', onclick_clipboardcopy_exportpath);

  $('input.input_color').on('input', oninput_inputcolor);

  $('input[type="text"].recent').on('input', oninput_recent);
  $('input[type="checkbox"].recent').on('click', onclick_recent);

  $('input[type="text"].summary').on('input', oninput_summary);
  $('input.summaryplaymodes').on('click', onclick_summaryplaymodes);
  $('input[type="checkbox"].summary').on('click', onclick_summary);

  $('button#button_output_csv').on('click', onclick_output_csv);
  $('button#button_confirm_clearrecent').on('click', onclick_confirm_clearrecent);
  $('button#button_clipboardcopy_css').on('click', onclick_clipboardcopy_css);

  $('button#button_execute_clearrecent').on('click', onclick_execute_clearrecent);

  $('button.dialogclose').on('click', onclick_button_dialogclose);

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
  const exportdirpath = await pywebview.api.get_exportdirpath();
  $('div#exportpath').text(exportdirpath);

  playmodes = await pywebview.api.get_playmodes();
  difficulties = await pywebview.api.get_difficulties();
  levels = await pywebview.api.get_levels();
  cleartypes = await pywebview.api.get_cleartypes();
  djlevels = await pywebview.api.get_djlevels();

  csssetting = await pywebview.api.get_csssetting();
  if(csssetting == null) csssetting = csssetting_default;

  $('input#text_recent_textsize').val(csssetting.recent['size']);

  $('input#text_recent_textcolor').val(csssetting.recent['color']);
  $(`div#colorblock_recent_textcolor`).css('background-color', csssetting.recent['color']);

  $('input#text_recent_shadowcolor').val(csssetting.recent['shadow-color']);
  $(`div#colorblock_recent_shadowcolor`).css('background-color', csssetting.recent['shadow-color']);

  difficulties.forEach(difficulty => {
    $(`input#text_recent_${difficulty}_color`).val(csssetting.recent[difficulty]);
    $(`div#colorblock_recent_${difficulty}_color`).css('background-color', csssetting.recent[difficulty]);
  });

  Object.keys(csssetting.recent['overviews']).forEach(key => {
    $(`input#check_recent_${key}_display`).prop('checked', csssetting.recent['overviews'][key]['display']);
    $(`input#text_recent_${key}_color`).val(csssetting.recent['overviews'][key]['color']);
    $(`div#colorblock_recent_${key}_color`).css('background-color', csssetting.recent['overviews'][key]['color']);
  });

  $('input#text_summary_textcolor').val(csssetting.summary['color']);
  $(`div#colorblock_summary_textcolor`).css('background-color', csssetting.summary['color']);

  $('input#text_summary_shadowcolor').val(csssetting.summary['shadow-color']);
  $(`div#colorblock_summary_shadowcolor`).css('background-color', csssetting.summary['shadow-color']);

  $('input#text_summary_datecolor').val(csssetting.summary['date color']);
  $(`div#colorblock_summary_datecolor`).css('background-color', csssetting.summary['date color']);

  playmodes.forEach(playmode => {
    $(`input.${playmode}`).prop('disabled', !csssetting.summary[playmode]['checked']);

    if(csssetting.summary[playmode]['checked']) {
      $(`input#check_summary_${playmode}`).prop('checked', true);
    }

    ['difficulties', 'levels'].forEach(key => {
      csssetting.summary[playmode][key]['checked'].forEach(value => {
        $(`input#check_summary_${playmode}_${value}`).prop('checked', true);
      });
  
      csssetting.summary[playmode][key]['clear_types'].forEach(cleartype => {
        const replaced_cleartype = cleartype.replace(' ', '--');
        $(`input#check_summary_${playmode}_${key}_${replaced_cleartype}`).prop('checked', true);
      });
  
      csssetting.summary[playmode][key]['dj_levels'].forEach(djlevel => {
        $(`input#check_summary_${playmode}_${key}_${djlevel}`).prop('checked', true);
      });
    });
  });

  switch_displaytab('manual');
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
  const tabname = splitted[0]

  switch_displaytab(tabname);

  if(tabname == 'recent')
    generatecss_recent();
  if(tabname == 'summary')
    generatecss_summary();
}

/**
 * エクスポートフォルダのパスをクリップボードにコピー
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_clipboardcopy_exportpath(e) {
  navigator.clipboard.writeText($('div#exportpath').text());
}

/**
 * 色設定を変更した
 * @param {ce.Event} e イベントハンドラ
 */
function oninput_inputcolor(e) {
  const id = $(this).attr('id');
  const targetid = id.replace('text', 'colorblock');
  $(`div#${targetid}`).css('background-color', $(this).val());
}

/**
 * 最近のデータの設定のテキスト入力を変更した
 * @param {ce.Event} e イベントハンドラ
 */
function oninput_recent(e) {
  generatecss_recent();
}

/**
 * 最近のデータの設定のチェックボックスを変更した
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_recent(e) {
  generatecss_recent();
}

/**
 * 統計の設定のテキスト入力を変更した
 * @param {ce.Event} e イベントハンドラ
 */
function oninput_summary(e) {
  generatecss_summary();
}

/**
 * 統計設定のプレイモードの有効/無効を切り替えた
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_summaryplaymodes(e) {
  const playmode = $(`label[for="${$(this).attr('id')}"]`).text();
  const value = $(this).prop('checked');

  $(`input.${playmode}`).prop('disabled', !value);

  generatecss_summary();
}

/**
 * 統計設定のチェックボックスを変更した
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_summary(e) {
  generatecss_summary();
}

/**
 * CSV出力
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_output_csv(e) {
  pywebview.api.output_csv();
}

/**
 * 最近のデータのリセットの確認
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_confirm_clearrecent(e) {
  $('dialog#dialog_clearrecent')[0].showModal();
}

/**
 * 最近のデータのリセット
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_execute_clearrecent(e) {
  pywebview.api.clear_recent();
  $(this).closest('dialog')[0].close();
}

/**
 * CSSをクリップボードにコピー
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_clipboardcopy_css(e) {
  navigator.clipboard.writeText($('textarea#css').val());
}

/**
 * ダイアログを閉じる
 * @param {ce.Event} e イベントハンドラ
 */
function onclick_button_dialogclose(e) {
  $(this).closest('dialog')[0].close();
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

function generatecss_recent() {
  const css = [];

  css.push('body {');

  const textsize = $('input#text_recent_textsize').val();
  if(!isNaN(textsize)) {
    csssetting.recent['size'] = textsize;
    css.push(`  font-size: ${textsize}px;`);
  }

  const textcolor = $('input#text_recent_textcolor').val();
  csssetting.recent['color'] = textsize;
  css.push(`  color: ${textcolor};`);

  const shadowcolor = $('input#text_recent_shadowcolor').val();
  csssetting.recent['shadow-color'] = textsize;
  const shadows = ['1px 1px', '-1px 1px', '1px -1px', '-1px -1px'];
  const shadow_value = shadows.map(v => {return `${v} 0 ${shadowcolor}`});
  css.push(`  text-shadow: ${shadow_value};`);
  css.push('}');

  css.push('');

  difficulties.forEach(difficulty => {
    const value = $(`input#text_recent_${difficulty}_color`).val();
    csssetting.recent[difficulty] = value;
    css.push(`span.${difficulty} { color: ${value};}`);
  });

  css.push('');

  Object.keys(csssetting_default.recent['overviews']).forEach(key => {
    const display = $(`input#check_recent_${key}_display`).prop('checked');
    const color = $(`input#text_recent_${key}_color`).val();

    csssetting.recent['overviews'][key]['display'] = display;
    csssetting.recent['overviews'][key]['color'] = color;

    css.push(`div#${key} {`);
    if(display)
      css.push('  display: block;');
    else
      css.push('  display: none;');
    css.push(`  color: ${color};`);
    css.push('}');
    css.push('');
  });

  $('span#csstarget').text('最近のデータ');
  $("textarea#css").val(css.join("\n"));

  pywebview.api.set_csssetting(csssetting);
}

function generatecss_summary() {
  const css = [];

  css.push('body {');

  const textcolor = $('input#text_summary_textcolor').val();
  csssetting.summary['color'] = textcolor;
  css.push(`  color: ${textcolor};`);

  const shadowcolor = $('input#text_summary_shadowcolor').val();
  csssetting.summary['shadow-color'] = shadowcolor;
  const shadows = ['1px 1px', '-1px 1px', '1px -1px', '-1px -1px'];
  const shadow_value = shadows.map(v => {return `${v} 0 ${shadowcolor}`});
  css.push(`  text-shadow: ${shadow_value};`);
  css.push('}');

  css.push('');

  css.push('div#update_date {');
  const datecolor = $('input#text_summary_datecolor').val();
  csssetting.summary['date color'] = datecolor;
  css.push(`  color: ${datecolor};`);
  css.push('}');

  css.push('');

  playmodes.forEach(playmode => {
    ['A', 'AA', 'AAA'].forEach(djlevel => {
    css.push(`div.${playmode}.ANOTHER.${djlevel} { display: none;}`);
    });

    css.push('');

    const playmodecheck = $(`input#check_summary_${playmode}`).prop('checked');
    csssetting.summary[playmode]['checked'] = playmodecheck;

    csssetting.summary[playmode]['difficulties'] = {};
    csssetting.summary[playmode]['difficulties']['checked'] = [];
    difficulties.forEach(difficulty => {
      if($(`input#check_summary_${playmode}_${difficulty}`).prop('checked'))
        csssetting.summary[playmode]['difficulties']['checked'].push(difficulty);
    });

    csssetting.summary[playmode]['levels'] = {};
    csssetting.summary[playmode]['levels']['checked'] = [];
    levels.forEach(level => {
      if($(`input#check_summary_${playmode}_${level}`).prop('checked'))
        csssetting.summary[playmode]['levels']['checked'].push(level);
    });

    ['difficulties', 'levels'].forEach(key => {
      csssetting.summary[playmode][key]['clear_types'] = [];
      cleartypes.forEach(cleartype => {
        const replaced_cleartype = cleartype.replace(' ', '--');
        if($(`input#check_summary_${playmode}_${key}_${replaced_cleartype}`).prop('checked'))
          csssetting.summary[playmode][key]['clear_types'].push(cleartype);
      });
  
      csssetting.summary[playmode][key]['dj_levels'] = [];
      djlevels.forEach(djlevel => {
        if($(`input#check_summary_${playmode}_${key}_${djlevel}`).prop('checked'))
          csssetting.summary[playmode][key]['dj_levels'].push(djlevel);
      });
    });
    
    if(playmodecheck) {
      csssetting.summary[playmode]['difficulties']['checked'].forEach(difficulty => {
        ['clear_types', 'dj_levels'].forEach(key => {
          csssetting.summary[playmode]['difficulties'][key].forEach(value => {
            css.push(`div.${playmode}.${difficulty}.${value.replace(' ', '-')} { display: block;}`);
          });
    
          css.push('');
        });
      });

      csssetting.summary[playmode]['levels']['checked'].forEach(level => {
        ['clear_types', 'dj_levels'].forEach(key => {
          csssetting.summary[playmode]['levels'][key].forEach(value => {
            css.push(`div.${playmode}.LEVEL${level}.${value.replace(' ', '-')} { display: block;}`);
          });
    
          css.push('');
        });
      });
    }
  });

  $('span#csstarget').text('統計データ');
  $('textarea#css').val(css.join('\n'));

  pywebview.api.set_csssetting(csssetting);
}