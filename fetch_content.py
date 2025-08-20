import internetarchive
import os
import json
import glob
from parse_file import parse_pdf

def fetch_content(identifier, folder_name, save_dir='.'):
    metadata_dir = os.path.join(save_dir, 'metadata', folder_name)
    content_dir = os.path.join(save_dir, 'content', folder_name)
    os.makedirs(metadata_dir, exist_ok=True)
    os.makedirs(content_dir, exist_ok=True)

    existing_articles = glob.glob(os.path.join(metadata_dir, 'article-*.json'))
    next_number = max([int(os.path.basename(f).split('-')[1].split('.')[0]) for f in existing_articles] + [0]) + 1

    try:
        item = internetarchive.get_item(identifier)
        metadata = item.metadata
        print("Metadata fetched successfully!")

        metadata_file = os.path.join(metadata_dir, f'article-{next_number}.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
        print(f"Metadata saved to {metadata_file}")

        pdf_files = [file for file in item.files if file.endswith('.pdf')]
        if not pdf_files:
            print("No PDF file found for this item.")
            return

        pdf_file_path = os.path.join(content_dir, f'article-{next_number}.pdf')
        item.download(files=pdf_files[0], destdir=content_dir, filename=f'article-{next_number}.pdf')
        print(f"PDF downloaded successfully: {pdf_file_path}")

        parse_pdf(pdf_file_path)
        os.remove(pdf_file_path)
        print(f"PDF processed and deleted: {pdf_file_path}")

    except Exception as e:
        print(f"Error fetching content: {e}")
