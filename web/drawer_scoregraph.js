/**
 * 譜面のグラフを描画する
 * 
 * 対象譜面の記録のスコアとミスカウントをグラフ化する。
 */
class DrawerScoregraph {
  static textcolor = 'white';
  static shadowcolor = 'black';
  static scorecolor_data = 'rgba(64, 64, 192, 0.8)';
  static misscountcolor_data = 'rgba(192, 64, 64, 0.8)';
  static scorecolor = 'rgb(32, 64, 192)';
  static misscountcolor = 'rgb(192, 64, 32)';

  draw_text = function(text, x, y, args) {
    ctx.fillText(text, x, y);
  }

  /**
   * @param {Bitint} width キャンバスの幅
   * @param {Bitint} height キャンバスの高さ
   */
  constructor(width, height) {
    this.canvas = new OffscreenCanvas(width, height);

    this.chart = null;
  }

  /**
   * スコア記録のグラフを描画する。
   * @param {Array<Array<Object.<string, Date|Bigint>} values グラフデータ
   * @param {Array<string} xrange X軸の範囲
   * @param {Bigint} notes スコアの最大値
   * @param {string} musicname 曲名
   * @param {string} playmode プレイモード(SP or DP)
   * @param {string} difficulty 譜面難易度
   * @returns {blob} 画像データ
   */
  async draw(values, xrange, notes, musicname, playmode, difficulty) {
    if(this.chart) this.chart.destroy();

    const scoretype = `${playmode}${difficulty.substring(0, 1)}`;

    this.chart = new Chart(this.canvas.getContext('2d'), {
      type: 'scatter',
      data: {
        datasets: [
          {
            label: 'スコア',
            showLine: true,
            lineTension: 0,
            fill: false,
            borderColor: DrawerScoregraph.scorecolor_data,
            borderWidth: 2,
            data: values[0],
            yAxisID: 'left-y-axis',
            backgroundColor: DrawerScoregraph.scorecolor_data,
          },
          {
            label: 'ミスカウント',
            showLine: true,
            lineTension: 0,
            fill: false,
            borderColor: DrawerScoregraph.misscountcolor_data,
            borderWidth: 2,
            data: values[1],
            yAxisID: 'right-y-axis',
            backgroundColor: DrawerScoregraph.misscountcolor_data,
          },
        ],
      },
      options: {
        layout: {
          padding: {
            top: 50,
            right: 50,
            bottom: 50,
            left: 50,
          },
        },
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'day',
              displayFormats: {
                day: 'yyyy/MM/dd'
              },
            },
            min: xrange[0],
            max: xrange[1],
            ticks: {
              font: {
                size: 22,
              },
              maxTicksLimit: 6,
              color: DrawerScoregraph.textcolor,
              textStrokeColor: DrawerScoregraph.shadowcolor,
              textStrokeWidth: 3,
            },
          },
          'left-y-axis': {
            type: 'linear',
            position: 'left',
            beginAtZero: true,
            min: 0,
            max: notes * 2,
            ticks: {
              font: {
                size: 22,
              },
              color: DrawerScoregraph.textcolor,
              textStrokeColor: DrawerScoregraph.scorecolor,
              textStrokeWidth: 3,
            },
            grid: {
              display: false,
            }
          },
          'right-y-axis': {
            type: 'linear',
            position: 'right',
            beginAtZero: true,
            min: 0,
            max: Math.floor(notes / 10),
            ticks: {
              font: {
                size: 22,
              },
              color: DrawerScoregraph.textcolor,
              textStrokeColor: DrawerScoregraph.misscountcolor,
              textStrokeWidth: 3,
            },
            grid: {
              display: false,
            }
          },
        },
        plugins: {
          title: {
            display: true,
            text: `${musicname}[${scoretype}]`,
            font: {
              size: 40,
            },
            color: DrawerScoregraph.textcolor,
          },
          legend: {
            labels: {
              font: {
                size: 28,
                weight: 'bold',
              },
              color: DrawerScoregraph.textcolor,
            },
          },
        },
        animation: {
          duration: 0,
        },
      },
      plugins: [
        {
          beforeDraw: (chart) => {
            const ctx = chart.ctx;

            const chartarea = chart.chartArea;

            ctx.save();

            ctx.fillStyle = 'gray',
            ctx.fillRect(chartarea.left, chartarea.top, chartarea.width, chartarea.height);
            
            ctx.restore();

            chart.legend.options.display = false;
            chart.titleBlock.options.display = false;
          },
          afterDraw: (chart) => {
            const ctx = chart.ctx;

            const scalex = chart.scales['x'];
            const titleblock = chart.titleBlock;

            const titlefont = titleblock.options.font;
            const titletext = titleblock.options.text;
            const titlecenterx = (titleblock.left + titleblock.right) / 2;
            const titlecentery = (titleblock.top + titleblock.bottom) / 2;

            const labelfont = chart.legend.options.labels.font;

            const linevalues = [
              [
                Math.floor(notes * 2 * 8 / 9),
                Math.floor(notes * 2 * 7 / 9),
                Math.floor(notes * 2 * 6 / 9),
              ],
              [
                Math.floor(notes / 100),
                Math.floor(notes / 25),
              ],
            ];

            const legendlabel_xpositions = [
              scalex.left,
              scalex.right,
            ];
    
            const args_title = {
              'textcolor': DrawerScoregraph.textcolor,
              'shadowcolor': DrawerScoregraph.shadowcolor,
              'fontsize': titlefont.size,
            }

            const args_label = {
              'textcolor': DrawerScoregraph.textcolor,
              'shadowcolor': null,
              'fontsize': labelfont.size,
            }

            ctx.save();

            ctx.textAlign = titleblock.options.align;

            ctx.font = `${titlefont.weight} ${titlefont.size}px ${Chart.defaults.font.family}`;
            this.draw_text(ctx, titletext, titlecenterx, titlecentery, args_title);

            ctx.font = `${labelfont.weight} ${labelfont.size}px ${Chart.defaults.font.family}`;
            ctx.textBaseline = 'bottom';

            for(let i = 0; i < chart.data.datasets.length; i++) {
              const data = chart.data.datasets[i];

              const scale = chart.scales[data.yAxisID];

              args_label.shadowcolor = data.borderColor;
              this.draw_text(
                ctx,
                data.label,
                legendlabel_xpositions[i],
                scale.top - labelfont.size,
                args_label,
              );

              ctx.lineWidth = 0.5;
              linevalues[i].forEach(v => {
                const ycoord = scale.getPixelForValue(v);
  
                ctx.globalAlpha = 0.8 - i * 0.05;

                ctx.beginPath();
                ctx.moveTo(scalex.left, ycoord);
                ctx.lineTo(scalex.right, ycoord);
                ctx.closePath();
                ctx.stroke();
              });
            }

            ctx.restore();
          },
        },
      ],
    });

    return await this.canvas.convertToBlob();
  }
};
