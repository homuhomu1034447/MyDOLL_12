import os
import re
import subprocess

# ======================
# 設定
# ======================
MATE_DIR = "../mate"
CONVERTER = "[CM3D2]mate←→txt変換.exe"

# _z01 などを除外
EXCLUDE_PATTERN = re.compile(r"_z\d+$")

def convert_txt_to_mate():
    """
    .mate.txt を変換ツールに渡して .mate に戻す
    """
    for filename in os.listdir(MATE_DIR):
        if not filename.endswith(".mate.txt"):
            continue

        file_path = os.path.join(MATE_DIR, filename)

        try:
            subprocess.run([CONVERTER, file_path], check=True)
            print(f"✔ Re-converted: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"✖ Failed: {filename}")
            print(e)

# ======================
# txt削除
# ======================
def cleanup_txt_files():
    for filename in os.listdir(MATE_DIR):
        if filename.lower().endswith(".txt"):
            path = os.path.join(MATE_DIR, filename)
            try:
                os.remove(path)
                print(f"Delete: {filename}")
            except Exception as e:
                print(f"Failed to delete: {filename}")
                print(e)


# ======================
# 対象判定
# ======================
def is_target_file(filename):
    name, ext = os.path.splitext(filename)

    if ext.lower() != ".mate":
        return False

    if EXCLUDE_PATTERN.search(name):
        return False

    return True


# ======================
# 変換処理
# ======================
def convert_mate(file_path):
    try:
        subprocess.run([CONVERTER, file_path], check=True)
        print(f"✔ Converted: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"✖ Failed: {file_path}")
        print(e)


# ======================
# リネーム処理（重要）
# ======================
def rename_txt_files(suffix):
    """
    myfile.mate.txt → myfile_z08.mate.txt
    """
    for filename in os.listdir(MATE_DIR):
        if not filename.lower().endswith(".mate.txt"):
            continue

        # 既に付いている場合はスキップ
        if f"_{suffix}.mate.txt" in filename:
            print(f"Skip (already renamed): {filename}")
            continue

        base = filename[:-len(".mate.txt")]  # myfile

        new_name = f"{base}_{suffix}.mate.txt"

        old_path = os.path.join(MATE_DIR, filename)
        new_path = os.path.join(MATE_DIR, new_name)

        os.rename(old_path, new_path)
        print(f"Rename: {filename} -> {new_name}")

def edit_mate_txt_contents(replace_char):
    """
    mate.txt の tex セクションを書き換える
    A → replace_char に変更
    """
    for filename in os.listdir(MATE_DIR):
        if not filename.endswith(".mate.txt"):
            continue

        file_path = os.path.join(MATE_DIR, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # texセクション検出
            if line.strip() == "tex":
                new_lines.append(line)
                i += 1

                # texセクションの5行をそのまま取得
                block = lines[i:i+5]

                if len(block) >= 5:
                    # 3行目（index 2）
                    name_line = block[2].rstrip("\n")
                    # 4行目（index 3）
                    path_line = block[3].rstrip("\n")

                    # A → 指定文字に置換
                    new_name = name_line.replace("A", replace_char)
                    new_path = path_line.replace("A", replace_char)

                    block[2] = new_name + "\n"
                    block[3] = new_path + "\n"

                    print(f"Edit name: {name_line} -> {new_name}")
                    print(f"Edit path: {path_line} -> {new_path}")

                # 追加
                new_lines.extend(block)
                i += 5
                continue

            # 通常行
            new_lines.append(line)
            i += 1

        # 上書き保存
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"✔ Edited: {filename}")

# ======================
# メイン
# ======================
def main():
    if not os.path.exists(MATE_DIR):
        print(f"フォルダが存在しません: {MATE_DIR}")
        return

    # 対話入力
    suffix = input("付与する文字列を入力してください（例: z08）: ").strip()

    if not suffix:
        print("文字列が空です。終了します。")
        return

    print(f"入力文字列: {suffix}")

    replace_char = input("Aを何に置き換えますか？（例: B）: ").strip()

    if not replace_char:
        print("置換文字が空です。終了します。")
        return

    # ① クリーンアップ
    print("---- txt削除 ----")
    cleanup_txt_files()

    # ② mate → txt
    print("---- 変換開始 ----")
    for filename in os.listdir(MATE_DIR):
        if not is_target_file(filename):
            print(f"Skip: {filename}")
            continue

        full_path = os.path.join(MATE_DIR, filename)
        convert_mate(full_path)

    # ③ suffix付与
    print("---- リネーム開始 ----")
    rename_txt_files(suffix)

    print("---- mateテキスト編集開始 ----")
    edit_mate_txt_contents(replace_char)

    print("---- txt → mate 再変換 ----")
    convert_txt_to_mate()

    print("完了！")


if __name__ == "__main__":
    main()