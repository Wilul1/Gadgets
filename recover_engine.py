import json
import ast
import os
log_file = r'C:\Users\rekai\.gemini\antigravity\brain\0c1da971-06c5-46b5-87ed-1037d2d099f2\.system_generated\logs\transcript.jsonl'
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('step_index') == 414 and 'tool_calls' in data:
                for tc in data['tool_calls']:
                    if tc['name'] == 'write_to_file':
                        args = tc['args']
                        if isinstance(args, str):
                            args = json.loads(args)
                        if 'chatbot_engine.py' in args.get('TargetFile', ''):
                            content = args.get('CodeContent', '')
                            # Parse it properly if it's JSON stringified
                            if content.startswith('"'):
                                content = ast.literal_eval(content)
                            with open(r'G:\Code\SE 2\SE-RAG\SE-with-chatbot\SE-main\chatbot_backend\chatbot_engine.py', 'w', encoding='utf-8') as out:
                                out.write(content)
                            print('Recovered clean chatbot_engine.py')
        except Exception:
            pass
