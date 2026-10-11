# AKTA Plotter

AKTA / UNICORNで書き出したCSVからクロマトグラムを作成するアプリです。複数の測定結果を重ねて比較し、軸や線の見た目を調整して画像に保存できます。Windows・macOS 12（Monterey）以降・Linuxに対応しています。

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
3. 左側の設定欄の下部にある、青い枠の「プロット更新」ボタンを押します。

複数ファイルを選ぶと、測定結果を同じグラフに重ねられます。ファイルは後から追加することもできます。「全ファイルを解除」で最初からやり直せます。

UNICORN形式では、CSVの2行目が「Injection」「Run Log」「Fraction」「UV 1_280_CUT_TEMP@100,BASEM」の項目を除き、数値項目を選べます。列の位置に関係なく、Injectionより右の項目も対象です。横軸は体積（mL）です。UVはmAU、導電率はmS/cmなど、縦軸は項目の単位ごとに表示されます。同じ単位の曲線は同じ縦軸を使います。

「X軸」の選択欄が表示された場合は、横軸に使う列を選んでください。

## 見た目を調整する

| 調整したいもの | 操作 |
| --- | --- |
| 線の色 | 各曲線の「色」ボタンから選択 |
| 線の太さ | 各曲線の太さ欄に数値を入力（pt） |
| タイトル | 「グラフタイトル」に入力 |
| 横軸・縦軸の範囲 | 「軸の設定」で最小値・最大値を入力 |
| 目盛り間隔 | 「軸の設定」で主目盛り・副目盛りの間隔を入力 |
| 軸の名前 | 「軸の設定」で横軸・単位ごとの縦軸の名前を入力 |
| 目盛りの向き | 「軸の設定」で内向き・外向き・交差を選択 |
| 軸・目盛りの太さ、文字サイズ | 「軸の設定」で太さと、目盛り・軸名の文字サイズを指定（pt） |
| キャプション（凡例）の文字 | 各曲線の「凡例」欄に入力（空欄はファイル名と項目名） |
| キャプション（凡例）の表示 | 「キャプション（凡例）を表示」を切り替え |
| 外枠・罫線 | 「外枠を表示」「罫線を表示」を切り替え |
| 目盛りの数値表示 | 「軸の設定」で主目盛り・副目盛りの表示を切り替え |

色・太さ・タイトル・凡例・外枠・罫線の変更後は「プロット更新」を押します。軸の変更は「適用」で反映されます。範囲・間隔の空欄は自動調整、軸名の空欄は単位の表示になります。外枠を非表示にすると上辺と囲みの右辺が消え、横軸・縦軸の線は残ります。単位ごとの右側の縦軸も残ります。

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
