import os
import sys
import shutil
import patoolib
from transliterate import translit
import re

EXTENSIONS = {
    "images": ["JPEG", "PNG", "JPG", "SVG"],
    "videos": ["AVI", "MP4", "MOV", "MKV"],
    "documents": ["DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX", "xlsx"],
    "music": ["MP3", "OGG", "WAV", "AMR"],
    "archives": ["ZIP", "GZ", "TAR", "RAR"]
}

def extract_files(archive_path, destination_folder):
    try:
        patoolib.extract_archive(archive_path, outdir=destination_folder, verbosity=-1)
    except Exception as e:
        print(f"Error extracting archive '{archive_path}': {e}")

def normalize(text):
    transliterated_text = translit(text, 'ru', reversed=True)
    normalized_text = re.sub(r'[^a-zA-Z0-9]', '_', transliterated_text)
    return normalized_text

def remove_empty_folders(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            if not os.listdir(dir_path):  # Check if folder is empty
                os.rmdir(dir_path)


def sort(folder_path):
    def sort_files(folder_path):
        global extension
        sorted_categories = {category: [] for category in EXTENSIONS.keys()}
        all_extensions = set()

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                original_extension = file.split('.')[-1]
                upper_extension = original_extension.upper()

                for category, extensions_list in EXTENSIONS.items():
                    if upper_extension in extensions_list:
                        sorted_categories[category].append(file)

                        new_name = normalize(file.split(".")[0])
                        new_name = new_name.replace(" ", "_")
                        new_name = f"{new_name}.{original_extension}"
                        new_item_path = os.path.join(folder_path, new_name)

                        os.rename(file_path, new_item_path)

                        extension = original_extension

                        all_extensions.add(extension)

                        new_folder = os.path.join(folder_path, category)
                        os.makedirs(new_folder, exist_ok=True)

                        # Здесь заменяем shutil.copy на shutil.move
                        shutil.move(new_item_path, os.path.join(new_folder, new_name))

                        if category == "archives":
                            archive_name = os.path.splitext(new_name)[0]
                            archive_folder = os.path.join(new_folder, archive_name)
                            os.makedirs(archive_folder, exist_ok=True)

                            extract_files(os.path.join(new_folder, new_name), archive_folder)

                            os.remove(os.path.join(new_folder, new_name))

                        break

                all_extensions.add(extension)

        return sorted_categories, sorted(all_extensions)

    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return {}, []

    return sort_files(folder_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]

    sorted_categories, all_extensions = sort(folder_path)

    print(f"Folder: {folder_path}")
    for category, files in sorted_categories.items():
        print(f"{category.capitalize()}: {', '.join(files)}")
