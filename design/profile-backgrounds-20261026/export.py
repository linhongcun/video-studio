"""Export original backgrounds, profile mockups, comparison sheets and ZIP."""
import json
from pathlib import Path
import shutil
import struct
from urllib.parse import quote
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ITEMS = json.loads((ROOT / 'catalog.json').read_text())
OVERLAY = (ROOT / 'profile-overlay.svg').read_text()
for folder in ['png', 'profile-previews', 'review']:
    (ROOT / folder).mkdir(exist_ok=True)

def uri(svg):
    return 'data:image/svg+xml;charset=utf-8,' + quote(svg)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1500, 'height': 1500}, device_scale_factor=1)
    for item in ITEMS:
        svg = ET.fromstring(item['svg'])
        assert svg.attrib['viewBox'] == '0 0 1500 1500'
        assert svg.attrib['width'] == svg.attrib['height'] == '1500'
        page.set_content('<style>body{margin:0}svg{display:block;width:100vw;height:100vh}</style>' + item['svg'])
        target = ROOT / 'png' / f'{item["id"]}-{item["slug"]}.png'
        page.screenshot(path=str(target))
        assert struct.unpack('>II', target.read_bytes()[16:24]) == (1500, 1500)
        page.set_content('<style>body{margin:0}main{position:relative;width:1500px;height:1500px}img{width:100%;height:100%;display:block}.overlay{position:absolute;inset:0}</style><main><img src="' + uri(item['svg']) + '"><img class="overlay" src="' + uri(OVERLAY) + '"></main>')
        page.locator('img').first.wait_for(state='visible')
        page.wait_for_function('Array.from(document.images).every(x=>x.complete&&x.naturalWidth>0)')
        page.screenshot(path=str(ROOT / 'profile-previews' / f'{item["id"]}-{item["slug"]}-preview.png'))

    def sheet(profile=False):
        cards = ''.join('<article><div class="art"><img src="' + uri(x['svg']) + '">'
                        + ('<img class="overlay" src="' + uri(OVERLAY) + '">' if profile else '')
                        + '</div><div class="label"><span>' + x['id'] + '</span><strong>' + x['name'] + '</strong></div></article>' for x in ITEMS)
        title = 'IT小村 · 主页背景效果' if profile else 'IT小村 · 主页背景候选'
        note = '头像与资料叠加示意，方便比较白字显示；下载原图不含文字与头像。' if profile else '为「代码小村」头像搭配的 8 款纯背景　/　深蓝 · 薄荷 · 少量暖金'
        return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><style>*{box-sizing:border-box}body{margin:0;background:#f1f1e9;color:#213b35;font-family:"Noto Sans CJK SC",sans-serif}main{width:2000px;padding:48px 55px 35px}header{display:flex;justify-content:space-between;align-items:end;padding-bottom:25px;border-bottom:1px solid #d1d9ca;margin-bottom:30px}h1{font-size:37px;margin:0 0 12px;letter-spacing:-.03em}header p{margin:0;color:#718674;font-size:17px}header span{font:14px monospace;color:#79907d;letter-spacing:.06em}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:28px 25px}.art{aspect-ratio:1;position:relative;border-radius:13px;overflow:hidden;background:#101d2d}img{display:block;width:100%;height:100%}.overlay{position:absolute;inset:0}.label{display:flex;gap:13px;align-items:center;margin-top:14px}.label span{font:17px monospace;color:#7e927d}.label strong{font-size:22px;font-weight:650}footer{margin-top:30px;border-top:1px solid #d1d9ca;padding-top:20px;display:flex;justify-content:space-between;color:#748975;font-size:15px}</style><main><header><div><h1>' + title + '</h1><p>' + note + '</p></div><span>08 BACKGROUNDS / 2026.10</span></header><section class="grid">' + cards + '</section><footer><span>告诉我喜欢的编号，可以沿着那个方向继续调整。</span><span>原图 1500 × 1500 PNG + SVG　·　按截图可见区域设计</span></footer></main></html>'

    page.set_viewport_size({'width': 2000, 'height': 1450})
    for profile in [False, True]:
        page.set_content(sheet(profile))
        page.wait_for_function('Array.from(document.images).every(x=>x.complete&&x.naturalWidth>0)')
        page.locator('main').screenshot(path=str(ROOT / ('profile-contact-sheet.png' if profile else 'contact-sheet.png')))

    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.set_content((ROOT / 'index.html').read_text(), wait_until='load')
    page.wait_for_function('Array.from(document.images).every(x=>x.complete&&x.naturalWidth>0)')
    assert page.locator('.card').count() == 8
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.locator('[data-view="profile"]').click()
    assert page.locator('main').evaluate('x=>x.classList.contains("profile")')
    page.locator('[data-open="01"]').click()
    assert page.locator('dialog').evaluate('x=>x.open')
    assert page.locator('dialog .compare>div').count() == 2
    with page.expect_download() as event:
        page.locator('dialog [data-png="01"]').click()
    downloaded = ROOT / 'review' / 'download-check.png'
    event.value.save_as(str(downloaded))
    assert struct.unpack('>II', downloaded.read_bytes()[16:24]) == (1500, 1500)
    downloaded.unlink()
    page.keyboard.press('Escape')
    assert not page.locator('dialog').evaluate('x=>x.open')
    page.locator('[data-view="original"]').click()
    page.mouse.move(0, 0)
    page.evaluate('document.activeElement.blur()')
    page.screenshot(path=str(ROOT / 'review/gallery-desktop.png'), full_page=True)
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.locator('[data-open="05"]').click()
    assert page.locator('dialog').evaluate('x=>x.open')
    page.locator('dialog .close').click()
    page.evaluate('document.activeElement.blur()')
    page.screenshot(path=str(ROOT / 'review/gallery-mobile.png'), full_page=True)
    assert not errors, errors
    browser.close()

report = {'originals': 8, 'originalSize': '1500 × 1500', 'profilePreviews': 8,
          'originalContents': 'Vector graphics only; no text, avatar, UI, raster images or external resources',
          'galleryChecks': 'Desktop/mobile layout, mode toggle, comparison dialog, Escape/close, clean PNG download passed',
          'viewports': [1440, 390], 'consoleErrors': errors}
(ROOT / 'review/checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
bundle = ROOT / 'it-village-backgrounds-8.zip'
with ZipFile(ROOT / 'it-village-backgrounds-png.zip', 'w', ZIP_DEFLATED) as archive:
    for path in sorted((ROOT / 'png').glob('*.png')):
        archive.write(path, Path('it-village-backgrounds-png') / path.name)
with ZipFile(bundle, 'w', ZIP_DEFLATED) as archive:
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and path.suffix != '.zip' and '__pycache__' not in path.parts:
            archive.write(path, Path('it-village-backgrounds-8') / path.relative_to(ROOT))
with ZipFile(bundle) as archive:
    assert archive.testzip() is None
    assert sum('/png/' in x and x.endswith('.png') for x in archive.namelist()) == 8
print(json.dumps(report, ensure_ascii=False))
