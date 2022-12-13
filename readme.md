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

WindowsのPowerShellで操作する

### バージョンの更新
```shell
python generate_version.py v0.0.0.0
```

### 実行ファイル化
```shell
pip install cx_Freeze
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

## 学習する

### 基本的なところ
- INFINITAS画面位置の検出
- リザルト画面の検出
- ミッション・ビット獲得のカットインが出ていないことの判断
- プレイサイドの認識(1P or 2P)
- ライバル挑戦状が出ているかどうか

以上の画像認識の学習を目的とする。

#### GUI上で画像にラベル付けする
```
python manage.pyw
```

#### 学習する
```
python larning_basics.py
```

#### 学習結果とラベルの照合
```
python evaluate_basics.py
```
evaluate_basics.csvが作成される。

### リザルトの詳細
- プレイモード(SP or DP)
- 譜面難易度と☆
- 曲名(未実装)
- 使用オプション
- クリアランプ・DJレベル・スコア・ミスカウント
- クリアランプ・DJレベル・スコア・ミスカウントのNEW RECORD

以上の画像認識の学習を目的とする。

#### GUI上で画像にラベル付けする
```
python annotation.pyw
```

#### 学習する
```
python larning_collection.py
python larning_music.py
```

#### 学習結果とラベルの照合
```
python evaluate_collection.py
```
evaluate_collection.csvが作成される。
