# sync-playlist-gmusic

## 概要
itunesのプレイリスト情報をgoogle-play-musicと同期させます。
スマートプレイリストについてはiTunesの管理ファイルの構造上曲順は同じにはなりません。

## 使い方

### 使用ライブラリの事前インストール

```bash
pip libpytunes gmusicapi python-dotenv
```

### google-play-musicのログイン情報取得

oauth.pyを実行してgoogleにログインしてgoogle play musicへのアクセスを許可します。

### iTunes Library.xmlファイルのエクスポート

iTunesから「iTunes Library.xml」をエクスポートしておきの配置先パスを控えておきます。

### .envファイルの準備

.env.exampleをコピーして.envファイルにリネームし、`ITUNES_MUSIC_LIBLARY_XML_PATH`へ「iTunes Library.xml」のパスを指定します。

### 同期の実行

sync-playlist.pyを実行してプレイリスト情報の同期を実行します。

```bash
python sync-playlist.py
```

件数が多すぎる場合はgoogle側のAPIでエラーが発生する場合があります。
その場合は再実行してみてください。

### その他

sync-playlist_old.py
同期するplaylistが存在する場合に該当のプレイリストを削除する方式のプログラムです。

clear-playlist.py
google play musicのプレイリストを全削除します。

### 利用ライブラリ

以下のライブリを利用させて頂いています。
libpytunes
https://github.com/liamks/libpytunes

gmusicapi
https://github.com/simon-weber/gmusicapi

python-dotenv
https://github.com/theskumar/python-dotenv
