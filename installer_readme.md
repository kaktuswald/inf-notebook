### 仮想環境を構築
```shell
python -m venv env_build_installer
env_build_installer/Scripts/Activate
```

### 必要なモジュールをインストール
```shell
python -m pip install --upgrade pip
pip install -r installer_requirements.txt
```

### ビルドする
```shell
python installer_setup.py build
```
