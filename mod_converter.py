import os
import sys
import shutil
import json
from datetime import datetime

VERSION = "1.0.0"

HEADER = """
=======================================================

  ██████ ██   ██ ██████      ███    ███  ██████  ██████
 ██      ██  ██      ██      ████  ████ ██    ██ ██   ██
 ██      █████    ███   ████ ██ ████ ██ ██    ██ ██   ██
 ██      ██  ██      ██      ██  ██  ██ ██    ██ ██   ██
  ██████ ██   ██ ██████      ██      ██  ██████  ██████

        CK3 Workshop Mod Converter  v""" + VERSION + """
        by 0V3RR  --  Free to use

=======================================================
"""

if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def verify_copy(src, dst):
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        dst_root = os.path.join(dst, rel)
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(dst_root, f)
            if not os.path.exists(dst_file):
                return False
            if os.path.getsize(src_file) != os.path.getsize(dst_file):
                return False
    return True

def main():
    print(HEADER)

    os.makedirs(LOG_DIR, exist_ok=True)

    user = os.environ.get("USERNAME") or os.environ.get("USER") or "User"
    default_workshop = os.path.join("C:\\", "Users", user, "Downloads", "STEAMCMD", "steamapps", "workshop", "content", "1158310")
    default_mod_dir = os.path.join("C:\\", "Users", user, "Documents", "Paradox Interactive", "Crusader Kings III", "mod")

    config = load_config()
    saved_workshop = config.get("workshop", "")
    saved_mod_dir = config.get("mod_dir", "")

    if saved_workshop and saved_mod_dir:
        print("Saved paths:")
        print("  Source      : " + saved_workshop)
        print("  Destination : " + saved_mod_dir)
        print("")
        print("Enter = use saved paths")
        print("'d'   = use default paths")
        print("'c'   = enter new custom paths")
    else:
        print("Default paths:")
        print("  Source      : " + default_workshop)
        print("  Destination : " + default_mod_dir)
        print("")
        print("Enter = use default paths")
        print("'c'   = enter custom paths")

    print("")
    choice = input("Your choice: ").strip().lower()

    if choice == "c":
        print("")
        print("SOURCE path (SteamCMD workshop folder):")
        print("Example: C:\\Users\\" + user + "\\Downloads\\STEAMCMD\\steamapps\\workshop\\content\\1158310")
        workshop = input("> ").strip().strip('"')

        print("")
        print("DESTINATION path (Paradox mod folder):")
        print("Example: C:\\Users\\" + user + "\\Documents\\Paradox Interactive\\Crusader Kings III\\mod")
        mod_dir = input("> ").strip().strip('"')

        if not workshop or not mod_dir:
            print("Empty path, cancelled.")
            input("Press Enter to close...")
            return

        config["workshop"] = workshop
        config["mod_dir"] = mod_dir
        config["version"] = VERSION
        save_config(config)
        print("Paths saved to config.json")

    elif choice == "d":
        workshop = default_workshop
        mod_dir = default_mod_dir
        config["workshop"] = workshop
        config["mod_dir"] = mod_dir
        config["version"] = VERSION
        save_config(config)

    else:
        if saved_workshop and saved_mod_dir:
            workshop = saved_workshop
            mod_dir = saved_mod_dir
        else:
            workshop = default_workshop
            mod_dir = default_mod_dir

    print("")
    print("Source      : " + workshop)
    print("Destination : " + mod_dir)
    print("")

    if not os.path.exists(workshop):
        print("ERROR: Source folder does not exist: " + workshop)
        input("Press Enter to close...")
        return

    print("Do you want to permanently delete the source files after copying?")
    print("  y = Yes (copy is verified before deleting)")
    print("  n = No, keep source intact")
    print("")
    delete_choice = input("Your choice: ").strip().lower()
    delete_source = delete_choice == "y"

    if delete_source:
        print("")
        print("WARNING: Source files will be PERMANENTLY deleted after copy.")
        print("Type 'CONFIRM' to proceed or anything else to cancel.")
        confirm = input("> ").strip()
        if confirm != "CONFIRM":
            print("Cancelled.")
            input("Press Enter to close...")
            return

    print("")
    os.makedirs(mod_dir, exist_ok=True)

    all_mods = [m for m in os.listdir(workshop) if os.path.isdir(os.path.join(workshop, m))]
    total = len(all_mods)

    success = 0
    skipped = 0
    failed = []

    log_lines = []
    log_lines.append("=== CK3 Mod Converter v" + VERSION + " - Log ===")
    log_lines.append("Date        : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log_lines.append("Source      : " + workshop)
    log_lines.append("Destination : " + mod_dir)
    log_lines.append("Delete src  : " + ("yes" if delete_source else "no"))
    log_lines.append("")

    for i, mod_id in enumerate(all_mods):
        src = os.path.join(workshop, mod_id)
        descriptor = os.path.join(src, "descriptor.mod")
        progress = "[" + str(i + 1) + "/" + str(total) + "]"

        if not os.path.exists(descriptor):
            print(progress + " SKIP (no descriptor.mod): " + mod_id)
            log_lines.append(progress + " SKIP: " + mod_id)
            skipped += 1
            continue

        print(progress + " Processing: " + mod_id)

        dst = os.path.join(mod_dir, mod_id)

        try:
            shutil.copytree(src, dst, dirs_exist_ok=True)

            if not verify_copy(src, dst):
                raise Exception("Copy verification failed")

            with open(descriptor, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if line.strip().startswith("remote_file_id"):
                    continue
                elif line.strip().startswith("path="):
                    new_lines.append("path=\"mod/" + mod_id + "\"\n")
                else:
                    new_lines.append(line)

            mod_file = os.path.join(mod_dir, mod_id + ".mod")
            with open(mod_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            if delete_source:
                shutil.rmtree(src)
                print(progress + " OK + source deleted: " + mod_id)
                log_lines.append(progress + " OK + deleted: " + mod_id)
            else:
                print(progress + " OK: " + mod_id)
                log_lines.append(progress + " OK: " + mod_id)

            success += 1

        except Exception as e:
            print(progress + " ERROR: " + mod_id + " -> " + str(e))
            log_lines.append(progress + " ERROR: " + mod_id + " -> " + str(e))
            failed.append(mod_id)

    print("")
    print("=======================================================")
    print("Done! " + str(success) + "/" + str(total) + " mods processed, " + str(skipped) + " skipped.")

    if failed:
        print("")
        print("FAILED MODS (" + str(len(failed)) + "):")
        for f in failed:
            print("  - " + f)

    log_lines.append("")
    log_lines.append("=======================================================")
    log_lines.append("Result: " + str(success) + "/" + str(total) + " OK, " + str(skipped) + " skipped, " + str(len(failed)) + " failed")
    if failed:
        log_lines.append("Failed:")
        for f in failed:
            log_lines.append("  - " + f)

    log_filename = "log_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
    log_path = os.path.join(LOG_DIR, log_filename)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print("")
    print("Log saved: logs\\" + log_filename)
    print("=======================================================")
    input("Press Enter to close...")

main()
