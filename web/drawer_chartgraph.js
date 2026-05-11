/**
 * 譜面のグラフを描画する
 * 
 * 対象譜面の記録のスコアとミスカウントをグラフ化する。
 */
class DrawerChartgraph {
  static textcolor = 'white';
  static shadowcolor = 'black';
  static chartcolor_score = 'rgba(64, 64, 192, 0.8)';
  static chartcolor_scorebest = 'rgba(64, 64, 255, 1)';
  static chartcolor_misscount = 'rgba(192, 64, 64, 0.8)';
  static chartcolor_misscountbest = 'rgba(255, 64, 64, 1)';
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
   * @param {string} charttype プレイの種類と譜面難易度の3文字
   * @param {string} songname 曲名
   * @returns {blob} 画像データ
   */
  async draw(values, xrange, notes, charttype, songname) {
    if(this.chart !== null) {
      const time = await release_wait(this.chart);
      console.log(`%cchart graph wait time: ${time} ms`, 'color: orange;');
    }
    
    this.chart = new Chart(this.canvas.getContext('2d'), {
      type: 'scatter',
      data: {
        datasets: [
          {
            label: '更新スコア',
            showLine: true,
            lineTension: 0,
            fill: false,
            pointRadius: 8,
            borderColor: DrawerChartgraph.chartcolor_scorebest,
            borderWidth: 2,
            data: values[1],
            yAxisID: 'left-y-axis',
            backgroundColor: DrawerChartgraph.chartcolor_scorebest,
          },
          {
            label: '更新ミスカウント',
            showLine: true,
            lineTension: 0,
            fill: false,
            pointRadius: 8,
            borderColor: DrawerChartgraph.chartcolor_misscountbest,
            borderWidth: 2,
            data: values[3],
            yAxisID: 'right-y-axis',
            backgroundColor: DrawerChartgraph.chartcolor_misscountbest,
          },
          {
            label: 'スコア',
            showLine: false,
            lineTension: 0,
            fill: false,
            pointRadius: 4,
            borderColor: DrawerChartgraph.chartcolor_scorebest,
            borderWidth: 0,
            data: values[0],
            yAxisID: 'left-y-axis',
            backgroundColor: DrawerChartgraph.chartcolor_score,
          },
          {
            label: 'ミスカウント',
            showLine: false,
            lineTension: 0,
            fill: false,
            pointRadius: 4,
            borderColor: DrawerChartgraph.chartcolor_misscountbest,
            borderWidth: 0,
            data: values[2],
            yAxisID: 'right-y-axis',
            backgroundColor: DrawerChartgraph.chartcolor_misscount,
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
                size: 30,
              },
              maxTicksLimit: 6,
              color: DrawerChartgraph.textcolor,
              textStrokeColor: DrawerChartgraph.shadowcolor,
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
                size: 30,
              },
              color: DrawerChartgraph.textcolor,
              textStrokeColor: DrawerChartgraph.scorecolor,
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
                size: 30,
              },
              color: DrawerChartgraph.textcolor,
              textStrokeColor: DrawerChartgraph.misscountcolor,
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
            text: `${songname}[${charttype}]`,
            font: {
              size: 50,
            },
            color: DrawerChartgraph.textcolor,
          },
          legend: {
            labels: {
              font: {
                size: 28,
                weight: 'bold',
              },
              color: DrawerChartgraph.textcolor,
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

            const yaxisdefines = [
              {
                'dataset': chart.data.datasets[2],
                'xposition': scalex.left,
                'lines': [
                  Math.floor(notes * 2 * 8 / 9),
                  Math.floor(notes * 2 * 7 / 9),
                  Math.floor(notes * 2 * 6 / 9),
                ],
              },
              {
                'dataset': chart.data.datasets[3],
                'xposition': scalex.right,
                'lines': [
                  Math.floor(notes / 100),
                  Math.floor(notes / 25),
                ],
              },
            ];

            const args_title = {
              'textcolor': DrawerChartgraph.textcolor,
              'shadowcolor': DrawerChartgraph.shadowcolor,
              'fontsize': titlefont.size,
            }

            const args_label = {
              'textcolor': DrawerChartgraph.textcolor,
              'shadowcolor': null,
              'fontsize': labelfont.size,
            }

            ctx.save();

            ctx.textAlign = titleblock.options.align;

            ctx.font = `${titlefont.weight} ${titlefont.size}px ${Chart.defaults.font.family}`;
            this.draw_text(ctx, titletext, titlecenterx, titlecentery, args_title);

            ctx.font = `${labelfont.weight} ${labelfont.size}px ${Chart.defaults.font.family}`;
            ctx.textBaseline = 'bottom';

            yaxisdefines.forEach(target => {
              const dataset = target.dataset;

              const scale = chart.scales[dataset.yAxisID];

              args_label.shadowcolor = dataset.borderColor;
              this.draw_text(
                ctx,
                dataset.label,
                target.xposition,
                scale.top - labelfont.size,
                args_label,
              );

              ctx.lineWidth = 0.5;
              target.lines.forEach(v => {
                const ycoord = scale.getPixelForValue(v);
  
                ctx.globalAlpha = 0.8 - i * 0.05;

                ctx.beginPath();
                ctx.moveTo(scalex.left, ycoord);
                ctx.lineTo(scalex.right, ycoord);
                ctx.closePath();
                ctx.stroke();
              });
            });

            ctx.restore();
          },
        },
      ],
    });

    const timer = new PerformanceTimer();
    const blob = await this.canvas.convertToBlob();
    if(setting.debug)
      console.log(`chart graph convert blob time: ${timer.time} ms`);

    this.chart.destroy();
    this.chart = null;
    
    return blob;
  }
}
