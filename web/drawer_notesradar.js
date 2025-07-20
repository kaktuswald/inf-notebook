/**
 * ノーツレーダーを描画する
 */
class DrawerNotesradar {
  static chart_notesradar_labels = ['NOTES', 'PEAK', 'SCRATCH', 'SOF-LAN', 'CHARGE', 'CHORD'];
  static chart_notesradar_bordercolors = [
    'rgba(237, 60, 189, 1)',
    'rgba(253, 107, 0, 1)',
    'rgba(255, 30, 96, 1)',
    'rgba(1, 125, 213, 1)',
    'rgba(136, 86, 219, 1)',
    'rgba(112, 204, 0, 1)',
  ];
  static chart_notesradar_backgroundcolors = [
    'rgba(237, 60, 189, 0.5)',
    'rgba(253, 107, 0, 0.5)',
    'rgba(255, 30, 96, 0.5)',
    'rgba(1, 125, 213, 0.5)',
    'rgba(136, 86, 219, 0.5)',
    'rgba(132, 224, 0, 0.5)',
  ];

  canvas = null;

  /**
   * ノーツレーダー描画用のオブジェクト
   * 
   * playmode, canvas, chartを持つ。
   */
  targets = [];

  draw_text = function(text, x, y, args) {
    ctx.fillText(text, x, y);
  }

  /**
   * @param {Array<string>} playmodes プレイモードのリスト
   * @param {Bigint} width キャンパスの幅
   * @param {Bitint} height キャンパスの高さ
   */
  constructor(playmodes, width, height) {
    this.canvas = new OffscreenCanvas(width, height);

    for(const playmode of playmodes) {
      this.targets.push({
        playmode: playmode,
        canvas: new OffscreenCanvas(width / 2, height),
        chart: null,
      });
    }
  }

  /**
   * ノーツレーダーを描画する
   * @param {Object.<string, Object.<string, Array<Number>>>} targetvalues 対象のノーツレーダー値
   * @returns {blob} 画像データ
   */
  async draw(targetvalues) {
    const ctx = this.canvas.getContext('2d');

    ctx.save();

    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    for(let i = 0; i < this.targets.length; i++) {
      if(i >= targetvalues.length) continue;

      const playmode = this.targets[i].playmode;
      
      if(this.targets[i].chart) this.targets[i].chart.destroy();

      const values = [];
      DrawerNotesradar.chart_notesradar_labels.forEach((label) => {
        values.push(targetvalues[playmode][label]);
      })

      const sum = values.reduce((accumulator, currentValue) => accumulator + currentValue);
      const maxvalue = Math.max(values[0], values[1], values[2], values[3], values[4], values[5]);
      const bordercolor = DrawerNotesradar.chart_notesradar_bordercolors[values.indexOf(maxvalue)];
      const backgroundcolor = DrawerNotesradar.chart_notesradar_backgroundcolors[values.indexOf(maxvalue)];

      const targetcanvas = this.targets[i].canvas;

      this.targets[i].chart = new Chart(targetcanvas, {
        type: 'radar',
        data: {
          labels: DrawerNotesradar.chart_notesradar_labels,
          datasets: [{
            data: values,
            borderWidth: 1,
            borderColor: bordercolor,
            backgroundColor: backgroundcolor,
          }],
        },
        options: {
          layout: {
            padding: {
              bottom: 30,
            },
          },
          scales: {
            r: {
              beginAtZero: true,
              max: 200.0,
              ticks: {
                min: 0.0,
                max: 50.0,
                stepSize: 50,
                display: false,
              },
              pointLabels: {
                padding: -60,
              },
              grid: {
                display: false,
              },
            },
          },
          elements: {
            point: {
              radius: 0,
            },
          },
          plugins: {
            title: {
              display: true,
              text: `${playmode} ${sum.toFixed(2)}`,
              color: 'white',
              font: {
                size: 60,
              },
              padding: {
                bottom: 40,
              },
            },
            legend: false,
          },
        },
        plugins: [
          {
            beforeDraw: (chart) => {
              const ctx = chart.ctx;

              const chartarea = chart.chartArea;
              const scale = chart.scales['r'];
    
              const centerx = (chartarea.left + chartarea.right) / 2;
              const centery = (chartarea.top + chartarea.bottom) / 2;
              const radius = scale.getDistanceFromCenterForValue(100);

              ctx.save();

              ctx.fillStyle = 'gray',

              ctx.beginPath();
              ctx.arc(centerx, centery, radius, 0, 2 * Math.PI);
              ctx.fill();

              ctx.restore();

              chart.titleBlock.options.display = false;
              scale.options.pointLabels.display = false;
            },
            afterDraw: (chart) => {
              const ctx = chart.ctx;
              
              const titleblock = chart.titleBlock;
              const scale = chart.scales['r'];
    
              const titlefont = titleblock.options.font;
              const titletext = titleblock.options.text;
              const titlecenterx = (titleblock.left + titleblock.right) / 2;
              const titlecentery = (titleblock.top + titleblock.bottom) / 2;

              const args_title = {
                'textcolor': 'white',
                'shadowcolor': 'black',
                'fontsize': titlefont.size,
              };

              const args_value = {
                'textcolor': 'white',
                'shadowcolor': null,
                'fontsize': 38,
              };

              const args_label = {
                'textcolor': 'white',
                'shadowcolor': null,
                'fontsize': 24,
              };

              ctx.save();

              ctx.font = `${titlefont.weight} ${titlefont.size}px ${Chart.defaults.font.family}`;
              ctx.textAlign = titleblock.options.align;
              this.draw_text(ctx, titletext, titlecenterx, titlecentery, args_title);

              chart.data.labels.forEach((label, index) => {
                const value_text = values[index].toFixed(2);
                const position = scale.getPointLabelPosition(index);
                const x = (position.left + position.right) / 2;
                const y = position.bottom;

                args_value.shadowcolor = DrawerNotesradar.chart_notesradar_bordercolors[index];
                args_label.shadowcolor = DrawerNotesradar.chart_notesradar_bordercolors[index];

                ctx.textAlign = 'center';

                let valuey;
                if(y < scale.yCenter)
                  valuey = y - 26;
                else
                  valuey = y + 36;

                ctx.font = `38px ${Chart.defaults.font.family}`;
                this.draw_text(ctx, value_text, x, valuey, args_value);

                ctx.font = `24px ${Chart.defaults.font.family}`;
                this.draw_text(ctx, label, x, y, args_label);
              });

              ctx.restore();
            },
          },
        ],
      });

      const image = await new Promise((resolve, reject) => {
        targetcanvas.convertToBlob().then((blob) => {
          const image = new Image();
          image.onload = () => resolve(image);
          image.src = URL.createObjectURL(blob);
        });
      });

      ctx.drawImage(image, i * image.width, 20, image.width, image.height * 1);
    }

    ctx.restore();

    return await this.canvas.convertToBlob();
  }
}