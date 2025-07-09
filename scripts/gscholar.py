import os
import json
from scholarly import scholarly
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────
AUTHOR_ID  = "YArRsvEAAAAJ"                      # your Google Scholar author_id
OUTPUT     = "_data/publications.json"           # path in your repo
# ─────────────────────────────────────────────────────────────

def fetch_publications():
    try:
        # Get the author by ID
        author = scholarly.search_author_id(AUTHOR_ID)
        print(f"Found author: {author.get('name', 'Unknown')}")
        
        # Get all publications - we need to fill the publications
        author_filled = scholarly.fill(author, sections=['publications'])
        
        publications = []
        if 'publications' in author_filled:
            for pub in author_filled['publications']:
                try:
                    # Get detailed publication info
                    pub_filled = scholarly.fill(pub)
                    
                    # Handle both object and dict formats
                    if hasattr(pub_filled, 'bib'):
                        bib = pub_filled.bib
                        # Improved citation extraction
                        cited_by = 0
                        if hasattr(pub_filled, 'num_citations'):
                            cited_by = int(getattr(pub_filled, 'num_citations', 0) or 0)
                        elif hasattr(pub_filled, 'citedby'):
                            cited_by = int(getattr(pub_filled, 'citedby', 0) or 0)
                        else:
                            cited_by = 0
                    else:
                        # Handle as dictionary
                        bib = pub_filled.get('bib', {})
                        cited_by = int(pub_filled.get('num_citations', 0) or pub_filled.get('citedby', 0) or 0)
                    
                    pub_data = {
                        "title": bib.get('title', ''),
                        "year": int(bib.get('year', 0)),
                        "authors": bib.get('author', []),
                        "venue": bib.get('journal', ''),
                        "cited_by": cited_by,
                        "url": bib.get('url', ''),
                        "snippet": bib.get('abstract', '')
                    }
                    publications.append(pub_data)
                    print(f"Processed: {pub_data['title'][:50]}...")
                except Exception as e:
                    print(f"Error processing publication: {e}")
                    continue
        
        return publications
    except Exception as e:
        print(f"Error fetching publications: {e}")
        return []

def normalize(pub):
    return {
        "title":      pub.get("title"),
        "year":       int(pub.get("year") or 0),
        "authors":    pub.get("authors"),
        "venue":      pub.get("venue"),
        "cited_by":   int(pub.get("cited_by", 0)),
        "url":        pub.get("url"),
        "snippet":    pub.get("snippet"),
    }

def main():
    print("Fetching publications from Google Scholar...")
    pubs = fetch_publications()
    data = [normalize(p) for p in pubs]
    # sort newest → oldest
    data.sort(key=lambda x: x["year"], reverse=True)

    # annotate a timestamp so you know when this ran
    out = {
      "generated_at": datetime.utcnow().isoformat() + "Z",
      "publications": data
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {len(data)} pubs to {OUTPUT}")

if __name__ == "__main__":
    main()