#!/usr/bin/env python3
"""
Fetch high-resolution album cover art from iTunes / Apple Music CDN for Girl Talk visualization.
Updates resources/AllDaySamplesWithSets.json with live, hotlink-friendly 600x600 artwork URLs.
"""

import json
import re
import time
import urllib.parse
import urllib.request
import os

JSON_PATH = "resources/AllDaySamplesWithSets.json"

def extract_text(val):
    if not val:
        return ""
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        res = []
        for item in val:
            if isinstance(item, str):
                res.append(item)
            elif isinstance(item, list) and len(item) >= 2:
                res.append(item[1])
            elif isinstance(item, list) and len(item) == 1:
                res.append(str(item[0]))
        return "".join(res)
    return str(val)

def clean_song_title(title):
    t = extract_text(title).strip('"\' ')
    t = re.split(r'\(portion sampled', t, flags=re.IGNORECASE)[0]
    t = re.split(r'\(samples\b', t, flags=re.IGNORECASE)[0]
    # Remove remix notes or trailing quotes
    return t.strip('"\' ')

def clean_artist(artist):
    a = extract_text(artist)
    return a.strip()

def extract_itunes_id(url):
    if not url:
        return None, None
    track_match = re.search(r'[?&]i=(\d+)', url)
    album_match = re.search(r'/id(\d+)', url)
    track_id = track_match.group(1) if track_match else None
    album_id = album_match.group(1) if album_match else None
    return track_id, album_id

def http_get(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_high_res_artwork(url100):
    if not url100:
        return None
    # Upgrade standard 100x100 thumbnail to 600x600
    return url100.replace("100x100bb.jpg", "600x600bb.jpg").replace("100x100bb.png", "600x600bb.png")

def main():
    if not os.path.exists(JSON_PATH):
        print(f"File {JSON_PATH} not found!")
        return

    print(f"Reading {JSON_PATH}...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    details = data.get("details", [])
    print(f"Found {len(details)} sample entries.")

    artwork_by_id = {}
    track_ids_to_fetch = set()
    album_ids_to_fetch = set()

    for d in details:
        t_id, a_id = extract_itunes_id(d.get("itunes-link"))
        if t_id:
            track_ids_to_fetch.add(t_id)
        elif a_id:
            album_ids_to_fetch.add(a_id)

    # 1. Batch lookup track IDs
    t_id_list = list(track_ids_to_fetch)
    print(f"Batch looking up {len(t_id_list)} track IDs from iTunes...")
    batch_size = 150
    for i in range(0, len(t_id_list), batch_size):
        batch = t_id_list[i:i+batch_size]
        url = f"https://itunes.apple.com/lookup?id={','.join(batch)}"
        try:
            res = http_get(url)
            for r in res.get("results", []):
                tid = str(r.get("trackId", ""))
                art = get_high_res_artwork(r.get("artworkUrl100"))
                if tid and art:
                    artwork_by_id[tid] = art
        except Exception as e:
            print(f"Error looking up batch: {e}")
        time.sleep(0.3)

    print(f"Resolved {len(artwork_by_id)} artworks via track IDs.")

    # 2. Search for remaining tracks
    artwork_by_query = {}
    unresolved_count = 0
    resolved_count = 0

    for idx, d in enumerate(details):
        t_id, a_id = extract_itunes_id(d.get("itunes-link"))
        art = artwork_by_id.get(t_id)

        artist_str = clean_artist(d.get("artist"))
        song_str = clean_song_title(d.get("song"))
        cache_key = (artist_str, song_str)

        if not art:
            if cache_key in artwork_by_query:
                art = artwork_by_query[cache_key]
            else:
                # Query iTunes search API
                query = f"{artist_str} {song_str}".strip()
                if query:
                    encoded = urllib.parse.quote_plus(query)
                    url = f"https://itunes.apple.com/search?term={encoded}&entity=song&limit=1"
                    try:
                        res = http_get(url)
                        results = res.get("results", [])
                        if results:
                            art = get_high_res_artwork(results[0].get("artworkUrl100"))
                    except Exception as e:
                        pass
                    time.sleep(0.1)
                artwork_by_query[cache_key] = art

        if art:
            d["album-image-link"] = art
            d["image-link"] = art
            resolved_count += 1
        else:
            unresolved_count += 1

        if (idx + 1) % 50 == 0 or (idx + 1) == len(details):
            print(f"Processed {idx + 1}/{len(details)} entries... (resolved: {resolved_count}, unresolved: {unresolved_count})")

    print(f"\nFinished! Total resolved: {resolved_count}/{len(details)} ({resolved_count*100//len(details)}%).")
    print(f"Saving updated data to {JSON_PATH}...")

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)

    # Also update AllDaySamples.json if it exists
    alt_path = "resources/AllDaySamples.json"
    if os.path.exists(alt_path):
        try:
            with open(alt_path, "w", encoding="utf-8") as f:
                json.dump(details, f)
            print(f"Also updated {alt_path}.")
        except Exception:
            pass

    print("Done!")

if __name__ == "__main__":
    main()
