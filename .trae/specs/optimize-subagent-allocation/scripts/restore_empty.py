#!/usr/bin/env python3
"""从 RAR 重新解压 0 字节的空文件，恢复内容。"""
import subprocess
from pathlib import Path

RAR = "/workspace/帝王战队621 1：00.rar"
WS = Path("/workspace/帝王战队621 1：00")
PIXIV = WS / "pixiv小说"

# 找出所有磁盘上的空 txt 文件
zeros = [p for p in PIXIV.rglob("*.txt") if p.stat().st_size == 0]
print(f"磁盘上空文件: {len(zeros)}")

restored = 0
failed = []
for p in zeros:
    rel = "帝王战队621 1：00/" + p.relative_to(WS).as_posix()
    # 用 unar -f 强制覆盖单个文件
    # unar 没法单文件解压 → 用临时目录 + 复制
    import tempfile, shutil
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # 在临时目录解压全部
        result = subprocess.run(
            ["unar", "-f", "-o", str(td), RAR],
            capture_output=True, text=True, timeout=600,
        )
        src = td / rel
        if src.exists() and src.stat().st_size > 0:
            shutil.copy2(src, p)
            restored += 1
            print(f"✓ {p.relative_to(PIXIV)}  恢复 {src.stat().st_size}B")
        else:
            failed.append(rel)
            print(f"✗ {p.relative_to(PIXIV)}  找不到/空")

print(f"\n恢复成功: {restored} / 失败: {len(failed)}")
remaining = [p for p in PIXIV.rglob("*.txt") if p.stat().st_size == 0]
print(f"剩余空文件: {len(remaining)}")
