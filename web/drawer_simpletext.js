/**
 * サマリー記録を描画する
 */
class DrawerSimpletext {
  static textcolor = 'white';
  static shadowcolor = 'black';

  static fontsize_simple = 120;
  static fontsize_title = 80;
  static fontsize_basic = 48;

  static title_y = 250;
  static message_y = 550;

  static drawtextargs_simple = {
    'textcolor': DrawerSimpletext.textcolor,
    'shadowcolor': DrawerSimpletext.shadowcolor,
    'fontsize': DrawerSimpletext.fontsize_simple,
  }

  static drawtextargs_title = {
    'textcolor': DrawerSimpletext.textcolor,
    'shadowcolor': DrawerSimpletext.shadowcolor,
    'fontsize': DrawerSimpletext.fontsize_title,
  }

  static drawtextargs_basic = {
    'textcolor': DrawerSimpletext.textcolor,
    'shadowcolor': DrawerSimpletext.shadowcolor,
    'fontsize': DrawerSimpletext.fontsize_basic,
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
   * 最もシンプルな画像を描画する
   * @returns {blob} 画像データ
   */
  async draw_simple(text) {
    const ctx = this.canvas.getContext('2d');

    ctx.save();

    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    ctx.textBaseline = 'middle';

    ctx.font = `${DrawerSimpletext.fontsize_simple}px ${this.fontfamily}`;
    this.drawtext_center(
      ctx,
      text,
      this.canvas.width / 2,
      this.canvas.height / 2,
      DrawerSimpletext.drawtextargs_simple,
    );

    ctx.restore();

    return await this.canvas.convertToBlob();
  }

  /**
   * メッセージを含む画像を描画する
   * @returns {blob} 画像データ
   */
  async draw_message(title, message) {
    const ctx = this.canvas.getContext('2d');

    ctx.save();

    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    ctx.textBaseline = 'middle';

    ctx.font = `${DrawerSimpletext.fontsize_title}px ${this.fontfamily}`;
    this.drawtext_center(
      ctx,
      title,
      this.canvas.width / 2,
      DrawerSimpletext.title_y,
      DrawerSimpletext.drawtextargs_title,
    );

    ctx.font = `${DrawerSimpletext.fontsize_basic}px ${this.fontfamily}`;
    this.drawtext_center(
      ctx,
      message,
      this.canvas.width / 2,
      DrawerSimpletext.message_y,
      DrawerSimpletext.drawtextargs_basic,
    );

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