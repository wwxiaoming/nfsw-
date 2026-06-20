#!/usr/bin/env python3
"""从 RAR 重新解压 0 字节的空文件，恢复内容。"""
import rarfile
from pathlib import Path

RAR = "/workspace/帝王战队621 1：00.rar"
WS = Path("/workspace/帝王战队621 1：00")
PIXIV = WS / "pixiv小说"

rf = rarfile.RarFile(RAR)
# 先找出所有磁盘上的空 txt 文件
zeros = []
for p in PIXIV.rglob("*.txt"):
    if p.stat().st_size == 0:
        rel = p.relative_to(WS).as_posix()  # 形如 帝王战队621 1：00/pixiv小说/...
        zeros.append((p, rel))

print(f"磁盘上空文件: {len(zeros)}")

# 逐个从 RAR 重新解压
restored = 0
failed = 0
for p, rel in zeros:
    found = False
    for f in rf.infolist():
        if f.filename == rel:
            found = True
            try:
                data = rf.read(f.filename)
                p.write_bytes(data)
                size = len(data)
                print(f"✓ {p.relative_to(PIXIV)}  恢复 {size}B")
                restored += 1
            except Exception as e:
                print(f"✗ {p.relative_to(PIXIV)}  失败: {e}")
                failed += 1
            break
    if not found:
        print(f"? RAR 中未找到: {rel}")
        failed += 1

print(f"\n恢复成功: {restored} / 失败: {failed}")
# 验证
remaining = [p for p in PIXIV.rglob("*.txt") if p.stat().st_size == 0]
print(f"剩余空文件: {len(remaining)}")
