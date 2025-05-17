/**
 * サマリー記録を描画する
 */
class DrawerInformation {
  static textcolor = 'white';
  static shadowcolor = 'black';

  static fontsize_basic = 60;
  static fontsize_value = 80;

  static musiccount_xpositions = {
    'label': 450,
    'value': 850,
  };
  static musiccount_y = 150;

  static playmodes_xpositions = {
    'SP': 930,
    'DP': 1130,
  };
  static playmodes_y = 250;

  static label_x = 150;
  static label_texts = {
    'allscores': '全譜面数',
    'begginers': 'ビギナー譜面数',
    'leggendarias': 'レジェンダリア譜面数',
  };
  static label_ypositions = {
    'allscores': 350,
    'begginers': 450,
    'leggendarias': 550,
  };

  static drawtextargs_basic = {
    'textcolor': DrawerInformation.textcolor,
    'shadowcolor': DrawerInformation.shadowcolor,
    'fontsize': DrawerInformation.fontsize_basic,
  }

  static drawtextargs_value = {
    'textcolor': DrawerInformation.textcolor,
    'shadowcolor': DrawerInformation.shadowcolor,
    'fontsize': DrawerInformation.fontsize_value,
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
   * インフィニタス情報を描画する
   * @argument {dict} values 全曲データ
   * @returns {blob} 画像データ
   */
  async draw(values) {
    const scorecounts = {'allscores': {}, 'begginers': {}, 'leggendarias': {}};
    Object.keys(values.levels).forEach(playmode => {
      scorecounts.allscores[playmode] = 0;
      Object.keys(values.levels[playmode]).forEach(level => {
        scorecounts.allscores[playmode] += Object.keys(values.levels[playmode][level]).length;
      });

      scorecounts.leggendarias[playmode] = Object.keys(values.leggendarias[playmode]).length;
    });
    scorecounts.begginers['SP'] = Object.keys(values.beginners).length;

    const ctx = this.canvas.getContext('2d');

    ctx.save();

    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    ctx.textBaseline = 'middle';

    ctx.font = `${DrawerInformation.fontsize_basic}px ${this.fontfamily}`;
    this.drawtext_left(
      ctx,
      '全曲数',
      DrawerInformation.musiccount_xpositions.label,
      DrawerInformation.musiccount_y,
      DrawerInformation.drawtextargs_basic,
    );

    ctx.font = `bold ${DrawerInformation.fontsize_value}px ${this.fontfamily}`;
    this.drawtext_right(
      ctx,
      Object.keys(values.musics).length,
      DrawerInformation.musiccount_xpositions.value,
      DrawerInformation.musiccount_y,
      DrawerInformation.drawtextargs_value,
    );

    Object.keys(DrawerInformation.playmodes_xpositions).forEach(playmode => {
      ctx.font = `${DrawerInformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_right(
        ctx,
        playmode,
        DrawerInformation.playmodes_xpositions[playmode],
        DrawerInformation.playmodes_y,
        DrawerInformation.drawtextargs_basic,
      );
    });

    Object.keys(DrawerInformation.label_ypositions).forEach(key => {
      ctx.font = `${DrawerInformation.fontsize_basic}px ${this.fontfamily}`;
      this.drawtext_left(
        ctx,
        DrawerInformation.label_texts[key],
        DrawerInformation.label_x,
        DrawerInformation.label_ypositions[key],
        DrawerInformation.drawtextargs_basic,
      );

      Object.keys(DrawerInformation.playmodes_xpositions).forEach(playmode => {
        if(scorecounts[key][playmode] == null) return;

        ctx.font = `bold ${DrawerInformation.fontsize_value}px ${this.fontfamily}`;
        this.drawtext_right(
          ctx,
          scorecounts[key][playmode],
          DrawerInformation.playmodes_xpositions[playmode],
          DrawerInformation.label_ypositions[key],
          DrawerInformation.drawtextargs_value,
        );
      });
    });
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