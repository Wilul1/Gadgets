import json

log_file = r'C:\Users\rekai\.gemini\antigravity\brain\0c1da971-06c5-46b5-87ed-1037d2d099f2\.system_generated\logs\transcript.jsonl'
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        if 'chatbot_engine.py' in line and 'write_to_file' in line:
            try:
                data = json.loads(line)
                if 'tool_calls' in data:
                    for tc in data['tool_calls']:
                        if tc['name'] == 'write_to_file':
                            args = tc['args']
                            if isinstance(args, str): args = json.loads(args)
                            if 'chatbot_engine.py' in args.get('TargetFile', ''):
                                content = args.get('CodeContent', '')
                                # This handles the extra quotes/escaping
                                content = json.loads(f'{{"content": {content}}}')['content']
                                with open(r'G:\Code\SE 2\SE-RAG\SE-with-chatbot\SE-main\chatbot_backend\chatbot_engine.py', 'w', encoding='utf-8') as out:
                                    out.write(content)
                                print('SUCCESSFULLY EXTRACTED chatbot_engine.py')
            except Exception as e:
                pass
