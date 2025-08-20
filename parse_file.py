import PyPDF2
import re
import os

def parse_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    
    lines = text.split('\n')
    filtered_lines = [line.strip() for line in lines if len(line.strip()) >= 50]
    
    processed_text = ' '.join(filtered_lines)
    sentences = re.split(r'(?<=[.!?])\s+', processed_text)
    
    sentence_filters = [
        lambda s: len(s.strip()) >= 50,
        lambda s: not re.match(r'^[^a-zA-Z]', re.sub(r'[^\w\s]', '', s.strip()))
    ]
    
    content_filters = [
        (r'["""'']', ''),
        (r'\([^)]*\)', ''),
        (r'[^\w\s]', ''),
        (r'\s+', ' ')
    ]
    
    final_sentences = []
    for sentence in sentences:
        if sentence.strip():
            filtered_sentence = sentence.strip()
            for pattern, replacement in content_filters:
                filtered_sentence = re.sub(pattern, replacement, filtered_sentence)
            
            if all(f(filtered_sentence) for f in sentence_filters):
                final_sentences.append(filtered_sentence)
    
    final_text = '\n'.join(final_sentences)
    
    txt_path = pdf_path.rsplit('.', 1)[0] + '.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"Text extracted and saved to {txt_path}")
