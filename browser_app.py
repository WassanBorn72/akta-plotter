import hashlib
import io
import streamlit as st
from akta_plotter.data import read_export, label
from akta_plotter.plot import COLORS, Curve, make_overlay, parse_axis


def axis_controls(name, key):
    with st.expander(name):
        cols = st.columns(4)
        values = [col.text_input(text, key=f'{key}-{i}', help='空欄は自動設定です。')
                  for i, (col, text) in enumerate(zip(cols, ['最小値', '最大値', '主目盛り間隔', '副目盛り間隔']))]
        major = st.checkbox('主目盛りの数値を表示', value=True, key=key + '-major')
        minor = st.checkbox('副目盛りの数値を表示', value=False, key=key + '-minor')
    return parse_axis(values, major, minor)


st.set_page_config(page_title='AKTA Plotter', layout='wide')
st.title('AKTA Plotter')
st.caption('複数CSVの曲線を重ね合わせ、軸・線の設定を調整して画像を保存できます。')
uploads = st.file_uploader('CSV / TSVファイル（複数選択可）', type=['csv', 'tsv', 'txt'], accept_multiple_files=True)
if uploads:
    curves = []
    for index, upload in enumerate(uploads):
        raw = upload.getvalue()
        prefix = f'file-{index}-{hashlib.sha256(raw).hexdigest()[:12]}'
        source = f'{index + 1}: {upload.name}'
        with st.expander(source, expanded=True):
            try:
                export = read_export(raw)
                if export.signal_x:
                    x = None
                    candidates = list(export.signal_x)
                    st.caption('X: mL · Injectionより左の数値曲線')
                else:
                    x = st.selectbox('X軸', list(export.frame), key=prefix + '-x')
                    candidates = [c for c in export.frame if c != x]
                ys = st.multiselect('表示する曲線', candidates, default=candidates[:1],
                                    format_func=lambda name: label(export, name), key=prefix + '-ys')
                for y in ys:
                    key = prefix + '-' + y
                    left, right = st.columns(2)
                    color = left.color_picker(f'{y} の線の色', COLORS[len(curves) % len(COLORS)], key=key + '-color')
                    width = right.number_input(f'{y} の線の太さ', min_value=.1, max_value=20., value=1.5, step=.1, key=key + '-width')
                    curves.append(Curve(export, y, x, source, color, width))
                st.caption(f'{len(export.frame)}行・文字コード: {export.encoding}')
            except Exception as exc:
                st.error(f'{upload.name}: {exc}')
    try:
        title = st.text_input('グラフタイトル', 'AKTA overlay')
        x_settings = axis_controls('横軸の設定', 'axis-x')
        y_settings = {unit: axis_controls(f'縦軸の設定 [{unit}]', 'axis-y-' + unit)
                      for unit in dict.fromkeys(c.unit for c in curves)}
        dpi = st.number_input('出力解像度 (DPI)', min_value=72, max_value=600, value=200, step=10)
        if curves:
            figure = make_overlay(curves, title, x_settings, y_settings)
            st.pyplot(figure)
            for extension, mime in [('png', 'image/png'), ('svg', 'image/svg+xml'), ('pdf', 'application/pdf')]:
                buffer = io.BytesIO()
                figure.savefig(buffer, format=extension, dpi=dpi)
                st.download_button(f'{extension.upper()}を保存', buffer.getvalue(), f'akta_plot.{extension}', mime=mime)
        else:
            st.info('表示する曲線を選択してください。')
    except Exception as exc:
        st.error(str(exc))
