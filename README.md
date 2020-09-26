# GBF Search Tool

## これはなに? / What is this?
ブラウザゲーム「グランブルーファンタジー」のTwitter救援検索支援ツールです。
ボス選択画面で選んだマルチバトルの救援ツイートを検索して、もっとも新しいtweetの救援IDをクリップボードにコピーします。

*このソフトウェアの使用または使用不可によって、いかなる問題が生じた場合も、著作者はその責任を負いません。

![exsample](doc/exsample.gif)

## 動作に必要な環境 / Requirements
* Windows 10 or macOS

    Windows10とmacOS 10.14.6にて動作検証しています。環境を整えればソース自体を直接実行することでLinuxでも実行できると思われます。
* Twitter Account

    TwitterAPIの利用に必要です。
### あるとよりよいもの
* Twitter Developer Account & APIKey

    Twitterの開発者アカウントの登録とアプリケーションの登録が必要を済ませてAPIKeyを持っていると、より高い頻度でTweetを検索できるようになります。

## 実行方法 / How to Run
* 実行中は、見つけた救援IDを常にクリップボードに上書きし続けます。

### for Windows
1. [Releases](https://github.com/yume-yu/gbf_search_tool/releases)から環境にあったuser-authバージョンのzipファイルをダウンロードし解凍する
1. `run.exe`をダブルクリックする

* 初回のみ認証が必要です。アプリケーションの指示に従って認証を行ってください。

### for mac
開発環境と同様の環境を用意する。

現在pyinstallerでの作成がうまく行っていないため、実行バイナリを用意できていません

### Developer アカウントを持っている場合
1. [Releases](https://github.com/yume-yu/gbf_search_tool/releases)から環境にあったapp-authバージョンのzipファイルをダウンロードし解凍する
1. `config.toml`を編集し、API keyをセットする
1. `run.exe`をダブルクリックする

## 開発環境の構築 / Build a Dev Environment

1. Python 3.8.x が動作する環境を作る
1. リポジトリをクローンする
1. `pip install -r requirement.txt`
1. (Windowsのみ) `pip install windows-curses`
1. `config.toml.sample` をコピーし、キーをセットしてconfig.tomlを作る。
1. `python src/run.py`でアプリケーションが動作すればOK

"Copyright © 2000 yume_yu me@yume-yu.com & kumamono This work is free. You can redistribute it and/or modify it under the terms of the Do What The Fuck You Want To Public License, Version 2, as published by Sam Hocevar. See the COPYING file for more details."
