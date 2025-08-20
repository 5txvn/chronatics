import internetarchive
import json
import os
import glob
import re
from parse_file import parse_pdf

def fetch_articles(start_year, end_year, language, rows=10000, folder_name=None, ocr_only=False):
    if not folder_name:
        folder_name = f"{start_year}-{language}"
    
    metadata_dir = os.path.join('metadata', folder_name)
    content_dir = os.path.join('content', folder_name)
    os.makedirs(metadata_dir, exist_ok=True)
    os.makedirs(content_dir, exist_ok=True)
    
    existing_identifiers = []
    if os.path.exists(metadata_dir):
        existing_files = glob.glob(os.path.join(metadata_dir, 'article-*.json'))
        for file_path in existing_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                if 'identifier' in metadata:
                    existing_identifiers.append(metadata['identifier'])
    
    search_query = f"mediatype:texts language:{language} date:[{start_year}-01-01 TO {end_year}-12-31]"
    search = internetarchive.search_items(search_query, fields=['identifier'], rows=rows)
    
    existing_articles = glob.glob(os.path.join(metadata_dir, 'article-*.json'))
    next_number = max([int(os.path.basename(f).split('-')[1].split('.')[0]) for f in existing_articles] + [0]) + 1
    
    for item in search:
        identifier = item['identifier']
        
        if identifier in existing_identifiers:
            continue
            
        if ocr_only and not re.search(r'ocr-|-ocr', identifier.lower()):
            continue
        
        try:
            archive_item = internetarchive.get_item(identifier)
            metadata = archive_item.metadata
            metadata_file = os.path.join(metadata_dir, f'article-{next_number}.json')
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)
            
            pdf_files = [file for file in archive_item.files if file.endswith('.pdf')]
            if pdf_files:
                pdf_file_path = os.path.join(content_dir, f'article-{next_number}.pdf')
                archive_item.download(files=pdf_files[0], destdir=content_dir, filename=f'article-{next_number}.pdf')
                print(f"Downloaded: {identifier} -> article-{next_number}")
                
                parse_pdf(pdf_file_path)
                os.remove(pdf_file_path)
                print(f"PDF processed and deleted: {pdf_file_path}")
            
            next_number += 1
            existing_identifiers.append(identifier)
            
        except Exception as e:
            print(f"Error processing {identifier}: {e}")
            continue

fetch_articles(2000, 2010, 'eng', folder_name='2000-eng', ocr_only=False)