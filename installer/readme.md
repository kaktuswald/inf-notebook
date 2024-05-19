### 仮想環境を構築
```shell
python -m venv env_build
env_build/Scripts/Activate
```

### 必要なモジュールをインストール
```shell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### ビルドする
```shell
python setup.py build
```
