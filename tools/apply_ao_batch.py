import os
import re
import argparse
import subprocess
import numpy as np
from PIL import Image

VALID_EXT = (".png", ".jpg", ".jpeg", ".tga")


# ----------------------
# パス
# ----------------------
def get_root_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    root_dir = os.path.join(parent_dir, "texture")

    if not os.path.isdir(root_dir):
        raise RuntimeError("textureフォルダが見つかりません")

    return root_dir


def get_textool_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe = os.path.join(script_dir, "TexTool.exe")

    if not os.path.exists(exe):
        print(f"[WARN] TexTool.exe not found: {exe}")
        return None

    return exe


# ----------------------
# フォルダ検出
# ----------------------
def find_target_folders(root_dir):
    folders = []

    for name in os.listdir(root_dir):
        path = os.path.join(root_dir, name)

        if not os.path.isdir(path):
            continue

        if name == "AO":
            continue

        if os.path.isdir(os.path.join(path, "src")):
            folders.append(name)

    return sorted(folders)


# ----------------------
# 対話
# ----------------------
def select_target_folders(folders):
    print("処理対象フォルダを選択してください:")

    for i, f in enumerate(folders):
        print(f"{i}: {f}")

    val = input("番号（例: 0 または 0,1）: ").strip()
    if not val:
        return []

    indices = []
    for x in val.split(","):
        try:
            indices.append(int(x))
        except:
            pass

    return [folders[i] for i in indices if 0 <= i < len(folders)]


def ask_opacity(default=1.0):
    val = input(f"AOの強さ (0.0〜1.0, default={default}): ").strip()

    if val == "":
        return default

    try:
        v = float(val)
        if 0.0 <= v <= 1.0:
            return v
    except:
        pass

    print("不正な値。default使用")
    return default


# ----------------------
# キー抽出（重要修正）
# ----------------------
def extract_key(filename):
    numbers = re.findall(r"(\d+)", filename)
    if not numbers:
        return None
    return numbers[-1]  # 最後の数字を使う


# ----------------------
# AO適用（numpy）
# ----------------------
def apply_ao(base_path, ao_path, output_path, opacity):
    base = Image.open(base_path).convert("RGB")
    ao = Image.open(ao_path).convert("RGB")

    if base.size != ao.size:
        ao = ao.resize(base.size, Image.BICUBIC)

    base_np = np.asarray(base).astype(np.float32) / 255.0
    ao_np = np.asarray(ao).astype(np.float32) / 255.0

    factor = 1.0 - opacity + opacity * ao_np
    result = base_np * factor

    result = (result * 255.0).clip(0, 255).astype(np.uint8)
    Image.fromarray(result).save(output_path)


# ----------------------
# 名前生成
# ----------------------
def extract_base_prefix(filename):
    return filename.split("_")[0]


def extract_ao_suffix(filename):
    parts = filename.split("_")
    if len(parts) >= 2:
        return "_".join(parts[-2:])
    return filename


# ----------------------
# AOインデックス
# ----------------------
def build_ao_index(ao_dir):
    ao_map = {}

    for f in os.listdir(ao_dir):
        if not f.lower().endswith(VALID_EXT):
            continue

        key = extract_key(f)
        if key is None:
            continue

        ao_map[key] = f

    return ao_map


# ----------------------
# TexTool
# ----------------------
def run_textool(exe_path, image_path):
    if exe_path is None:
        return

    try:
        subprocess.run([exe_path, image_path], check=True)
        print("  -> Tex変換OK")
    except subprocess.CalledProcessError:
        print("  -> Tex変換失敗")


# ----------------------
# メイン処理
# ----------------------
def process(root, targets, opacity):
    ao_dir = os.path.join(root, "AO")
    ao_map = build_ao_index(ao_dir)
    exe_path = get_textool_path()

    for target in targets:
        print(f"\n=== Processing: {target} ===")

        src_dir = os.path.join(root, target, "src")
        out_dir = os.path.join(root, target)

        for f in os.listdir(src_dir):
            if not f.lower().endswith(VALID_EXT):
                continue

            key = extract_key(f)
            if key is None:
                continue

            if key not in ao_map:
                print(f"skip (AOなし): {f}")
                continue

            base_path = os.path.join(src_dir, f)
            ao_file = ao_map[key]
            ao_path = os.path.join(ao_dir, ao_file)

            base_prefix = extract_base_prefix(f)
            ao_suffix = extract_ao_suffix(ao_file)

            output_name = f"{base_prefix}_{ao_suffix}"
            output_path = os.path.join(out_dir, output_name)

            print(f"{f} + {ao_file} -> {output_name}")

            apply_ao(base_path, ao_path, output_path, opacity)
            run_textool(exe_path, output_path)


# ----------------------
# エントリ
# ----------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", nargs="+")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--opacity", type=float, default=1.0)

    args = parser.parse_args()

    root = get_root_dir()
    folders = find_target_folders(root)

    if args.all:
        targets = folders

    elif args.target:
        targets = args.target

    else:
        targets = select_target_folders(folders)
        if not targets:
            print("終了")
            return

        args.opacity = ask_opacity(args.opacity)

    process(root, targets, args.opacity)


if __name__ == "__main__":
    main()