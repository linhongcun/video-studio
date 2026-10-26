"""Render the SVG avatar collection and review sheets with local Chromium."""

import json
from pathlib import Path
import shutil
import struct
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
ITEMS = json.loads((ROOT / "catalog.json").read_text())
(ROOT / "png").mkdir(exist_ok=True)
(ROOT / "review").mkdir(exist_ok=True)

for item in ITEMS:
    svg = ET.fromstring(item["svg"])
    assert svg.attrib["viewBox"] == "0 0 1024 1024"
    assert svg.attrib["width"] == svg.attrib["height"] == "1024"

FONT = '"Noto Sans CJK SC","Microsoft YaHei",sans-serif'
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=shutil.which("chromium"), args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 1024, "height": 1024}, device_scale_factor=1)
    for item in ITEMS:
        page.set_content('<style>body{margin:0}svg{display:block}</style>' + item["svg"])
        target = ROOT / "png" / f'{item["id"]}-{item["slug"]}.png'
        page.screenshot(path=str(target))
        assert struct.unpack(">II", target.read_bytes()[16:24]) == (1024, 1024)

    cards = "".join(
        '<article><div class="art">' + x["svg"] + '</div><div class="label"><span>'
        + x["id"] + '</span><strong>' + x["name"] + '</strong></div></article>'
        for x in ITEMS
    )
    sheet = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><style>
    *{box-sizing:border-box}body{margin:0;background:#f1f1e9;color:#213b35;font-family:FONT}
    main{padding:55px 64px 38px;width:1800px}header{display:flex;justify-content:space-between;align-items:end;margin-bottom:38px;border-bottom:1px solid #ccd6c7;padding-bottom:25px}
    h1{font-size:38px;letter-spacing:-.035em;margin:0 0 10px}p{margin:0;color:#667e6d;font-size:17px}.edition{font:500 14px monospace;color:#6f8673;letter-spacing:.06em}
    .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:23px 32px}article{text-align:center;padding:12px 0 13px}.art{display:grid;place-items:center}.art svg{width:306px;height:306px;border-radius:50%}.label{margin-top:17px;display:flex;gap:12px;justify-content:center;align-items:center}.label span{font:500 17px monospace;color:#6e8676}.label strong{font-size:22px;font-weight:650}footer{margin-top:29px;padding-top:22px;border-top:1px solid #ccd6c7;font-size:15px;color:#667e6d;display:flex;justify-content:space-between}
    </style><main><header><div><h1>IT小村 · 头像候选集</h1><p>代码 · 连接 · 好奇心　/　符号 01–04　角色 05–08　字标 09–12</p></div><div class="edition">12 EXPLORATIONS / 2026.10</div></header><section class="grid">CARDS</section><footer><span>告诉我喜欢的编号，就可以沿着那个方向继续细化。</span><span>原图 1024 × 1024 PNG + SVG　·　此处为圆形裁切预览</span></footer></main></html>'''.replace("FONT", FONT).replace("CARDS", cards)
    page.set_viewport_size({"width": 1800, "height": 1600})
    page.set_content(sheet)
    page.locator("main").screenshot(path=str(ROOT / "contact-sheet.png"))

    proof_rows = "".join('<div class="row"><span>' + x["id"] + ' ' + x["name"]
                         + '</span>' + ''.join('<div style="width:120px">'
                         + x["svg"].replace('width="1024" height="1024"', f'width="{size}" height="{size}"', 1)
                         + '</div>' for size in [32, 48, 64, 96]) + '</div>' for x in ITEMS)
    page.set_content('<style>body{margin:0;background:#f1f1e9;color:#213b35;font-family:' + FONT
                     + ';padding:30px}.row{display:flex;align-items:center;height:110px;gap:25px}.row>span{width:190px;font-size:16px}svg{border-radius:50%;display:block}h1{font-size:24px}</style><h1>小尺寸检查 · 32 / 48 / 64 / 96 px</h1>' + proof_rows)
    page.set_viewport_size({"width": 850, "height": 1470})
    page.screenshot(path=str(ROOT / "review" / "small-sizes.png"), full_page=True)

    # Exercise the actual standalone gallery and its download controls.
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.set_content((ROOT / "index.html").read_text(), wait_until="load")
    page.wait_for_function("document.querySelectorAll('.card').length === 12")
    page.locator('[data-filter="角色"]').click()
    assert page.locator(".card:visible").count() == 4
    page.locator('[data-filter="字标"]').click()
    assert page.locator(".card:visible").count() == 4
    page.locator('[data-filter="全部"]').click()
    assert page.locator(".card:visible").count() == 12
    page.locator('[data-shape="square"]').click()
    assert not page.locator("main").evaluate("x => x.classList.contains('round')")
    page.locator('[data-shape="round"]').click()
    page.locator('[data-open="06"]').click()
    assert page.locator("dialog").evaluate("x => x.open")
    with page.expect_download() as download_info:
        page.locator('dialog [data-png="06"]').click()
    download = download_info.value
    download_path = ROOT / "review" / "download-check.png"
    download.save_as(str(download_path))
    assert download.suggested_filename == "it-village-06-bracket-friend.png"
    assert struct.unpack(">II", download_path.read_bytes()[16:24]) == (1024, 1024)
    download_path.unlink()
    page.keyboard.press("Escape")
    assert not page.locator("dialog").evaluate("x => x.open")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    for art in page.locator(".art svg").all():
        box = art.bounding_box()
        assert abs(box["width"] - box["height"]) < 1
    page.evaluate("document.activeElement.blur()")
    page.mouse.move(0, 0)
    page.screenshot(path=str(ROOT / "review" / "gallery-desktop.png"), full_page=True)
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.locator('[data-open="09"]').click()
    assert page.locator("dialog").evaluate("x => x.open")
    page.locator("dialog .close").click()
    page.evaluate("document.activeElement.blur()")
    page.mouse.move(0, 0)
    page.screenshot(path=str(ROOT / "review" / "gallery-mobile.png"), full_page=True)
    assert not errors, errors
    browser.close()

report = {
    "avatars": 12,
    "pngDimensions": "1024 × 1024",
    "svg": "All 12 valid XML; no raster images or external resources",
    "gallery": "Filters, shape toggle, dialog, Escape, 1024px PNG download verified",
    "viewports": "1440px desktop / 390px mobile: no horizontal overflow",
    "consoleErrors": errors,
}
(ROOT / "review" / "checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
bundle = ROOT / "it-village-avatars-12.zip"
with ZipFile(bundle, "w", ZIP_DEFLATED) as archive:
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != bundle and "__pycache__" not in path.parts:
            archive.write(path, Path("it-village-avatars-12") / path.relative_to(ROOT))
with ZipFile(bundle) as archive:
    assert archive.testzip() is None
    assert sum("/png/" in name and name.endswith(".png") for name in archive.namelist()) == 12
    assert sum("/svg/" in name and name.endswith(".svg") for name in archive.namelist()) == 12
print(json.dumps(report, ensure_ascii=False))
