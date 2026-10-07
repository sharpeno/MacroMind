import json
from pathlib import Path
from macromind.methods.timeline import render_timeline
r=Path.cwd();o=r/'phase1/method_timeline/run_001';(o/'TRACE.html').write_text(render_timeline(json.loads((o/'timeline.json').read_text(encoding='utf-8'))),encoding='utf-8')
