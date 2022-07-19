import os


def main():
    sources = '../Sources'
    files = os.listdir(sources)
    files = (file.split('/')[-1] for file in files)
    files = (file.split('.')[0] for file in files)
    isNamed = all(file.isnumeric() for file in files)
    print(f'Files are {"Already" if isNamed else " not" } Named.')
    if not isNamed:
        for i in range(len(files)):
            fullName = os.path.join(os.getcwd(), sources, files[i])
            os.rename(fullName, os.path.join(os.getcwd(), sources, f'{i}.db'))
