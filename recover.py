import json
import os

log_file = r"C:\Users\rekai\.gemini\antigravity\brain\0c1da971-06c5-46b5-87ed-1037d2d099f2\.system_generated\logs\transcript.jsonl"
target_files = ["chatbot_engine.py", "firebase_connector.py", "intent_router.py", "ingest_faqs.py", ".env"]

file_contents = {f: "" for f in target_files}

with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if "tool_calls" in data:
                for tc in data["tool_calls"]:
                    if tc["name"] == "write_to_file":
                        args = tc["args"]
                        if isinstance(args, str):
                            args = json.loads(args)
                        target = args.get("TargetFile", "")
                        content = args.get("CodeContent", "")
                        for tf in target_files:
                            if tf in target:
                                file_contents[tf] = content
        except Exception as e:
            pass

for tf, content in file_contents.items():
    if content:
        out_path = os.path.join(r"G:\Code\SE 2\SE-RAG\SE-with-chatbot\SE-main\chatbot_backend", tf)
        with open(out_path, 'w', encoding='utf-8') as out:
            out.write(content)
        print(f"Recovered {tf} to chatbot_backend")
