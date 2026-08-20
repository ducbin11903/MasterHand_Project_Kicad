#!/usr/bin/env python3
"""
add_bus_alias.py
================
Inserts bus alias definitions into KiCad schematic files.

Bus aliases live inside each .kicad_sch file, so a definition made on one sheet
is not visible on another. This script writes the same list into every sheet you
choose, in one pass.

Usage
-----
    python add_bus_alias.py board.kicad_sch                    preview
    python add_bus_alias.py board.kicad_sch --apply            write
    python add_bus_alias.py --all --apply                      every sheet in this folder
    python add_bus_alias.py sheet1.kicad_sch sheet2.kicad_sch --apply
    python add_bus_alias.py --all --apply --file my_alias.txt  use another list

The alias list is read from bus_alias_sexpr.txt next to this script unless
--file points somewhere else. Lines that are not bus_alias entries are ignored.

Close KiCad before running with --apply.
"""

import os, re, sys, shutil, argparse, glob
from datetime import datetime

DEFAULT_LIST = "bus_alias_sexpr.txt"

ALIAS_RE = re.compile(r'\(bus_alias\s+"([^"]+)"\s*\(members((?:\s+"[^"]*")*)\s*\)\s*\)')


def script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def read_alias_list(path):
    """Parse a text file into {name: full_sexpr_line}, keeping the original order."""
    if not os.path.isfile(path):
        return None
    text = open(path, encoding="utf-8").read()
    out = {}
    for m in ALIAS_RE.finditer(text):
        name = m.group(1)
        members = re.findall(r'"([^"]*)"', m.group(2))
        out[name] = (members, m.group(0).strip())
    return out


def existing_aliases(text):
    return {m.group(1): m.group(0) for m in ALIAS_RE.finditer(text)}


def insertion_point(text):
    """
    KiCad writes bus_alias entries after the title block and before lib_symbols.
    Return the character index where new entries should go.
    """
    m = re.search(r'\n\s*\(lib_symbols\b', text)
    if m:
        return m.start() + 1
    for pat in (r'\n\s*\(title_block\b', r'\n\s*\(paper\b', r'\n\s*\(uuid\b'):
        m = re.search(pat, text)
        if not m:
            continue
        # jump past that whole block
        i = text.index("(", m.start())
        depth = 0
        for j in range(i, len(text)):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    return j + 1
    # fall back: right after the opening (kicad_sch
    m = re.search(r'\(kicad_sch\b[^\n]*\n', text)
    return m.end() if m else 0


def process(path, aliases, apply_changes, replace):
    try:
        text = open(path, encoding="utf-8").read()
    except Exception as ex:
        return None, f"cannot read: {ex}"

    if "(kicad_sch" not in text:
        return None, "not a schematic file"

    present = existing_aliases(text)
    to_add, to_replace, unchanged = [], [], []

    for name, (members, line) in aliases.items():
        if name not in present:
            to_add.append(name)
        elif present[name].strip() == line.strip():
            unchanged.append(name)
        elif replace:
            to_replace.append(name)
        else:
            unchanged.append(name)

    if not to_add and not to_replace:
        return (0, 0, len(unchanged)), None

    new_text = text
    # replace the ones that differ
    for name in to_replace:
        new_text = new_text.replace(present[name], aliases[name][1], 1)

    # insert the missing ones
    if to_add:
        block = "".join("\t" + aliases[n][1] + "\n" for n in to_add)
        pos = insertion_point(new_text)
        new_text = new_text[:pos] + block + new_text[pos:]

    if apply_changes:
        open(path, "w", encoding="utf-8").write(new_text)

    return (len(to_add), len(to_replace), len(unchanged)), None


def main():
    ap = argparse.ArgumentParser(description="Add bus aliases to KiCad schematics")
    ap.add_argument("files", nargs="*", help="schematic files to edit")
    ap.add_argument("--all", action="store_true",
                    help="every .kicad_sch found from this folder downwards")
    ap.add_argument("--file", default=None, help="text file holding the alias list")
    ap.add_argument("--apply", action="store_true", help="write the changes")
    ap.add_argument("--replace", action="store_true",
                    help="overwrite aliases that already exist with a different member list")
    args = ap.parse_args()

    list_path = args.file or os.path.join(script_dir(), DEFAULT_LIST)
    aliases = read_alias_list(list_path)
    if aliases is None:
        print(f"Alias list not found: {list_path}")
        print("Save your bus_alias lines to that file, or pass --file <path>")
        sys.exit(1)
    if not aliases:
        print(f"No bus_alias entries found in {list_path}")
        sys.exit(1)

    if args.all:
        base = script_dir()
        targets = sorted(glob.glob(os.path.join(base, "**", "*.kicad_sch"), recursive=True))
    else:
        targets = [os.path.abspath(f) for f in args.files]

    if not targets:
        print("No schematic files given.")
        print("  python add_bus_alias.py board.kicad_sch --apply")
        print("  python add_bus_alias.py --all --apply")
        sys.exit(1)

    print(f"Alias list : {list_path}   ({len(aliases)} aliases)")
    print(f"Sheets     : {len(targets)}")
    print(f"Existing   : {'overwritten' if args.replace else 'left alone'}")
    print(f"Action     : {'WRITE' if args.apply else 'PREVIEW (nothing will change)'}")
    print("-" * 68)

    backup_dir = None
    if args.apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(script_dir(), f"sch_backup_{stamp}")
        os.makedirs(backup_dir, exist_ok=True)
        for t in targets:
            try:
                shutil.copy2(t, os.path.join(backup_dir, os.path.basename(t)))
            except Exception:
                pass
        print(f"Backup     : {backup_dir}")
        print("-" * 68)

    total_add = total_rep = 0
    for t in targets:
        name = os.path.basename(t)
        res, err = process(t, aliases, args.apply, args.replace)
        if err:
            print(f"  {name:<38} skipped   ({err})")
            continue
        add, rep, same = res
        total_add += add
        total_rep += rep
        bits = []
        if add:  bits.append(f"added {add}")
        if rep:  bits.append(f"replaced {rep}")
        if same: bits.append(f"already there {same}")
        print(f"  {name:<38} {', '.join(bits)}")

    print("-" * 68)
    if not total_add and not total_rep:
        print("Nothing to change.")
        if not args.replace:
            print("Use --replace if you want existing aliases overwritten.")
        return

    print(f"{total_add} aliases added, {total_rep} replaced.")
    if args.apply:
        print()
        print("Open the schematic in KiCad and check")
        print("File > Schematic Setup > Bus Alias Definitions.")
        print(f"Backup kept at: {backup_dir}")
    else:
        print()
        print("This was a preview. Re-run with --apply to write the changes.")


if __name__ == "__main__":
    main()
