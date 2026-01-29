from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import re
import itertools
from collections import defaultdict
from typing import Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# In-memory storage for latest analysis
last_analysis: Dict[str, Any] = {}


def analyze_script(text: str) -> Dict[str, Any]:
    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # --------- 1) CHARACTER NAMES FROM CUES (ALL CAPS LINES) ---------
    lines = text.split("\n")
    character_lines = []
    for line in lines:
        stripped = line.strip()
        # Heuristic: uppercase, at least 3 chars, not too long
        if (
            len(stripped) >= 3
            and len(stripped) <= 40
            and stripped.isupper()
            and re.match(r"^[A-Z0-9 '\-()]+$", stripped)
        ):
            character_lines.append(stripped)

    unique_chars = sorted(set(character_lines))
    if not unique_chars:
        unique_chars = ["UNKNOWN"]
        character_lines = ["UNKNOWN"]

    # Frequency of character cue lines
    freq = {c: character_lines.count(c) for c in unique_chars}

    # --------- 2) TIER DISTRIBUTION (A/B/C) ---------
    tiers = [
        {
            "tier": "A",
            "count": len([c for c, f in freq.items() if f > 50]),
            "characters": [c for c, f in freq.items() if f > 50],
        },
        {
            "tier": "B",
            "count": len([c for c, f in freq.items() if 20 <= f <= 50]),
            "characters": [c for c, f in freq.items() if 20 <= f <= 50],
        },
        {
            "tier": "C",
            "count": len([c for c, f in freq.items() if f < 20]),
            "characters": [c for c, f in freq.items() if f < 20],
        },
    ]

    # --------- 3) SCENE SPLITTING ---------
    # Naive: blank lines separate scenes
    scene_blocks = re.split(r"\n\s*\n+", text)
    scenes_chars = []
    for block in scene_blocks:
        # Find character cues inside this scene
        chars_in_scene = set(
            re.findall(r"\n([A-Z][A-Z0-9 '\-()]{2,})\n", "\n" + block + "\n")
        )
        if chars_in_scene:
            scenes_chars.append(chars_in_scene)

    # --------- 4) RELATIONSHIP WEIGHTS (SHARED SCENES) ---------
    pair_counts: Dict[tuple, int] = defaultdict(int)
    for chars in scenes_chars:
        for a, b in itertools.combinations(sorted(chars), 2):
            pair_counts[(a, b)] += 1

    links = []
    MIN_SHARED_SCENES = 1    # Set to 2 if you want only strong relationships
    for (a, b), w in pair_counts.items():
        if w >= MIN_SHARED_SCENES:
            links.append({"source": a, "target": b, "weight": w})

    nodes = [{"name": c} for c in unique_chars]

    # --------- 5) NARRATIVE INTENSITY (10 SEGMENTS) ---------
    total_scenes = max(len(scenes_chars), 1)
    chunk_size = max(total_scenes // 10, 1)
    counts = []
    for i in range(10):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, total_scenes)
        if start >= total_scenes:
            count = 0
        else:
            count = len(scenes_chars[start:end])
        counts.append(count)

    max_count = max(counts) if counts else 1
    intensity_points = []
    for i, count in enumerate(counts):
        intensity_value = round(count / max_count, 2) if max_count > 0 else 0.0
        intensity_points.append(
            {
                "chapter": i + 1,
                "title": f"Segment {i + 1}",
                "intensity": intensity_value,
            }
        )

    return {
        "characterNetwork": {
            "nodes": nodes,
            "links": links,
        },
        "tierDistribution": {
            "tiers": tiers,
        },
        "narrativeIntensity": {
            "intensity": intensity_points,
        },
    }


@app.post("/api/upload-script")
async def upload_script(file: UploadFile = File(...)):
    global last_analysis
    raw = await file.read()
    text = raw.decode(errors="ignore")
    analysis = analyze_script(text)
    last_analysis = analysis
    return analysis


def get_or_default(key: str) -> Any:
    """Return last analysis for a section, or default demo data."""
    if last_analysis:
        return last_analysis[key]

    # Default demo data before any upload
    if key == "characterNetwork":
        return {
            "nodes": [{"name": "Marcus"}, {"name": "Darren"}, {"name": "Elijah"}],
            "links": [
                {"source": "Marcus", "target": "Darren", "weight": 3},
                {"source": "Marcus", "target": "Elijah", "weight": 2},
            ],
        }
    if key == "tierDistribution":
        return {
            "tiers": [
                {"tier": "A", "count": 2, "characters": ["Marcus", "Elijah"]},
                {"tier": "B", "count": 1, "characters": ["Darren"]},
                {"tier": "C", "count": 0, "characters": []},
            ]
        }
    if key == "narrativeIntensity":
        return {
            "intensity": [
                {"chapter": 1, "title": "Segment 1", "intensity": 0.3},
                {"chapter": 2, "title": "Segment 2", "intensity": 0.7},
                {"chapter": 3, "title": "Segment 3", "intensity": 1.0},
            ]
        }
    return {}


@app.get("/api/character-network")
async def get_character_network():
    return get_or_default("characterNetwork")


@app.get("/api/tier-distribution")
async def get_tier_distribution():
    return get_or_default("tierDistribution")


@app.get("/api/narrative-intensity")
async def get_narrative_intensity():
    return get_or_default("narrativeIntensity")


if __name__ == "__main__":
    uvicorn.run("script_parser:app", host="0.0.0.0", port=8081, reload=True)
