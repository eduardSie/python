import sys
from pathlib import Path
from datetime import datetime as dt

CODE_LIST = {'.cpp', '.hpp', '.c', '.h', '.py', '.pyw', '.cs', '.js', '.java'}
WHITE_LIST = CODE_LIST | {'.html', '.json', '.txt', '.ipynb'}

folders = [Path('/home/eduard/projects/exercism'), Path('/home/eduard/projects/lumind-copy'), Path('/home/eduard/projects/epam'),Path('/home/eduard/projects/devops')]

START_YEAR = 2024
START_MONTH = 9

def created_at(path):
    if sys.platform.startswith('win'):
        timestamp = path.stat().st_birthtime
    else:
        timestamp = path.stat().st_ctime

    date = dt.fromtimestamp(timestamp)
    return date.year, date.month


def lines_counter(path):
    try:
        count = 0
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
    except:
        return 0


def main():
    d = {}

    for folder in folders:
        if not folder.exists(): continue

        for el in folder.rglob('*'):
            if el.is_file() and el.suffix in WHITE_LIST:
                try:
                    y, m = created_at(el)

                    if y < START_YEAR or (y == START_YEAR and m < START_MONTH):
                        continue

                    key = (y, m)
                    if key not in d:
                        d[key] = [0, 0, 0]

                    d[key][0] += 1
                    d[key][1] += el.stat().st_size

                    if el.suffix in CODE_LIST:
                        d[key][2] += lines_counter(el)
                except Exception as e:
                    continue

    sorted_d = sorted(d.items())

    print(
        f"\n{'Year':<6} {'Mon':<4} {'Count':<8} {'Total Size':<12} {'Total Lines':<12} {'Avg Size':<10} {'Avg Lines':<10}")
    print("-" * 75)

    for (year, month), (count, size, lines) in sorted_d:
        avg_size = size / count if count else 0
        avg_lines = lines / count if count else 0

        print(f"{year:<6} {month:<4} {count:<8} {size:<12} {lines:<12} {avg_size:<10.0f} {avg_lines:<10.1f}")


if __name__ == "__main__":
    main()