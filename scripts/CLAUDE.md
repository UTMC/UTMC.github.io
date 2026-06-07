# https://www.utmc.or.jp/ メンテナス用ツール群

* `make-ogp-image.py` : OGP用の画像を生成するPython3 スクリプト

## 全体の設定

* pytnon3 を使う
* uv で管理

## make-ogp-image.py の仕様

* 引数に指定した HTML を parse して、og:title と og:site_name、og:description を抽出し、タイトル、サイト名、説明を得る
* 生成するOGP画像は 1200x630 px
* 背景は白
* 画像の左の真ん中に ../files/utmclogo.svg のロゴを埋め込む
* 画像の右側は上側に大きめの文字でタイトル、下側に小さめの文字で説明、下右橋にサイト名を小さく書く
* Python の pillow ライブラリを使う
* 生成した画像データは og:image に指定されているファイル名で保存する