import sys
import csv
from pathlib import Path
from datetime import datetime as dt

CODE_LIST = {'.cpp', '.hpp', '.c', '.h', '.py', '.pyw', '.cs', '.js', '.java'}
WHITE_LIST = CODE_LIST | {'.html', '.json', '.txt', '.ipynb'}

folders = [Path('/home/eduard/projects/exercism'), Path('/home/eduard/projects/lumind-copy'), Path('/home/eduard/projects/epam'),Path('/home/eduard/projects/devops')]

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
    csv_data = {}

    for folder in folders:
        if not folder.exists(): continue

        for el in folder.rglob('*'):
            if el.is_file() and el.suffix in WHITE_LIST:
                try:
                    y, m = created_at(el)
                    ext = el.suffix
                    key = (y, m, ext)

                    if key not in csv_data:
                        csv_data[key] = [0, 0, 0]

                    csv_data[key][0] += 1
                    csv_data[key][1] += el.stat().st_size

                    if ext in CODE_LIST:
                        csv_data[key][2] += lines_counter(el)
                except Exception:
                    continue

    filename = 'lab1_1.csv'
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['year', 'mon', 'ext', 'cnt', 'size', 'lines', 'avg_size', 'avg_line'])

            sorted_rows = sorted(csv_data.items())

            for (y, m, ext), (cnt, size, lines) in sorted_rows:
                avg_sz = size / cnt if cnt else 0

                if ext in CODE_LIST:
                    lines_str = str(lines)
                    avg_ln = lines / cnt if cnt else 0
                    avg_ln_str = f"{avg_ln:.1f}"
                else:
                    lines_str = ""
                    avg_ln_str = ""

                writer.writerow([y, m, ext, cnt, size, lines_str, f"{avg_sz:.1f}", avg_ln_str])

        print(f"Успішно! Файл '{filename}' створено.")
    except Exception as e:
        print(f"Помилка при записі CSV: {e}")


if __name__ == "__main__":
    main()