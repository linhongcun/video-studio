#!/usr/bin/env python3
"""Run the unchanged player checks using CA-verified live canonical responses."""
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import BrowserType

OUT = Path(__file__).resolve().parent
D = OUT.parents[1]
helper = OUT / 'verified-transport.py'
spec = importlib.util.spec_from_file_location('verified_mq_transport', helper)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
transports = []
original_launch = BrowserType.launch

def launch_with_verified_transport(self, *args, **kwargs):
    browser = original_launch(self, *args, **kwargs)
    transports.append(module.install_browser_transport(browser))
    return browser

BrowserType.launch = launch_with_verified_transport
sys.argv = [str(D/'check-site.py'), '--base',
            'https://linhongcun.github.io/video-studio/', '--out', str(OUT)]
passed = False
try:
    runpy.run_path(str(D/'check-site.py'), run_name='__main__')
    passed = True
finally:
    BrowserType.launch = original_launch
    report = {
        'checkedAt': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'passed': passed,
        'directBrowserAttempt': {
            'passed': False,
            'reason': 'Chromium Page.goto failed with net::ERR_CERT_AUTHORITY_INVALID before page loading; its trust store lacks the managed proxy CA.'
        },
        'scope': 'Actual Chromium playback, interactions and native fullscreen with live canonical HTTPS bytes fetched through the configured CA-verified urllib transport. Browser-native TLS trust, physical mobile devices and full human listening were not tested as passing.',
        'helperSHA256': hashlib.sha256(helper.read_bytes()).hexdigest(),
        'unchangedCheckScriptSHA256': hashlib.sha256((D/'check-site.py').read_bytes()).hexdigest(),
        'transports': [transport.report() for transport in transports]
    }
    (OUT/'transport.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
