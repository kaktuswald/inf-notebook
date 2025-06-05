# inf-notebook

## 使い方

### Pythonのインストール
省略

### 仮想環境を構築
```shell
python -m venv env_inf-notebook
py -3.12 -m venv env_inf-notebook
env_inf-notebook/Scripts/Activate
```

### 必要なモジュールをインストール
```shell
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
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
- Alt+F10でスクリーンショットを撮ってファイル保存する
- 標準出力がウィンドウに表示される

## ビルド

WindowsのPowerShellで操作する

### バージョンの更新
```shell
python generate_version.py v0.0.0.0
```

### 実行ファイル化
```shell
pip install cx_Freeze==8.3.0
python setup.py build
```

## INFINITAS画面画像の収集と学習
リザルト手帳を起動してAlt+F10を押すとスクリーンショットを撮って画像に保存する

収集した画像を使って学習させ、リソースファイルを作成する

### 基本的なところ
- ローディング画面の検出
- リザルト画面(ミッション・ビット獲得のカットインや撃墜の文字が出ていない)の検出
- プレイサイドの認識(1P or 2P)
- ライバル挑戦状が出ているかどうか
- 途中落ちしているかどうか

以上の画像認識の学習を目的とする。

#### GUI上で画像にラベル付けする
```shell
python manage.pyw
```

#### いくつかのリソースを作る
```shell
python resources_generate_fromraw.py -all
python resources_learning_fromraw.py -all
```
エラーが出なければOK

resourcesフォルダ内にいくつかのリソースファイルが作成される。
- get_screen.res
- is_savable.res
- rival.npy
- play_side.npy
- dead.npy

### 選曲画面
- プレイモード(SP or DP)
- 曲名
- 選択中の譜面難易度
- 各譜面難易度のレベル
- クリアランプ・DJレベル・スコア・ミスカウント

#### GUI上で画像にラベル付けする
```shell
python annotation_musicselect.pyw
```

#### 学習する
```shell
python resources_learning_musicselect.py
```

resourcesフォルダ内にリソースファイルが作成される。
- musicselect(バージョン).res

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

- bucket-inf-notebook-resources

認識用のリソースデータ

学習後の最新のリソースをアップロードして、クライアント起動時にチェックして最新版をダウンロードする

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

### リザルトの詳細と曲リスト
曲リスト
- 全曲の曲名ソート順の曲リスト
- バージョンごとの曲リスト
- レベルごとの曲リスト
- ビギナーとレジェンダリアの曲リスト

リザルトの詳細
- プレイモード(SP or DP)
- 譜面難易度と☆とノーツ数
- 曲名
- 表示しているグラフ(グルーブゲージorレーンごとDJLEVELor小節ごとの精度)
- 使用オプション(グラフがグループゲージのときのみ)
- クリアランプ・DJレベル・スコア・ミスカウント
- クリアランプ・DJレベル・スコア・ミスカウントのNEW RECORD

選曲
- プレイモード(SP or DP)
- バージョン
- 曲名
- 各譜面のレベル
- 自己ベストのクリアランプ・DJレベル・スコア・ミスカウント

以上の画像認識の学習と全収録曲のリストの作成を目的とする。

#### 収録曲情報
registriesフォルダに各種ファイルを作っておく。
- versions.txt バージョンのリスト
- musics.csv 全曲のリスト
- categorycount_versions.csv バージョンカテゴリの各曲数
- categorycount_difficulties.csv 難易度カテゴリの各曲数(BEGINNER,LEGGENDARIA)
- categorycount_levels.csv レベルカテゴリの各曲数

#### GUI上で画像にラベル付けする
```shell
python annotation_musicselect.pyw
python annotation_result.pyw
```

##### 曲リストの作成
musics.csvから曲リストを作成して、収集した選曲画面のラベルから各譜面のレベルを取り込む。
アーケードのCSVデータファイルをダウンロードして、
originalscoredata_sp,originalscoredata_dpフォルダにおいておく。
アーケードデータとの収録曲やレベルの比較を行う。
各カテゴリの曲数を照合する。

```shell
python resources_generate_musictable.py
```

#### 学習する
```shell
python resources_learning_informations.py
python resources_learning_details.py
python resources_learning_musicselect.py
```

#### 誤った曲名の修正
記録を保存するファイルのファイル名に「曲名をエンコードした文字列」を使用している。

そのため曲名の修正があった場合は該当ファイルのファイル名を変更する必要がある。

その定義をresources/musicnamechanges.resに記述する(中身はjson)
```json
[
    ["♥LOVE2 シュガー→♥", "♥LOVE2 シュガ→♥"]
]
```

resourcesフォルダに以下ファイルが作成される。
- musictable(バージョン).res
- informations(バージョン).res
- detailss(バージョン).res
- musicselect(バージョン).res

#### 学習した曲名認識データをアップロードする
すべての場合
```shell
python resources_upload.py -all
```

指定したリソースファイルのみアップロードする場合
```shell
python resources_upload.py -musictable
python resources_upload.py -informations
python resources_upload.py -details
python resources_upload.py -musicselect
python resources_upload.py -musicnamechanges
```
