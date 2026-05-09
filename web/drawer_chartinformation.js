/**
 * 譜面記録を描画する
 */
class DrawerChartinformation {
  static textcolor = 'white';
  static shadowcolor_basic = 'black';
  static fontsize_songname = 80;
  static fontsize_basic = 50;
  static fontsize_value = 60;
  static fontsize_small = 30;

  static shadowcolors_difficulty = {
    'BEGINNER': 'rgb(0, 160, 0)',
    'NORMAL': 'rgb(0, 0, 224)',
    'HYPER': 'rgb(160, 160, 0)',
    'ANOTHER': 'rgb(192, 0, 0)',
    'LEGGENDARIA': 'rgb(192, 0, 192)',
  };

  static shadowcolor_fcomboandaaa = 'rgb(240, 200, 80)';
  static shadowcolor_max = 'rgb(128, 255, 40)';
  
  static songname_x = 20;
  static songname_y = 10;

  static charttype_y = 100;
  static playtype_x = 80;
  static difficulty_x = 190;
  static difficulty_x_battle = 480;

  static playedcount_xpositions = {'label': 40, 'value': 700};
  static playedcount_ypositions = {'label': 180, 'value': 175};

  static lasttimeplayed_xpositions = {'label': 40, 'value': 550};
  static lasttimeplayed_ypositions = {'label': 250, 'value': 245};

  static newrecordlabel_x = 40;
  static newrecordlabel_y = 350;
  static newrecordkeys = {
    'score': {
      'label': {'x': 80, 'y': 420},
      'value': {'x': 580, 'y': 415},
      'option': {'x': 650, 'y': 415},
    },
    'miss_count': {
      'label': {'x': 80, 'y': 490},
      'value': {'x': 580, 'y': 485},
      'option': {'x': 650, 'y': 485},
    },
  };

  static achievementlabel_x = 40;
  static achievementlabel_y = 580;
  static achievementkeys = {
    'fixed': {
      'label': {'text': 'FIXED', 'x': 220, 'y': 640},
      'max and fcomboandaaa': {'x': 220, 'y': 680},
      'clear_type': {'x': 240, 'y': 680},
      'dj_level': {'x': 330, 'y': 680},
    },
    'S-RANDOM': {
      'label': {'text': 'S-RANDOM', 'x': 620, 'y': 640},
      'max and fcomboandaaa': {'x': 620, 'y': 680},
      'clear_type': {'x': 640, 'y': 680},
      'dj_level': {'x': 730, 'y': 680},
    },
    'ALL-SCR': {
      'label': {'text': 'ALL-SCR', 'x': 1020, 'y': 640, 'special': true},
      'max and fcomboandaaa': {'x': 1020, 'y': 680},
      'clear_type': {'x': 1040, 'y': 680},
      'dj_level': {'x': 1130, 'y': 680},
    },
  };

  static drawtextargs_songname = {
    'textcolor': DrawerChartinformation.textcolor,
    'shadowcolor': DrawerChartinformation.shadowcolor_basic,
    'fontsize': DrawerChartinformation.fontsize_songname,
    'maxwidth': 1200,
  };

  static drawtextargs_basic = {
    'textcolor': DrawerChartinformation.textcolor,
    'shadowcolor': DrawerChartinformation.shadowcolor_basic,
    'fontsize': DrawerChartinformation.fontsize_basic,
  };

  static drawtextargs_value = {
    'textcolor': DrawerChartinformation.textcolor,
    'shadowcolor': DrawerChartinformation.shadowcolor_basic,
    'fontsize': DrawerChartinformation.fontsize_value,
  };

  static drawtextargs_small = {
    'textcolor': DrawerChartinformation.textcolor,
    'shadowcolor': DrawerChartinformation.shadowcolor_basic,
    'fontsize': DrawerChartinformation.fontsize_small,
  };

  canvas = null;

  draw_text = function(ctx, text, x, y, args) {
    ctx.fillText(text, x, y);
  }

  /**
   * @param {Bigint} width キャンパスの幅
   * @param {Bitint} height キャンパスの高さ
   * @param {string} fontfamily フォント名
   */
  constructor(width, height, fontfamily) {
    this.canvas = new OffscreenCanvas(width, height, fontfamily);
    this.fontfamily = fontfamily;
  }

  /**
   * 画像を描画する
   * @param {} values 譜面記録データ
   * @param {string} playtype プレイの種類
   * @param {string} songname 曲名
   * @param {string} difficulty 譜面難易度
   * @param {boolean} battle バトルモード
   * @returns {blob} 画像データ
   */
  async draw(values, playtype, songname, difficulty, battle) {
    const ctx = this.canvas.getContext('2d');

    const args_difficulty = {
      'textcolor': DrawerChartinformation.textcolor,
      'shadowcolor': DrawerChartinformation.shadowcolors_difficulty[difficulty],
      'fontsize': DrawerChartinformation.fontsize_value,
    }

    ctx.save();

    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    ctx.textBaseline = 'top';

    ctx.font = `${DrawerChartinformation.fontsize_songname}px ${this.fontfamily}`;
    this.drawtext_left(
      ctx,
      songname,
      DrawerChartinformation.songname_x,
      DrawerChartinformation.songname_y,
      DrawerChartinformation.drawtextargs_songname,
    );

    ctx.font = `${DrawerChartinformation.fontsize_value}px ${this.fontfamily}`;

    this.drawtext_left(
      ctx,
      playtype,
      DrawerChartinformation.playtype_x,
      DrawerChartinformation.charttype_y,
      DrawerChartinformation.drawtextargs_value,
    );
    this.drawtext_left(
      ctx,
      difficulty,
      !battle ? DrawerChartinformation.difficulty_x : DrawerChartinformation.difficulty_x_battle,
      DrawerChartinformation.charttype_y,
      args_difficulty,
    );

    if(values.timestamps != null && values.timestamps.length > 0) {
      ctx.font = `${DrawerChartinformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        'Played count.',
        DrawerChartinformation.playedcount_xpositions.label,
        DrawerChartinformation.playedcount_ypositions.label,
        DrawerChartinformation.drawtextargs_basic,
      );

      ctx.font = `bold ${DrawerChartinformation.fontsize_value}px ${this.fontfamily}`;
      this.drawtext_right(
        ctx,
        values.timestamps.length,
        DrawerChartinformation.playedcount_xpositions.value,
        DrawerChartinformation.playedcount_ypositions.value,
        DrawerChartinformation.drawtextargs_value,
      );
    }

    if(values.latest != null) {
      ctx.font = `${DrawerChartinformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        'Last time played.',
        DrawerChartinformation.lasttimeplayed_xpositions.label,
        DrawerChartinformation.lasttimeplayed_ypositions.label,
        DrawerChartinformation.drawtextargs_basic,
      );

      ctx.font = `bold ${DrawerChartinformation.fontsize_value}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        values.latest.timestamp,
        DrawerChartinformation.lasttimeplayed_xpositions.value,
        DrawerChartinformation.lasttimeplayed_ypositions.value,
        DrawerChartinformation.drawtextargs_value,
      );
    }

    if(values.best != null) {
      ctx.font = `${DrawerChartinformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        'Options when update a new record.',
        DrawerChartinformation.newrecordlabel_x,
        DrawerChartinformation.newrecordlabel_y,
        DrawerChartinformation.drawtextargs_basic,
      );

      Object.keys(DrawerChartinformation.newrecordkeys).forEach(key => {
        ctx.font = `${DrawerChartinformation.fontsize_basic}px ${this.fontfamily}`;
        this.drawtext_left(
          ctx,
          key.replace('_', ' '),
          DrawerChartinformation.newrecordkeys[key].label.x,
          DrawerChartinformation.newrecordkeys[key].label.y,
          DrawerChartinformation.drawtextargs_basic,
        );

        if(values.best[key] == null || values.best[key].value == null) return;

        ctx.font = `bold ${DrawerChartinformation.fontsize_value}px ${this.fontfamily}`;
        this.drawtext_right(
          ctx,
          values.best[key].value,
          DrawerChartinformation.newrecordkeys[key].value.x,
          DrawerChartinformation.newrecordkeys[key].value.y,
          DrawerChartinformation.drawtextargs_value,
        );

        let option;
        if(values.best[key].options != null)
          option = values.best[key].options.arrange == null ? '-------' : values.best[key].options.arrange;
        else
          option = '?????'

        ctx.font = `bold ${DrawerChartinformation.fontsize_value}px ${this.fontfamily}`;
        this.drawtext_left(
          ctx,
          option,
          DrawerChartinformation.newrecordkeys[key].option.x,
          DrawerChartinformation.newrecordkeys[key].option.y,
          DrawerChartinformation.drawtextargs_value,
        );
      });
    }

    if(values.achievement != null) {
      ctx.font = `${DrawerChartinformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        'Achievement status for each options.',
        DrawerChartinformation.achievementlabel_x,
        DrawerChartinformation.achievementlabel_y,
        DrawerChartinformation.drawtextargs_basic,
      );

      const drawtextargs_special = {
        'textcolor': DrawerChartinformation.textcolor,
        'shadowcolor': DrawerChartinformation.shadowcolors_difficulty[difficulty],
        'fontsize': DrawerChartinformation.fontsize_small,
      };
    
      Object.keys(DrawerChartinformation.achievementkeys).forEach(key => {
        if(!values.achievement.hasOwnProperty(key) || values.achievement[key] == null) return;

        ctx.font = `${DrawerChartinformation.fontsize_small}px ${this.fontfamily}`;

        let drawtextargs_text = DrawerChartinformation.drawtextargs_small;
        if(DrawerChartinformation.achievementkeys[key].label.special)
          drawtextargs_text = drawtextargs_special;
        
        this.drawtext_center(
          ctx,
          DrawerChartinformation.achievementkeys[key].label.text,
          DrawerChartinformation.achievementkeys[key].label.x,
          DrawerChartinformation.achievementkeys[key].label.y,
          drawtextargs_text,
        );

        if(values.achievement[key]['MAX']) {
          this.drawtext_center(
            ctx,
            'MAX',
            DrawerChartinformation.achievementkeys[key]['max and fcomboandaaa'].x,
            DrawerChartinformation.achievementkeys[key]['max and fcomboandaaa'].y,
            drawtextargs_special,
          );
  
          return;
        }
        
        if(values.achievement[key]['F-COMBO & AAA']) {
          this.drawtext_center(
            ctx,
            'F-COMBO & AAA',
            DrawerChartinformation.achievementkeys[key]['max and fcomboandaaa'].x,
            DrawerChartinformation.achievementkeys[key]['max and fcomboandaaa'].y,
            drawtextargs_special,
          );
  
          return;
        }
        
        ['clear_type', 'dj_level'].forEach(key2 => {
          if(!values.achievement[key].hasOwnProperty(key2) || values.achievement[key][key2] == null) return;

          this.drawtext_right(
            ctx,
            values.achievement[key][key2],
            DrawerChartinformation.achievementkeys[key][key2].x,
            DrawerChartinformation.achievementkeys[key][key2].y,
            DrawerChartinformation.drawtextargs_small,
          );
        });
      });
    }
    ctx.restore();

    const timer = new PerformanceTimer();
    const blob = await this.canvas.convertToBlob();
    if(setting.debug)
      console.log(`chart information convert blob time: ${timer.time} ms`);

    return blob;
  }

  drawtext_left(ctx, text, x, y, args) {
    this.draw_text(ctx, text, x, y, args);
  }

  drawtext_right(ctx, text, x, y, args) {
    const width = ctx.measureText(text).width;

    this.draw_text(ctx, text, x - width, y, args);
  }

  drawtext_center(ctx, text, x, y, args) {
    const width = ctx.measureText(text).width;

    this.draw_text(ctx, text, x - width / 2, y, args);
  }
}
