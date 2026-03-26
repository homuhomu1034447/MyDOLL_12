import os
import re
import subprocess

# ======================
# 設定
# ======================
MENU_DIR = "../menu"
CONVERTER = "[CM3D2]menu←→txt変換.exe"

# 除外パターン（_z01 など）
EXCLUDE_PATTERN = re.compile(r"_z\d+$")


def is_target_file(filename):
    name, ext = os.path.splitext(filename)

    if ext.lower() != ".menu":
        return False

    if EXCLUDE_PATTERN.search(name):
        return False

    return True


def convert_menu(file_path):
    try:
        subprocess.run([CONVERTER, file_path], check=True)
        print(f"✔ Converted: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"✖ Failed: {file_path}")
        print(e)


def rename_txt_files(suffix):
    """
    .menu.txt の形式に対して
    myfile.menu.txt → myfile_z04.menu.txt
    のようにリネームする
    """
    for filename in os.listdir(MENU_DIR):
        if not filename.lower().endswith(".menu.txt"):
            continue

        # すでに suffix が付いている場合はスキップ
        if f"_{suffix}.menu.txt" in filename:
            print(f"Skip (already renamed): {filename}")
            continue

        # ".menu.txt" を分離
        base = filename[:-len(".menu.txt")]  # ← myfile の部分

        new_name = f"{base}_{suffix}.menu.txt"

        old_path = os.path.join(MENU_DIR, filename)
        new_path = os.path.join(MENU_DIR, new_name)

        os.rename(old_path, new_path)
        print(f"Rename: {filename} -> {new_name}")


def edit_txt_contents():
    """
    .menu.txt の中身を編集する
    """
    for filename in os.listdir(MENU_DIR):
        if not filename.endswith(".menu.txt"):
            continue

        # suffix 抽出（_z08 など）
        m = re.search(r"_(z\d+)\.menu\.txt$", filename)
        if not m:
            print(f"Skip (no suffix): {filename}")
            continue

        suffix = m.group(1)  # z08

        file_path = os.path.join(MENU_DIR, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []

        for line in lines:
            if line.startswith("マテリアル変更"):
                parts = line.rstrip("\n").split("\t")

                if len(parts) >= 4:
                    mate_name = parts[-1]

                    # すでに suffix が付いているならスキップ
                    if f"_{suffix}." in mate_name:
                        new_lines.append(line)
                        continue

                    # 拡張子分離
                    base, ext = os.path.splitext(mate_name)

                    new_mate = f"{base}_{suffix}{ext}"
                    parts[-1] = new_mate

                    new_line = "\t".join(parts) + "\n"
                    new_lines.append(new_line)

                    print(f"Edit: {mate_name} -> {new_mate}")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # 上書き保存
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"✔ Edited: {filename}")

def cleanup_txt_files():
    """
    menuフォルダ内の .txt ファイルをすべて削除
    """
    for filename in os.listdir(MENU_DIR):
        if filename.lower().endswith(".txt"):
            file_path = os.path.join(MENU_DIR, filename)

            try:
                os.remove(file_path)
                print(f"Delete: {filename}")
            except Exception as e:
                print(f"Failed to delete: {filename}")
                print(e)

def convert_txt_to_menu():
    """
    .txt を変換ツールに渡して .menu に戻す
    """
    for filename in os.listdir(MENU_DIR):
        if not filename.endswith(".menu.txt"):
            continue

        file_path = os.path.join(MENU_DIR, filename)

        try:
            subprocess.run([CONVERTER, file_path], check=True)
            print(f"✔ Re-converted: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"✖ Failed: {filename}")
            print(e)

def main():
    # ======================
    # 対話入力
    # ======================
    suffix = input("付与する文字列を入力してください（例: z09）: ").strip()

    if not suffix:
        print("文字列が空です。終了します。")
        return

    print(f"入力文字列: {suffix}")

    # ======================
    # ① 既存txt削除
    # ======================
    print("---- txt削除 ----")
    cleanup_txt_files()

    # ======================
    # ② 変換処理
    # ======================
    print("---- 変換開始 ----")
    for filename in os.listdir(MENU_DIR):
        if not is_target_file(filename):
            print(f"Skip: {filename}")
            continue

        full_path = os.path.join(MENU_DIR, filename)
        convert_menu(full_path)

    # ======================
    # ③ リネーム
    # ======================
    print("---- リネーム開始 ----")
    rename_txt_files(suffix)

    # ======================
    # ④ 中身編集
    # ======================
    print("---- テキスト編集開始 ----")
    edit_txt_contents()

    print("---- txt → menu 再変換 ----")
    convert_txt_to_menu()

    print("完了！")


if __name__ == "__main__":
    main()