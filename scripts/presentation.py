"""TRACE presentation assets; upstream skills remain untouched."""
import base64
import hashlib

from setup import ROOT, read_json


def font_css():
    folder = ROOT / 'assets/pretendard'
    for name, row in read_json(folder / 'source.json')['files'].items():
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Pretendard asset changed')
    font = base64.b64encode((folder / 'PretendardVariable.woff2').read_bytes()).decode('ascii')
    license_text = (folder / 'LICENSE').read_text(encoding='utf-8')
    return ('<!-- Pretendard 1.3.9 / OFL-1.1\n' + license_text + '\n-->\n'
            '<style id="trace-presentation-font">'
            '@font-face{font-family:Pretendard;src:url(data:font/woff2;base64,' + font + ') format("woff2");'
            'font-weight:100 900;font-style:normal;font-display:swap}'
            'body,button,input,select,textarea,svg text{font-family:Pretendard,system-ui,sans-serif!important}'
            '</style>')
