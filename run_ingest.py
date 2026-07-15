import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("CHROMA_PATH", os.path.join(os.path.dirname(__file__), ".chroma"))

from dotenv import load_dotenv
load_dotenv()

from src.tools.ingest import ingest_repo
import json, time

t0 = time.time()
result = ingest_repo(r"E:\PROJECTS\idurar-erp-crm", clear_existing=True)
print(json.dumps(result, indent=2))
print(f"Took {time.time()-t0:.1f}s")