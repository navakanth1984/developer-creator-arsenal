"""
Hypit SVML Compiler - Compiles word-anchored Structured Video Markup Language into deterministic timeline events.
"""

import xml.etree.ElementTree as ET
import json
import os
import sys

def compile_svml(file_path: str) -> dict:
    tree = ET.parse(file_path)
    root = tree.getroot()

    fps = int(root.attrib.get("fps", 30))
    width = int(root.attrib.get("width", 1080))
    height = int(root.attrib.get("height", 1920))

    # Step 1: Map words to timestamp ranges
    word_map = {}
    words_list = []
    audio_track = root.find("audio_track")
    if audio_track is not None:
        for w in audio_track.findall("word"):
            w_id = w.attrib["id"]
            start_ms = int(w.attrib["start"])
            end_ms = int(w.attrib["end"])
            text = w.text or ""
            word_obj = {
                "id": w_id,
                "text": text,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "start_frame": int((start_ms / 1000.0) * fps),
                "end_frame": int((end_ms / 1000.0) * fps)
            }
            word_map[w_id] = word_obj
            words_list.append(word_obj)

    # Step 2: Resolve scenes and elements by anchoring to words
    scenes = []
    for sc in root.findall("scene"):
        sc_id = sc.attrib["id"]
        start_anchor = sc.attrib["anchor_start"]
        end_anchor = sc.attrib["anchor_end"]
        transition = sc.attrib.get("transition", "cut")

        start_word = word_map[start_anchor]
        end_word = word_map[end_anchor]

        elements = []
        for el in sc.findall("element"):
            el_type = el.attrib["type"]
            el_anchor = el.attrib.get("anchor", start_anchor)
            el_end_anchor = el.attrib.get("anchor_end", el_anchor)
            
            elements.append({
                "type": el_type,
                "text": el.attrib.get("text", ""),
                "start_frame": word_map[el_anchor]["start_frame"],
                "end_frame": word_map[el_end_anchor]["end_frame"],
                "style": el.attrib.get("style", ""),
                "highlight_color": el.attrib.get("highlight_color", "#FFFFFF")
            })

        scenes.append({
            "id": sc_id,
            "start_ms": start_word["start_ms"],
            "end_ms": end_word["end_ms"],
            "start_frame": start_word["start_frame"],
            "end_frame": end_word["end_frame"],
            "transition": transition,
            "elements": elements
        })

    compiled_timeline = {
        "metadata": {
            "fps": fps,
            "dimensions": {"width": width, "height": height},
            "total_words": len(words_list),
            "total_duration_ms": words_list[-1]["end_ms"] if words_list else 0
        },
        "words": words_list,
        "scenes": scenes
    }
    return compiled_timeline

def generate_html_preview(timeline: dict, out_html_path: str):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Hypit SVML Video Preview</title>
  <style>
    body {{ background: #000; color: #fff; font-family: system-ui, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
    #viewport {{ width: 360px; height: 640px; background: #0d1117; border: 2px solid #30363d; border-radius: 18px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; padding: 24px; box-sizing: border-box; }}
    .badge {{ align-self: flex-start; padding: 6px 14px; border-radius: 9999px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; }}
    .kinetic-text {{ font-size: 32px; font-weight: 800; line-height: 1.2; text-align: center; margin: auto 0; }}
    .word {{ display: inline-block; margin-right: 6px; transition: color 0.15s, transform 0.15s; }}
    .active-word {{ color: #00f2fe; transform: scale(1.15); }}
    #scrubber {{ width: 360px; margin-top: 16px; }}
    .timeline-info {{ font-size: 13px; color: #8b949e; margin-top: 8px; }}
  </style>
</head>
<body>
  <h2>Hypit SVML Word-Anchored Video Player</h2>
  <div id="viewport">
    <div id="badge" class="badge" style="background:#EF4444;">🚨 RADICAL SHIFT</div>
    <div id="caption" class="kinetic-text">
      {" ".join([f'<span id="span_{w["id"]}" class="word">{w["text"]}</span>' for w in timeline["words"]])}
    </div>
    <div style="font-size: 11px; color:#58a6ff; text-align:center;">Word-Anchored SVML Engine</div>
  </div>
  <input type="range" id="scrubber" min="0" max="{timeline['metadata']['total_duration_ms']}" value="0">
  <div class="timeline-info">Time: <span id="time_display">0ms</span> / {timeline['metadata']['total_duration_ms']}ms</div>

  <script>
    const words = {json.dumps(timeline["words"])};
    const scrubber = document.getElementById('scrubber');
    const timeDisplay = document.getElementById('time_display');
    const badge = document.getElementById('badge');

    scrubber.addEventListener('input', (e) => {{
      const currMs = parseInt(e.target.value);
      timeDisplay.innerText = currMs + 'ms';

      words.forEach(w => {{
        const el = document.getElementById('span_' + w.id);
        if (currMs >= w.start_ms && currMs <= w.end_ms) {{
          el.className = 'word active-word';
        }} else {{
          el.className = 'word';
        }}
      }});

      if (currMs < 3800) {{
        badge.innerText = '🚨 RADICAL SHIFT';
        badge.style.background = '#EF4444';
      }} else {{
        badge.innerText = '⚡ REA CLONER';
        badge.style.background = '#06B6D4';
      }}
    }});
  </script>
</body>
</html>
"""
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    src_file = os.path.join(os.path.dirname(__file__), "template.svml")
    compiled = compile_svml(src_file)

    out_json = os.path.join(os.path.dirname(__file__), "compiled_timeline.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(compiled, f, indent=2)

    out_html = os.path.join(os.path.dirname(__file__), "preview.html")
    generate_html_preview(compiled, out_html)

    print(f"[✓] Compiled SVML with {compiled['metadata']['total_words']} words across {len(compiled['scenes'])} scenes.")
    print(f"[✓] Render manifest written to: {out_json}")
    print(f"[✓] Interactive player preview saved to: {out_html}")

if __name__ == "__main__":
    main()
