import json

# Load Calfa data
with open('sources/calfa-etymology/staged_calfa_merge_entries.json', encoding='utf-8') as f:
    calfa_data = json.load(f)

# Create a lookup dictionary for Calfa entries by title
calfa_lookup = {}
for entry in calfa_data:
    title = entry.get('title', '').lower()
    calfa_lookup[title] = entry

# Load main dictionary
with open('western_armenian_merged.json', 'r', encoding='utf-8') as f:
    main_data = json.load(f)

# Add source attribution
fixed_count = 0
for entry in main_data:
    title = entry.get('title', '').lower()
    if title not in calfa_lookup:
        continue
    
    calfa_entry = calfa_lookup[title]
    
    # Extract source from etymology field
    etymology_list = calfa_entry.get('etymology', [])
    sources_found = []
    
    for ety_item in etymology_list:
        if ety_item.get('source'):
            sources_found.append(ety_item.get('source'))
        if ety_item.get('citations'):
            for citation in ety_i            for citation in ety_i         # Look for    aṙean/Adjaria            for citation in ety_i            for citation in ety_i         # Look for    a�ow            for citation in urces_found.append('Ačaṙean (1926)')
    
    # Add the     # Add the o main entry
    if sources_f    if sources_f    if sources_f    if so l    if sources_f    if sourcesove    if sources_f    iixed_count += 1
        
        # Also add definition source if availabl        # Also add definitit('definition_source'):
                  'd                  'd  alfa_entry.get('definition_source')
    
    # Mark that this came from Calfa
    entry['data_so   e'    entry['data_so   e'    entry['datr   tion to {fixed_count} entries")

# Count by source type
source_counts = {}
for entry in main_data:
    if entry.get('etym   gy    if entry.get('etym   gy    ify.get('etymology_source')
        if i        if i        if i        if i        if i   ces:
                source_counts[s] = sour                source_counts[s] = sour                source_counts[s] = sour                source_counts[s] = sour                source_counts[s] = sour                source_counts[s] = sour                source_counts[s] = sour                source_countsount}")    Save
with open('western_armenian_mergwith open('western_armenian_mergwith open('western_armenian_mergwith open('western_armenian_mergwith open('western_armenian_merenian_merged.json")
