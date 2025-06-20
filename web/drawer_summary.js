/**
 * サマリー記録を描画する
 */
class DrawerSummary {
  static textcolor = 'white';
  static shadowcolor = 'black';
  static fontsize_title = 80;
  static fontsize_basic = 46;
  static fontsize_small = 30;
  static fontsize_nodatalabel = 22;

  static title_texts = {
      false: 'Number achieved.',
      true: 'Number recorded.',
  }

  static title_x = 20;
  static title_y = 20;

  static summarytypes = ['cleartypes', 'djlevels'];

  static summarytypes_xpositions = {
    'cleartypes': {'label': 520, 'count': 640},
    'djlevels': {'label': 790, 'count': 910},
  }

  static total_x = 1100;
  static nodata_x = 1230;
  static columnheaders_y = 150;

  static playmode_x = 100;
  static level_x = 200;

  static drawtextargs_title = {
    'textcolor': DrawerSummary.textcolor,
    'shadowcolor': DrawerSummary.shadowcolor,
    'fontsize': DrawerSummary.fontsize_title,
  }

  static drawtextargs_basic = {
    'textcolor': DrawerSummary.textcolor,
    'shadowcolor': DrawerSummary.shadowcolor,
    'fontsize': DrawerSummary.fontsize_basic,
  }

  static drawtextargs_nodatalabel = {
    'textcolor': DrawerSummary.textcolor,
    'shadowcolor': DrawerSummary.shadowcolor,
    'fontsize': DrawerSummary.fontsize_nodatalabel,
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
   * @param {} vaues 統計カウントデータ
   * @param {boolean} countmethod_only カウント方式が一致する譜面のみ
   * @returns {blob} 画像データ
   */
  async draw(values, countmethod_only) {
    const ctx = this.canvas.getContext('2d');

    ctx.save();

    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    ctx.textBaseline = 'top';

    ctx.font = `${DrawerSummary.fontsize_title}px ${this.fontfamily}`;
    this.drawtext_left(
      ctx,
      DrawerSummary.title_texts[countmethod_only],
      DrawerSummary.title_x,
      DrawerSummary.title_y,
      DrawerSummary.drawtextargs_title,
    );

    ctx.font = `${DrawerSummary.fontsize_basic}px ${this.fontfamily}`;
    ctx.lineWidth = DrawerSummary.fontsize_basic / 5;

    this.drawtext_right(
      ctx,
      'CLEAR TYPE',
      DrawerSummary.summarytypes_xpositions.cleartypes.count,
      DrawerSummary.columnheaders_y,
      DrawerSummary.drawtextargs_basic,
    );
    this.drawtext_right(
      ctx,
      'DJ LEVEL',
      DrawerSummary.summarytypes_xpositions.djlevels.count,
      DrawerSummary.columnheaders_y,
      DrawerSummary.drawtextargs_basic,
    );
    this.drawtext_right(
      ctx,
      'TOTAL',
      DrawerSummary.total_x,
      DrawerSummary.columnheaders_y,
      DrawerSummary.drawtextargs_basic,
    );

    ctx.font = `${DrawerSummary.fontsize_nodatalabel}px ${this.fontfamily}`;

    this.drawtext_right(
      ctx,
      'NO',
      DrawerSummary.nodata_x, 
      DrawerSummary.columnheaders_y,
      DrawerSummary.drawtextargs_nodatalabel,
    );
    this.drawtext_right(
      ctx,
      'DATA',
      DrawerSummary.nodata_x,
      DrawerSummary.columnheaders_y + 26,
      DrawerSummary.drawtextargs_nodatalabel,
    );

    let line = 0;
    Object.keys(values).forEach(playmode => {
      Object.keys(values[playmode]).forEach(level => {
        const levelcount = Math.max(
          Object.keys(values[playmode][level]['cleartypes']).length,
          Object.keys(values[playmode][level]['djlevels']).length,
        );

        const items = {}
        DrawerSummary.summarytypes.forEach(summarytype => {
          items[summarytype] = [];

          Object.keys(values[playmode][level][summarytype]).forEach(key => {
            items[summarytype].push({'key': key, 'count': values[playmode][level][summarytype][key]});
          });
        });

        for(let i = 0; i < levelcount; i++) {
          ctx.font = `${DrawerSummary.fontsize_basic}px ${this.fontfamily}`;
          this.drawtext_right(
            ctx,
            playmode,
            DrawerSummary.playmode_x, line * 50 + 200,
            DrawerSummary.drawtextargs_basic,
          );
          this.drawtext_right(
            ctx,
            level,
            DrawerSummary.level_x, line * 50 + 200,
            DrawerSummary.drawtextargs_basic,
          );

          DrawerSummary.summarytypes.forEach(summarytype => {
            if(i >= items[summarytype].length)
              return;

            ctx.font = `${DrawerSummary.fontsize_basic}px ${this.fontfamily}`;
            this.drawtext_right(
              ctx,
              items[summarytype][i].key,
              DrawerSummary.summarytypes_xpositions[summarytype].label,
              line * 50 + 200,
              DrawerSummary.drawtextargs_basic,
            );

            ctx.font = `bold ${DrawerSummary.fontsize_basic}px ${this.fontfamily}`;
            this.drawtext_right(
              ctx,
              items[summarytype][i].count,
              DrawerSummary.summarytypes_xpositions[summarytype].count,
              line * 50 + 200,
              DrawerSummary.drawtextargs_basic,
            );
          });

          ctx.font = `bold ${DrawerSummary.fontsize_basic}px ${this.fontfamily}`;
          this.drawtext_right(
            ctx,
            values[playmode][level]['TOTAL'],
            DrawerSummary.total_x, line * 50 + 200,
            DrawerSummary.drawtextargs_basic,
          );

          if(values[playmode][level]['NO DATA']) {
            ctx.font = `${DrawerSummary.fontsize_small}px ${this.fontfamily}`;
            ctx.lineWidth = DrawerSummary.fontsize_small / 5;
            this.drawtext_right(
              ctx,
              `(${values[playmode][level]['NO DATA']})`,
              DrawerSummary.nodata_x, line * 50 + 200 + 15,
              DrawerSummary.drawtextargs_basic,
            );
          }

          line += 1;
        }
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
}