/**
 * 処理時間を計測する
 * 
 * timeプロパティでインスタンスの生成からの経過時間を取得。
 */
class PerformanceTimer {
    constructor() {
      this.starttime = performance.now();
    }
  
    get time() {
      return (performance.now() - this.starttime).toFixed(3);
    }
  }
  
/**
 * Chartが解放されるまで待つ
 * 
 * @returns 
 */
async function release_wait(chart) {
  const timer = new PerformanceTimer();

  await new Promise(resolve => {
    // console.log(`wait!!! ${chart.name}`);
    const timer = setInterval(() => {
      if(chart.canvas === null) {
        clearInterval(timer);
        resolve();
      }
    }, 50);
  });

  return timer.time;
}
