# AKTA Plotter

AKTA / UNICORNで書き出したCSVからクロマトグラムを作成するアプリです。複数の測定結果を重ねて比較し、軸や線の見た目を調整して画像に保存できます。Windows・Mac・Linuxに対応しています。

## ダウンロード・起動

お使いのPCに合ったファイルをダウンロードして展開し、起動ファイルを開いてください。

| PC | ダウンロード | 起動ファイル |
| --- | --- | --- |
| MシリーズMac | [Mac用（Apple Silicon）](https://github.com/WassanBorn72/akta-plotter/releases/latest/download/AKTA-Plotter-macos-apple-silicon.zip) | AKTA-Plotter.app |
| Intel Mac | [Mac用（Intel）](https://github.com/WassanBorn72/akta-plotter/releases/latest/download/AKTA-Plotter-macos-intel.zip) | AKTA-Plotter.app |
| Windows（64ビット） | [Windows用](https://github.com/WassanBorn72/akta-plotter/releases/latest/download/AKTA-Plotter-windows-x64.zip) | AKTA-Plotterフォルダ内のAKTA-Plotter.exe |
| Linux（x86_64） | [Linux用](https://github.com/WassanBorn72/akta-plotter/releases/latest/download/AKTA-Plotter-linux-x64.tar.gz) | AKTA-Plotterフォルダ内のAKTA-Plotter |

Macの種類は、Appleメニュー →「このMacについて」で確認できます。「チップ」がApple Mで始まる場合はApple Silicon用、「プロセッサ」がIntelの場合はIntel用を選びます。展開したアプリは「アプリケーション」フォルダに移動できます。

Windows・Linuxでは、展開したAKTA-Plotterフォルダを丸ごと保管してください。LinuxはUbuntu 22.04以降などのデスクトップ環境が対象です。

初回起動で警告が表示される場合があります。上記リンクから入手したアプリであることを確認し、OSの許可画面から起動してください。Macでは「システム設定」→「プライバシーとセキュリティ」に許可操作が表示される場合があります。

更新内容は[リリース情報](https://github.com/WassanBorn72/akta-plotter/releases/latest)で確認できます。

## グラフを作る

1. 「CSVを追加（複数選択可）」を押して、測定結果のCSVを選びます。
2. ファイルごとの一覧で、表示したい項目にチェックを入れます。
3. 「プロット更新」を押します。

複数ファイルを選ぶと、測定結果を同じグラフに重ねられます。ファイルは後から追加することもできます。「全ファイルを解除」で最初からやり直せます。

UNICORN形式では、CSVの2行目にある「Injection」より左の数値項目を選べます。横軸は体積（mL）です。UVはmAU、導電率はmS/cmなど、縦軸は項目の単位ごとに表示されます。同じ単位の曲線は同じ縦軸を使います。

「X軸」の選択欄が表示された場合は、横軸に使う列を選んでください。

## 見た目を調整する

| 調整したいもの | 操作 |
| --- | --- |
| 線の色 | 各曲線の「色」ボタンから選択 |
| 線の太さ | 各曲線の太さ欄に数値を入力（pt） |
| タイトル | 「グラフタイトル」に入力 |
| 横軸・縦軸の範囲 | 「軸の設定」で最小値・最大値を入力 |
| 目盛り間隔 | 「軸の設定」で主目盛り・副目盛りの間隔を入力 |
| 目盛りの数値表示 | 「軸の設定」で主目盛り・副目盛りの表示を切り替え |

色・太さ・タイトルの変更後は「プロット更新」を押します。軸の変更は「適用」で反映されます。軸設定の空欄は自動調整になります。

グラフのツールバーで拡大や移動もできます。画像に保存する範囲は「軸の設定」で指定してください。

## 画像を保存する

1. 「出力解像度」を指定します。通常は200 DPI、印刷用は300 DPIが目安です。
2. 「画像を保存」を押します。
3. 形式と保存先を選びます。

| 形式 | 用途 |
| --- | --- |
| PNG | レポートやスライドへの貼り付け |
| SVG | 拡大や図の編集 |
| PDF | 印刷・共有 |

## 利用上の注意

- CSV・TSV・TXTを読み込めます。エクスポート形式によって読み込めない場合があります。
- 横軸の単位が異なる曲線は重ね合わせできません。単位換算や曲線の位置合わせは行いません。
- フラクション表示、ピーク積分、分子量校正は未対応です。

不具合は[Issues](https://github.com/WassanBorn72/akta-plotter/issues)へ、OS・エラーメッセージ・発生した操作を添えてお知らせください。

開発・ビルド手順は[開発者向けドキュメント](docs/DEVELOPMENT.md)にまとめています。
