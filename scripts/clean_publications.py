import json
import re
from datetime import datetime
import os

def extract_year_from_title(title):
    """Extract year from title if it contains a year pattern"""
    # Look for 4-digit years in the title, but avoid patent numbers
    # Skip if it looks like a patent number (e.g., "Ser. No. 11/323,088")
    if re.search(r'Ser\.\s*No\.|Patent|Application', title, re.IGNORECASE):
        return None
    
    year_match = re.search(r'\b(19[8-9]\d|20[0-2]\d)\b', title)
    if year_match:
        year = int(year_match.group())
        # Sanity check: year should be reasonable
        if 1980 <= year <= 2025:
            return year
    return None

def extract_year_from_venue(venue):
    """Extract year from venue if it contains a year pattern"""
    if not venue:
        return None
    
    # Look for year patterns in venue names
    year_match = re.search(r'\b(19[8-9]\d|20[0-2]\d)\b', venue)
    if year_match:
        year = int(year_match.group())
        # Sanity check: year should be reasonable
        if 1980 <= year <= 2025:
            return year
    return None

def clean_title(title):
    """Clean up title formatting"""
    if not title:
        return ""
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title.strip())
    return title

def clean_authors(authors):
    """Clean up authors list"""
    if not authors:
        return []
    if isinstance(authors, str):
        # Split by "and" or comma
        authors = re.split(r'\s+and\s+|\s*,\s*', authors)
    return [author.strip() for author in authors if author.strip()]

def clean_venue(venue):
    """Clean up venue name"""
    if not venue:
        return ""
    # Remove extra whitespace and common artifacts
    venue = re.sub(r'\s+', ' ', venue.strip())
    return venue

def estimate_year_from_context(pub):
    """Try to estimate year from various sources"""
    # Try title first
    year = extract_year_from_title(pub.get('title', ''))
    if year:
        return year
    
    # Try venue
    year = extract_year_from_venue(pub.get('venue', ''))
    if year:
        return year
    
    # Try snippet (but be more careful)
    snippet = pub.get('snippet', '')
    if snippet and not re.search(r'Ser\.\s*No\.|Patent|Application', snippet, re.IGNORECASE):
        year = extract_year_from_title(snippet)
        if year:
            return year
    
    return None

def clean_publications(input_file, output_file):
    """Clean and improve publications data"""
    print(f"Loading publications from {input_file}...")
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    publications = data.get('publications', [])
    cleaned_pubs = []
    
    print(f"Processing {len(publications)} publications...")
    
    for i, pub in enumerate(publications):
        # Clean basic fields
        cleaned_pub = {
            "title": clean_title(pub.get('title', '')),
            "authors": clean_authors(pub.get('authors', [])),
            "venue": clean_venue(pub.get('venue', '')),
            "cited_by": int(pub.get('cited_by', 0)),
            "url": pub.get('url', ''),
            "snippet": pub.get('snippet', '')
        }
        
        # Fix year
        original_year = pub.get('year', 0)
        if original_year == 0:
            estimated_year = estimate_year_from_context(pub)
            if estimated_year:
                cleaned_pub["year"] = estimated_year
                print(f"  Fixed year for '{cleaned_pub['title'][:50]}...' from 0 to {estimated_year}")
            else:
                cleaned_pub["year"] = 0
        else:
            cleaned_pub["year"] = original_year
        
        # Try to improve citation count (if it's 0, might be missing data)
        if cleaned_pub["cited_by"] == 0:
            # Could add logic here to try to get citation data from other sources
            pass
        
        # Try to add missing URLs
        if not cleaned_pub["url"] and cleaned_pub["title"]:
            # Could add logic here to search for paper URLs
            pass
        
        cleaned_pubs.append(cleaned_pub)
    
    # Sort by year (newest first), then by title for same year
    cleaned_pubs.sort(key=lambda x: (x["year"], x["title"]), reverse=True)
    
    # Create output data
    output_data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "cleaned_at": datetime.utcnow().isoformat() + "Z",
        "total_publications": len(cleaned_pubs),
        "publications_with_years": len([p for p in cleaned_pubs if p["year"] > 0]),
        "publications_with_citations": len([p for p in cleaned_pubs if p["cited_by"] > 0]),
        "publications": cleaned_pubs
    }
    
    # Save cleaned data
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nCleaning complete!")
    print(f"  Total publications: {len(cleaned_pubs)}")
    print(f"  Publications with years: {output_data['publications_with_years']}")
    print(f"  Publications with citations: {output_data['publications_with_citations']}")
    print(f"  Saved to: {output_file}")
    
    return output_data

if __name__ == "__main__":
    input_file = "../_data/publications.json"
    output_file = "../_data/publications_cleaned.json"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run gscholar.py first.")
        exit(1)
    
    clean_publications(input_file, output_file) 