# 開発者向けドキュメント

利用者向けの操作手順は [README](../README.md) を参照してください。

## 開発環境

Python 3.12を推奨します（ソースコードはPython 3.10以上を対象）。Tkと、GUIを表示できるデスクトップ環境が必要です。Windowsでは公式PythonのTcl/Tkを有効にしてください。Macでは利用するPythonに対応するTk、Linuxではディストリビューションのpython3-tkを導入してください。

既存のチェックアウトを使用し、プロジェクトのルートで実行します。

```sh
python -m venv .venv
```

Windowsでは `.venv\Scripts\activate`、Mac / Linuxでは `source .venv/bin/activate` で仮想環境を有効にします。Mac / Linuxで `python` が見つからない場合、仮想環境の作成には `python3` を使用してください。

```sh
python -m pip install -r requirements.txt
python -m akta_plotter.desktop
```

## コード構成

| ファイル | 役割 |
| --- | --- |
| akta_plotter/data.py | CSVの読み込み、信号名・単位・対応する体積列の検出 |
| akta_plotter/plot.py | 複数曲線の描画、単位別の軸、設定値の検証 |
| akta_plotter/desktop.py | Tkの操作画面 |
| scripts/desktop_entry.py | 配布版の起動と同梱環境の検証 |
| scripts/build_desktop.py | 現在のOS向けのPyInstallerビルド |

## データ形式

UTF-8・BOM付きUTF-16・CP932・CP1252を試行します。コンマ・セミコロン・タブ区切りを判定します。

UNICORN形式では2行目に信号名、3行目に単位、4行目以降に数値を想定します。列の位置に関係なくmL列と数値信号列のペアを抽出します。2行目の信号名がInjection、Run Log、Fraction、UV 1_280_CUT_TEMP@100,BASEMに完全一致するペアを除外します（前後の空白・大文字小文字の差は無視）。部分一致では除外しません。信号ごとにX列と有効な測定点数が異なることがあります。単位換算は行わず、ml / mLの横軸表記のみ正規化します。単位が空のペアはunitless軸にまとめます。

一般的な表形式ではX列を手動選択します。自動形式判定は、すべてのUNICORNバージョンへの対応を保証するものではありません。

## テスト

配布版の互換性検査も含めるため、ビルド用の依存関係を導入して実行します。

```sh
python -m pip install -r requirements-build.txt
python -m unittest discover -s tests -v
```

テストはCSV解析、UTF-16、欠損値、重複ヘッダー、小数コンマ、信号固有のX列、Injectionの左右の信号抽出、指定名の除外、単位別の軸、重ね合わせ、軸範囲・目盛り・ラベル表示、線の色・太さ、不正入力、PNG/SVG/PDF出力を検証します。

サンプルは `examples/demo.csv` と `examples/mixed_units.tsv` です。利用者から提供された実機CSVでUV 3_480 / UV 1_280の座標と画像出力を確認していますが、そのCSVはリポジトリに含めていません。

書き込みが制限された環境では、Matplotlibのキャッシュを利用可能な場所に設定します。例：

```sh
mkdir -p /tmp/akta-mpl /tmp/akta-cache
export MPLCONFIGDIR=/tmp/akta-mpl
export XDG_CACHE_HOME=/tmp/akta-cache
```

## 配布版のビルド

対象OS上のPython 3.12とTkを使用します。別OS向けにクロスコンパイルすることはできません。

```sh
python -m venv .build-venv
```

Windowsは `.build-venv\Scripts\activate`、Mac / Linuxは `source .build-venv/bin/activate` で有効にします。

```sh
python -m pip install -r requirements-build.txt
python -m unittest discover -s tests -v
python scripts/build_desktop.py
```

出力先は `dist/` です。診断用のコンソール付きビルドは `python scripts/build_desktop.py --console` です。生成物や仮想環境はコミットしません。

### 同梱環境の検証

Linuxの例：

```sh
dist/AKTA-Plotter/AKTA-Plotter --self-test
xvfb-run -a dist/AKTA-Plotter/AKTA-Plotter --gui-smoke-test
```

GUIが使える場合はxvfb-runは不要です。Windowsの起動ファイルは `dist/AKTA-Plotter/AKTA-Plotter.exe`、Macは `dist/AKTA-Plotter.app/Contents/MacOS/AKTA-Plotter` です。

`--self-test` は同梱環境でCSV・描画・画像出力を確認します。`--gui-smoke-test` はGUIを生成し、2ファイルの重ね合わせと画像保存を実行して終了します。Linuxクラウド環境では、ソースと配布版の両方でこれらのチェックを通過しています。OS別のビルド成功は、それぞれのCI実行結果で確認してください。

### GitHub Actions

[Build desktop applications](https://github.com/WassanBorn72/akta-plotter/actions/workflows/build-desktop.yml)は、対象コード・依存定義・ワークフローのmainへのpush、vで始まるタグ、またはRun workflowで実行します。Windows x64、Intel Mac、Apple Silicon Mac、Ubuntu 22.04 x64でネイティブビルドし、テストと同梱環境の検証後にアーカイブをArtifactsへ保存します。

LinuxのCI配布版はglibc 2.35以上のGUI環境を対象とします。異なるLinux環境でローカルビルドした場合、必要なglibcバージョンはビルド環境に依存します。Macはdittoで.appをZIP化し、Windows / Linuxはフォルダ全体を配布します。

コード署名・Apple公証・インストーラー・自動アップデートは未実装です。

## 正式リリース

アプリのバージョンは `akta_plotter/__init__.py` の `__version__` に記載します。対応するリリースノートを `docs/releases/v<version>.md` に作成し、変更をmainへ反映してから同じバージョンのタグをpushします。例：

```sh
git tag -a v1.0.0 -m "AKTA Plotter v1.0.0"
git push origin v1.0.0
```

タグのCIではバージョン一致を確認し、4種類のネイティブビルドとテストがすべて成功した後だけreleaseジョブが実行されます。アーカイブ内の起動ファイルと整合性を検証し、SHA256SUMS.txtを生成します。releaseジョブは全ファイルを下書きへ添付した後に正式公開するため、ビルドが欠けた状態で公開しません。GitHub ActionsのGITHUB_TOKENを使用し、書き込み権限はreleaseジョブだけに付与します。

公開失敗時に下書きが残っていれば、同じタグのCIを再実行すると添付を更新して公開できます。公開済みのリリースは上書きしません。不具合修正は次のバージョンで公開してください。

## アプリアイコン

専用のピーク形状のアイコンを `akta_plotter/assets/` に保存しています。PNGはTk画面用、ICOはWindows実行ファイル用、ICNSはMacアプリ用です。PyInstallerはこれらを同梱し、OSに応じたアイコンを設定します。LinuxはアプリのウィンドウアイコンにPNGを使用します。

アイコンの元画像を変更する場合は、正方形の画像を指定して各形式を再生成します。

```sh
python scripts/convert_icon.py path/to/artwork.png
```

配布版のGUIチェックでは、同梱PNGが読み込めることも確認します。

## macOSの最低対応バージョン

配布版はmacOS 12.0以降を対象にします。CIの依存ダウンロードに `--platform macosx_12_0_arm64` / `macosx_12_0_x86_64` を指定し、ビルドマシンの新しいOSにだけ対応したwheelを避けます。NumPyは同じバージョンでもmacOS 11用と14用のwheelがあり、通常のpip installではビルドマシンに合わせて14用が選ばれることがあります。

バンドルのLSMinimumSystemVersionを12.0に設定し、全Mach-OファイルのLC_BUILD_VERSION / LC_VERSION_MIN_MACOSXを `scripts/check_macos_target.py` で検査します。メタデータだけを変更して非互換のバイナリを通すことはしません。CIの起動検証は新しいOS上で行われるため、macOS 12実機での動作確認は別途必要です。
