# inf-notebook

## 使い方

### Pythonのインストール
省略

### 必要なモジュールをインストール
```
python -m pip install --upgrade pip
pip install numpy keyboard pillow PyAutoGUI PySimpleGUI
```

### 使う
```
python main.pyw
```

### マネージモード
設定ファイルに記述を追加するとmain.pywがマネージモードで走る。
```json:setting.json
{
  "manage": true
}
```
- スクリーンショットのリアルタイム更新ができる
- スクリーンショット代わりにpngが開ける
- Ctrl+F10でスクリーンショットを撮ってファイル保存する
- 標準出力がウィンドウに表示される

## ビルド

### 実行ファイル化
WindowsのPowerShellで
```
pip install cx_Freeze
echo 0.0.0.0 > VERSION.txt
python setup.py build
```

## リザルト画像の収集と学習

### GCPの操作
- プロジェクトを作成
- Cloud Storageバケットを作成
- サービスアカウントの作成(accessor)
- ロールを与える(Storage オブジェクト管理者 もしくは ストレージ管理者)
- キーを作成
- pythonライブラリのインストール
```
pip install google-cloud-storage
```

### サービスアカウント
作成したサービスアカウントのキーをソースに反映させる。

- (方法1)ダウンロードしたファイルを指定する
```
python generate_service_account_info.py ファイル名.json
```

- (方法2)base64でエンコードした文字列を引数にする
```
python generate_service_account_info.py 文字列
```

- (おまけ)ダウンロードしたファイルをエンコードする
```
python encode.py ファイル名.json
```

### アップロード設定
設定ファイルで収集を有効化しているときのみ、アップロードが処理される。
```json:setting.json
{
  "data_collection": true
}
```

### 収集画像を回収する
Cloud Storage上の画像を全てcollection_data下に保存し、削除する。
```
python download.py
```

<!--
大幅仕様変更に未対応のためコメントアウト中
### アノテーションする
```
python annotation.pyw
```

### 学習させる
```
python larning.py
```
defineフォルダに各種画像ファイルを作成される

### 認識結果の評価
```
python evaluate.py
```
結果ファイルのevaluate.csvが作成される
-->