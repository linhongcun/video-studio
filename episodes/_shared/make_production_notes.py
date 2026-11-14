"""制作说明的中性 CLI 入口，复用现有生成实现。

默认输出仍为 knoll-props.md，兼容已有装配器、冻结器和批量检查器；
该文件名不表示制作职责或指定代理。可用 --out 指定其他输出路径。
历史 --spec 按原实现生成，不改写既有制作说明及其字节身份。
"""
from make_knoll_props import main


if __name__ == '__main__':
    raise SystemExit(main())
