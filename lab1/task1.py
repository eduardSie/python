from pathlib import Path

CODE_LIST = {'.cpp', '.hpp', '.c', '.h', '.py', '.pyw', '.cs', '.js', '.java'}
WHITE_LIST = CODE_LIST | {'.html', '.json', '.txt', '.ipynb'}

folders = [Path('/home/eduard/projects/exercism'), Path('/home/eduard/projects/lumind-copy'), Path('/home/eduard/projects/epam'),Path('/home/eduard/projects/devops')]

def kind(extension):
    if extension in CODE_LIST:
        return 'C'
    elif extension in WHITE_LIST:
        return 'W'
    else:
        return 'O'

def main():
    d = {}

    for folder in folders:
        if not folder.exists():
            continue

        for el in folder.glob('**/*'):
            if el.is_file():
                ext = el.suffix
                d[ext] = d.get(ext, 0) + 1

    result = sorted(d.items(), key=lambda x: x[1], reverse=True)

    print(f"\n{'Ext':<20} {'Count':<10} {'Type':<5}")
    print("-" * 35)

    for ext, count in result:
        k = kind(ext)
        print(f"{ext:<20} {count:<10} {k:<5}")


if __name__ == "__main__":
    main()