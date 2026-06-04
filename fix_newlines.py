import os
import ast

backend_dir = r'G:\Code\SE 2\SE-RAG\SE-with-chatbot\SE-main\chatbot_backend'
for file in os.listdir(backend_dir):
    if file.endswith('.py') or file == '.env':
        path = os.path.join(backend_dir, file)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            if content.startswith('"') and content.endswith('"'):
                parsed_content = ast.literal_eval(content)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(parsed_content)
                print(f'Fixed {file}')
        except Exception as e:
            pass
