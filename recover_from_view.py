import json
import re

log_file = r'C:\Users\rekai\.gemini\antigravity\brain\0c1da971-06c5-46b5-87ed-1037d2d099f2\.system_generated\logs\transcript.jsonl'
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('type') == 'TOOL_RESPONSE':
                output = data.get('content', '')
                if 'File Path: `file:///G:/Code/SE%202/chatbot_engine.py`' in output and 'Total Lines: 174' in output:
                    # Parse the lines
                    lines = output.split('\n')
                    code_lines = []
                    for l in lines:
                        match = re.match(r'^\d+:\s(.*)', l)
                        if match:
                            code_lines.append(match.group(1))
                    
                    full_code = '\n'.join(code_lines)
                    with open(r'G:\Code\SE 2\SE-RAG\SE-with-chatbot\SE-main\chatbot_backend\chatbot_engine.py', 'w', encoding='utf-8') as out:
                        out.write(full_code)
                    print('Recovered from view_file step!')
        except Exception as e:
            pass
