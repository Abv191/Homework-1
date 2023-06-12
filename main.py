import os
import shutil
import patoolib
from transliterate import translit

EXTENSIONS = {
    "images": ["JPEG", "PNG", "JPG", "SVG"],
    "videos": ["AVI", "MP4", "MOV", "MKV"],
    "documents": ["DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX", "xlsx"],
    "music": ["MP3", "OGG", "WAV", "AMR"],
    "archives": ["ZIP", "GZ", "TAR", "RAR"]
}


def extract_files(archive_path, destination_folder):
    patoolib.extract_archive(archive_path, outdir=destination_folder, verbosity=-1)


def transliterate_text(text):
    return translit(text, 'ru', reversed=True)


def remove_empty_folders(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            if not os.listdir(dir_path):  # Проверяем, пустая ли папка
                os.rmdir(dir_path)


def sort_files(folder_path):
    remove_empty_folders(folder_path)  # Удаление пустых папок

    categories = {key: [] for key in EXTENSIONS.keys()}
    all_extensions = []

    folder_name = os.path.basename(folder_path)
    transliterated_folder_name = transliterate_text(folder_name)
    new_folder_path = os.path.join(os.path.dirname(folder_path), transliterated_folder_name)

    if folder_path != new_folder_path:
        os.rename(folder_path, new_folder_path)
        folder_path = new_folder_path

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        if os.path.isdir(item_path):
            # Исключаем сортировку данных в подпапках с названиями "images", "videos", "documents", "music" и "archives"
            if item in EXTENSIONS.keys():
                continue

            sort_files(item_path)
        elif os.path.isfile(item_path):
            extension = item.split(".")[-1].upper()
            all_extensions.append(extension)

            for category, extensions in EXTENSIONS.items():
                if extension in extensions:
                    new_name = transliterate_text(item.split(".")[0])
                    new_name = new_name.replace(" ", "_")
                    new_name = f"{new_name}.{extension}"
                    new_item_path = os.path.join(folder_path, new_name)

                    os.rename(item_path, new_item_path)
                    categories[category].append(new_name)

                    # Создание папок и перемещение файлов
                    new_folder = os.path.join(folder_path, category)
                    os.makedirs(new_folder, exist_ok=True)
                    shutil.move(new_item_path, os.path.join(new_folder, new_name))

                    # Распаковка архива в отдельную папку
                    if category == "archives":
                        archive_name = os.path.splitext(new_name)[0]
                        archive_folder = os.path.join(new_folder, archive_name)
                        os.makedirs(archive_folder, exist_ok=True)

                        extract_files(os.path.join(new_folder, new_name), archive_folder)

                        os.remove(os.path.join(new_folder, new_name))

                    break

    print(f"Folder: {folder_path}")
    for category, files in categories.items():
        print(f"{category.capitalize()}: {', '.join(files)}")

    return categories, all_extensions


if __name__ == "__main__":
    folder_path = input("Введите путь к папке: ")
    sorted_categories, all_extensions = sort_files(folder_path)

    known_extensions = set(all_extensions).intersection(set(sum(EXTENSIONS.values(), [])))
    print(f"\nИзвестные расширения: {', '.join(known_extensions)}")

    unknown_extensions = [ext for ext in all_extensions if ext not in known_extensions]
    print(f"Неизвестные расширения: {', '.join(unknown_extensions)}")
