# inf-notebook

## 使い方

### Pythonのインストール
省略

### 仮想環境を構築
```shell
python -m venv env_inf-notebook
env_inf-notebook/Scripts/Activate
```

### 必要なモジュールをインストール
```shell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 使う
```shell
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
pip install cx_Freeze==6.14.9
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
```shell
pip install google-cloud-storage
```

### 作成するバケット
- bucket-inf-notebook-informations

譜面難易度・譜面レベル・曲名・ノーツ数の含まれたリザルト画像の切り取り

- bucket-inf-notebook-details

オプション・クリアランプ・DJ LEVEL・スコア・ミスカウントの含まれたリザルト画像の切り取り

- bucket-inf-notebook-musics

曲名を画像認識する学習データ

リージョンがサウスカロライナ(us-east1)なら無料(のはず)

### サービスアカウント
作成したサービスアカウントのキーをソースに反映させる。

- (方法1)ダウンロードしたファイルを指定する
```shell
python generate_service_account_info.py ファイル名.json
```


- (方法2)base64でエンコードした文字列を引数にする
```shell
python generate_service_account_info.py 文字列
```


- (おまけ)ダウンロードしたファイルをエンコードする
```shell
python encode.py ファイル名.json
```

***
方法1はローカルでビルドするときに使う

方法2はGitHub上でActionsを利用してビルドするときに使う

おまけでエンコードした文字列をGitHubのAction secretsに追加する(名称: KEYINFO)
***

### アップロード設定
設定ファイルで収集を有効化しているときのみ、アップロードが処理される。
```json:setting.json
{
  "data_collection": true
}
```

### 収集画像を回収する
Cloud Storage上の画像を全てcollection_data下に保存し、削除する。
```shell
python download_collections.py
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
```shell
python manage.pyw
```

#### いくつかのリソースを作る
```shell
python generate_resources.py -all
```
resourcesフォルダ内にいくつかのリソースファイルが作成される。

#### 学習する
```shell
python larning_basics.py
```

#### 学習結果とラベルの照合
```shell
python evaluate_basics.py
```
evaluate_basics.csvが作成される。

### リザルトの詳細
- プレイモード(SP or DP)
- 譜面難易度と☆とノーツ数
- 曲名
- 表示しているグラフ(グルーブゲージorレーンごとDJLEVELor小節ごとの精度)
- 使用オプション(グラフがグループゲージのときのみ)
- クリアランプ・DJレベル・スコア・ミスカウント
- クリアランプ・DJレベル・スコア・ミスカウントのNEW RECORD

以上の画像認識の学習を目的とする。

#### GUI上で画像にラベル付けする
```shell
python annotation.pyw
```

#### 学習する
```shell
python larning_collection.py -all
python larning_music.py
```

#### 学習結果とラベルの照合
```shell
python evaluate_collection.py
```

evaluate_collection.csvが作成される。

#### 学習した曲名認識データをアップロードする
```shell
python upload_resource_musics.py
```
