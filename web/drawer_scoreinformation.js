/**
 * 譜面記録を描画する
 */
class DrawerScoreinformation {
  static textcolor = 'white';
  static shadowcolor_basic = 'black';
  static fontsize_musicname = 80;
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

  static musicname_x = 20;
  static musicname_y = 10;

  static scoretype_y = 100;
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
      'clear_type': {'x': 240, 'y': 680},
      'dj_level': {'x': 330, 'y': 680},
    },
    'S-RANDOM': {
      'label': {'text': 'S-RANDOM', 'x': 620, 'y': 640},
      'clear_type': {'x': 640, 'y': 680},
      'dj_level': {'x': 730, 'y': 680},
    },
  };

  static drawtextargs_musicname = {
    'textcolor': DrawerScoreinformation.textcolor,
    'shadowcolor': DrawerScoreinformation.shadowcolor_basic,
    'fontsize': DrawerScoreinformation.fontsize_musicname,
    'maxwidth': 1200,
  }

  static drawtextargs_basic = {
    'textcolor': DrawerScoreinformation.textcolor,
    'shadowcolor': DrawerScoreinformation.shadowcolor_basic,
    'fontsize': DrawerScoreinformation.fontsize_basic,
  }

  static drawtextargs_value = {
    'textcolor': DrawerScoreinformation.textcolor,
    'shadowcolor': DrawerScoreinformation.shadowcolor_basic,
    'fontsize': DrawerScoreinformation.fontsize_value,
  }

  static drawtextargs_small = {
    'textcolor': DrawerScoreinformation.textcolor,
    'shadowcolor': DrawerScoreinformation.shadowcolor_basic,
    'fontsize': DrawerScoreinformation.fontsize_small,
  }

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
   * @param {string} musicname 曲名
   * @param {string} difficulty 譜面難易度
   * @param {boolean} battle バトルモード
   * @returns {blob} 画像データ
   */
  async draw(values, playtype, musicname, difficulty, battle) {
    const ctx = this.canvas.getContext('2d');

    const args_difficulty = {
      'textcolor': DrawerScoreinformation.textcolor,
      'shadowcolor': DrawerScoreinformation.shadowcolors_difficulty[difficulty],
      'fontsize': DrawerScoreinformation.fontsize_value,
    }

    ctx.save();

    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    ctx.textBaseline = 'top';

    ctx.font = `${DrawerScoreinformation.fontsize_musicname}px ${this.fontfamily}`;
    this.drawtext_left(
      ctx,
      musicname,
      DrawerScoreinformation.musicname_x,
      DrawerScoreinformation.musicname_y,
      DrawerScoreinformation.drawtextargs_musicname,
    );

    ctx.font = `${DrawerScoreinformation.fontsize_value}px ${this.fontfamily}`;

    this.drawtext_left(
      ctx,
      playtype,
      DrawerScoreinformation.playtype_x,
      DrawerScoreinformation.scoretype_y,
      DrawerScoreinformation.drawtextargs_value,
    );
    this.drawtext_left(
      ctx,
      difficulty,
      !battle ? DrawerScoreinformation.difficulty_x : DrawerScoreinformation.difficulty_x_battle,
      DrawerScoreinformation.scoretype_y,
      args_difficulty,
    );

    if(values.timestamps != null && values.timestamps.length > 0) {
      ctx.font = `${DrawerScoreinformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        'Played count.',
        DrawerScoreinformation.playedcount_xpositions.label,
        DrawerScoreinformation.playedcount_ypositions.label,
        DrawerScoreinformation.drawtextargs_basic,
      );

      ctx.font = `bold ${DrawerScoreinformation.fontsize_value}px ${this.fontfamily}`;
      this.drawtext_right(
        ctx,
        values.timestamps.length,
        DrawerScoreinformation.playedcount_xpositions.value,
        DrawerScoreinformation.playedcount_ypositions.value,
        DrawerScoreinformation.drawtextargs_value,
      );
    }

    if(values.latest != null) {
      ctx.font = `${DrawerScoreinformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        'Last time played.',
        DrawerScoreinformation.lasttimeplayed_xpositions.label,
        DrawerScoreinformation.lasttimeplayed_ypositions.label,
        DrawerScoreinformation.drawtextargs_basic,
      );

      ctx.font = `bold ${DrawerScoreinformation.fontsize_value}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        values.latest.timestamp,
        DrawerScoreinformation.lasttimeplayed_xpositions.value,
        DrawerScoreinformation.lasttimeplayed_ypositions.value,
        DrawerScoreinformation.drawtextargs_value,
      );
    }

    if(values.best != null) {
      ctx.font = `${DrawerScoreinformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        'Options when update a new record.',
        DrawerScoreinformation.newrecordlabel_x,
        DrawerScoreinformation.newrecordlabel_y,
        DrawerScoreinformation.drawtextargs_basic,
      );

      Object.keys(DrawerScoreinformation.newrecordkeys).forEach(key => {
        ctx.font = `${DrawerScoreinformation.fontsize_basic}px ${this.fontfamily}`;
        this.drawtext_left(
          ctx,
          key.replace('_', ' '),
          DrawerScoreinformation.newrecordkeys[key].label.x,
          DrawerScoreinformation.newrecordkeys[key].label.y,
          DrawerScoreinformation.drawtextargs_basic,
        );

        if(values.best[key] == null || values.best[key].value == null) return;

        ctx.font = `bold ${DrawerScoreinformation.fontsize_value}px ${this.fontfamily}`;
        this.drawtext_right(
          ctx,
          values.best[key].value,
          DrawerScoreinformation.newrecordkeys[key].value.x,
          DrawerScoreinformation.newrecordkeys[key].value.y,
          DrawerScoreinformation.drawtextargs_value,
        );

        let option;
        if(values.best[key].options != null)
          option = values.best[key].options.arrange == null ? '-------' : values.best[key].options.arrange;
        else
          option = '?????'

        ctx.font = `bold ${DrawerScoreinformation.fontsize_value}px ${this.fontfamily}`;
        this.drawtext_left(
          ctx,
          option,
          DrawerScoreinformation.newrecordkeys[key].option.x,
          DrawerScoreinformation.newrecordkeys[key].option.y,
          DrawerScoreinformation.drawtextargs_value,
        );
      });
    }

    if(values.achievement != null) {
      ctx.font = `${DrawerScoreinformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        'Achievement status for each options.',
        DrawerScoreinformation.achievementlabel_x,
        DrawerScoreinformation.achievementlabel_y,
        DrawerScoreinformation.drawtextargs_basic,
      );

      Object.keys(DrawerScoreinformation.achievementkeys).forEach(key => {
        if(!values.achievement.hasOwnProperty(key) || values.achievement[key] == null) return;
        
        ctx.font = `${DrawerScoreinformation.fontsize_small}px ${this.fontfamily}`;
        this.drawtext_center(
          ctx,
          DrawerScoreinformation.achievementkeys[key].label.text,
          DrawerScoreinformation.achievementkeys[key].label.x,
          DrawerScoreinformation.achievementkeys[key].label.y,
          DrawerScoreinformation.drawtextargs_small,
        );

        ['clear_type', 'dj_level'].forEach(key2 => {
          if(!values.achievement[key].hasOwnProperty(key2) || values.achievement[key][key2] == null) return;

          ctx.font = `bold ${DrawerScoreinformation.fontsize_small}px ${this.fontfamily}`;
          this.drawtext_right(
            ctx,
            values.achievement[key][key2],
            DrawerScoreinformation.achievementkeys[key][key2].x,
            DrawerScoreinformation.achievementkeys[key][key2].y,
            DrawerScoreinformation.drawtextargs_small,
          );
        });
      });
    }
    ctx.restore();

    return await this.canvas.convertToBlob();
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