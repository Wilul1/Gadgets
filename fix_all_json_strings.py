import json
import os
backend_dir = r'G:\Code\SE 2\SE-RAG\SE-with-chatbot\SE-main\chatbot_backend'

for file in os.listdir(backend_dir):
    if file.endswith('.py') or file == '.env':
        path = os.path.join(backend_dir, file)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # If it looks like a JSON stringified python file
        if content.startswith('"'):
            try:
                parsed = json.loads(f'{{"content": {content}}}')['content']
                with open(path, 'w', encoding='utf-8') as out:
                    out.write(parsed)
                print(f'Successfully fixed {file}')
            except Exception as e:
                print(f'Failed to fix {file}: {e}')
