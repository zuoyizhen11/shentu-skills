# -*- coding: utf-8 -*-
"""天正 DWG -> R2018 DXF（accoreconsole _.DXFOUT 包装）。

用法:
    python dxfout.py 输入.dwg [-o 输出.dxf] [--acad accoreconsole.exe完整路径] [--dry-run]

要点（实测）:
- ezdxf 不能读任何版本的 DWG 二进制，必须先转 DXF。
- SCR 必须 GBK + CRLF；参数序列 FILEDIA 0 / CMDDIA 0 / _.DXFOUT / 路径 / V / 2018 / 16 / _.QUIT / Y。
- 输出已存在时先删除，否则 DXFOUT 追加覆盖确认提示打乱序列。
- 禁用 -EXPORTTOAUTOCAD：10MB 级天正图 >5 分钟无产出。
"""
import argparse
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ACAD_CANDIDATES = [
    r"D:\Program Files\AutoCAD 2023\AutoCAD 2023\accoreconsole.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2024\AutoCAD 2024\accoreconsole.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2023\AutoCAD 2023\accoreconsole.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2022\accoreconsole.exe",
]


def find_acad(explicit=None):
    for p in ([explicit] if explicit else []) + ACAD_CANDIDATES:
        if p and os.path.isfile(p):
            return p
    raise SystemExit("找不到 accoreconsole.exe，请用 --acad 指定完整路径")


def make_scr(dxf_path):
    lines = ["FILEDIA", "0", "CMDDIA", "0", "_.DXFOUT", dxf_path,
             "V", "2018", "16", "_.QUIT", "Y"]
    return "\r\n".join(lines) + "\r\n"


def main():
    ap = argparse.ArgumentParser(description="天正 DWG 转 R2018 DXF")
    ap.add_argument("dwg")
    ap.add_argument("-o", "--out", help="输出 DXF 路径（默认同目录同名 .dxf）")
    ap.add_argument("--acad", help="accoreconsole.exe 完整路径")
    ap.add_argument("--dry-run", action="store_true", help="只生成并打印 SCR，不执行")
    a = ap.parse_args()

    dwg = os.path.abspath(a.dwg)
    if not os.path.isfile(dwg):
        raise SystemExit(f"输入不存在: {dwg}")
    out = os.path.abspath(a.out) if a.out else os.path.splitext(dwg)[0] + ".dxf"

    with open(dwg, "rb") as f:
        ver = f.read(6).decode("ascii", "replace")
    print(f"输入: {dwg}  大小 {os.path.getsize(dwg):,} B  DWG版本头: {ver}")

    scr_path = os.path.join(tempfile.gettempdir(), "tz_dxfout.scr")
    with open(scr_path, "w", encoding="gbk", newline="") as f:
        f.write(make_scr(out))
    print(f"SCR: {scr_path}  (GBK+CRLF)")
    print("SCR 内容: " + make_scr(out).replace("\r\n", " | ").strip())

    if a.dry_run:
        print("(dry-run，未执行)")
        return

    if os.path.isfile(out):
        os.remove(out)  # 避免覆盖确认提示打乱 SCR 序列

    exe = find_acad(a.acad)
    print(f"accoreconsole: {exe}  （100MB 级 DXF 约需 1~3 分钟）")
    log = out + ".dxfout.log"
    with open(log, "wb") as lf:
        rc = subprocess.call([exe, "/i", dwg, "/s", scr_path, "/l", "en-US"],
                             stdout=lf, stderr=lf)
    print(f"退出码 {rc}  日志(GBK): {log}")

    if os.path.isfile(out) and os.path.getsize(out) > 0:
        with open(out, "rb") as f:
            head = f.read(4096).decode("ascii", "replace")
        print(f"输出: {out}  {os.path.getsize(out):,} B  含AC1032(R2018)={'AC1032' in head}")
        if "AC1032" not in head:
            print("警告: 输出头不含 AC1032，请人工检查日志")
    else:
        print("失败: 未产出 DXF，请用 GBK 编码查看日志")


if __name__ == "__main__":
    main()
