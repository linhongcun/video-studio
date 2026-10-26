#!/usr/bin/env python3
"""Canonical height-choice smoke; run only after explicit Pages success confirmation."""
from pathlib import Path
import importlib.util
p=Path(__file__).with_name('site-browser.py')
s=importlib.util.spec_from_file_location('height_choice_site_browser',p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
if __name__=='__main__':m.main(online=True)
