# Western Armenian Etymological Dictionary

An interactive web-based dictionary of Western Armenian with detailed etymological information.

## Features

- **18,938+ entries** with complete etymological data
- **Interactive search** with autocomplete suggestions
- **Inflected form lemmatization** - click on any verb conjugation or noun declension to jump to the base entry
- **Language-based search** - find all words borrowed from Turkish, Persian, Greek, etc.
- **Etymological graph** showing language relationships and borrowing patterns
- **Modern web interface** with clean, readable design

## Live Demo

[View the dictionary online](https://yourusername.github.io/western-armenian-etymology/)

## Search Examples

### Word Search
- `ժամանակ` (time)
- `հայր` (father)
- `մայր` (mother)
- `գիրք` (book)
- `սեր` (love)

### Language Search
- `turkish` - shows all Turkish loanwords
- `persian` - shows all Persian borrowings
- `greek` - shows all Greek loanwords
- `russian` - shows all Russian loanwords

## Etymology Sources

The dictionary covers borrowings from:
- **Classical Armenian** (4,700+ words)
- **Persian** (73 words)
- **Turkish/Ottoman** (29 words)
- **Greek** (61 words)
- **Russian** (759 words)
- **French** (49 words)
- **Arabic** (30 words)
- **Latin** (83 words)

## Technical Details

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Visualization**: vis.js for interactive graphs
- **Data**: JSON format with structured etymology information
- **Processing**: Python scripts for data analysis and maintenance
- **Indexing**: Client-side in-memory index built from `western_armenian_wiktionary.json` in `index.html`

## Files

- `index.html` - Main web interface
- `western_armenian_wiktionary.json` - Dictionary data (15MB)
- `western_armenian_merged.json` - Dictionary data plus Nayiri-only lemmas
- `graph_web.json` - Graph visualization data (6.9MB)
- `analyze_dict.py` - Dictionary analysis and statistics
- `parser_fast.py` - Etymology parsing utilities
- `auto_fill_all.py` - Automated etymology generation
- `cleanup_dict.py` - Data cleaning and validation
- `merge.py` - Merge Wiktionary and Nayiri into a single searchable dictionary
- `review_merged_entries.py` - Review merged data for duplicates and weak entries
- `ocr_etym_dict_to_json.py` - Convert OCR text from scanned dictionaries into staged JSON
- `download_nayiri_imaged_dictionary.py` - Download Nayiri imaged-dictionary manifests, page HTML, and scan images
- `ocr_images_with_vision.swift` - OCR helper using macOS Vision for scan images
- `ingest_nayiri_scans.py` - OCR downloaded Nayiri scans and optionally stage/merge them
- `ingest_martirosyan_etymologies_pdf.py` - Extract ETYM-focused snippets from Martirosyan (2011) PDF for manual etymology curation
- `ingest_calfa_etymology_xml.py` - Parse Calfa's `etymology01.xml` into staged JSON and etymology-only review artifacts
- `compare_calfa_etymology.py` - Compare staged Calfa entries against the current merged dictionary before any merge
- `merge_calfa_etymology.py` - Stage and merge the conservative Calfa overlap subset into the current merged dictionary

## Development

### Prerequisites
- Python 3.6+
- Modern web browser

### Running Locally
1. Clone the repository
2. Open `index.html` in your web browser
3. No server required - runs entirely client-side

### Data Analysis
```bash
python3 analyze_dict.py  # Generate statistics
python3 parser_fast.py   # Parse etymologies
python3 cleanup_dict.py  # Clean data
python3 infer_morphological_etymology.py --dry-run  # Preview inferred prefix/root/suffix etymologies
python3 infer_morphological_etymology.py --replace-weak  # Fill missing/weak etymologies with explicit inferred breakdowns
python3 build_external_etymology_queue.py  # Build prioritized unresolved queue + external source adapter manifest
python3 merge.py         # Build merged Wiktionary + Nayiri dataset
python3 merge.py --extra-json staged_ocr_entries.json  # Merge OCR-imported entries too
python3 review_merged_entries.py  # Review merged dataset quality
```

### Adding More Sources
```bash
python3 ocr_etym_dict_to_json.py scans/my_ocr.txt staged_ocr_entries.json --source-name "Acharian Etymological Dictionary"
python3 merge.py --extra-json staged_ocr_entries.json
python3 review_merged_entries.py
```

### Martirosyan (2011) PDF Workflow
```bash
# 1) Place/download the PDF once
mkdir -p sources/armenian-etymologies-2011
curl -L "https://vahagnakanch.wordpress.com/wp-content/uploads/2011/04/armenian-etymologies.pdf" \
	-o sources/armenian-etymologies-2011/armenian-etymologies.pdf

# 2) Extract plain text + ETYM snippets + optional queue exact-match hits
python3 ingest_martirosyan_etymologies_pdf.py

# 3) Build staged merge entries (confidence-thresholded)
python3 build_martirosyan_staged_entries.py --min-confidence medium

# 4) Optionally merge staged entries into dictionary
python3 merge.py --extra-json sources/armenian-etymologies-2011/staged_martirosyan_entries.json

# 5) Review outputs
# - sources/armenian-etymologies-2011/etym_sections.jsonl
# - sources/armenian-etymologies-2011/queue_hits.jsonl
# - sources/armenian-etymologies-2011/staged_martirosyan_entries.json
# - sources/armenian-etymologies-2011/staged_martirosyan_report.json
```

The Martirosyan integration is designed for manual curation: it creates page-indexed snippet artifacts rather than auto-writing etymology entries.

### Calfa etymology01.xml Workflow
```bash
# 1) Fetch and parse the XML into staged review artifacts
python3 ingest_calfa_etymology_xml.py --fetch-missing

# 2) Compare Calfa headwords against the current merged dictionary
python3 compare_calfa_etymology.py

# 3) Build merge-ready Calfa entries and apply the conservative overlap subset
python3 merge_calfa_etymology.py

# 4) Review outputs
# - sources/calfa-etymology/staged_calfa_entries.json
# - sources/calfa-etymology/calfa_etymology_only.jsonl
# - sources/calfa-etymology/calfa_parse_report.json
# - sources/calfa-etymology/calfa_comparison_rows.jsonl
# - sources/calfa-etymology/calfa_comparison_report.json
# - sources/calfa-etymology/staged_calfa_merge_entries.json
# - sources/calfa-etymology/calfa_merge_report.json
```

The Calfa XML integration stays conservative: it only auto-merges unambiguous, non-proper-noun matches where the current entry lacks a meaningful etymology, and it records excluded homograph collisions in the merge report.

### Nayiri Scan Workflow
```bash
python3 download_nayiri_imaged_dictionary.py scans/nayiri_7 --dictionary-id 7 --start-page 78 --end-page 90
python3 ingest_nayiri_scans.py scans/nayiri_7 scans/nayiri_7/ocr/all_pages.txt --staged-json scans/nayiri_7/staged_entries.json --merge-output western_armenian_merged.json --source-name "Acharian Etymological Dictionary"
python3 review_merged_entries.py
```

`download_nayiri_imaged_dictionary.py` uses browser-style headers and referers so Nayiri scan PNGs can be fetched reliably. `ingest_nayiri_scans.py` depends on the macOS Swift toolchain and Vision framework.

The current site loads `western_armenian_merged.json` first when present, and falls back to `western_armenian_wiktionary.json` otherwise.

The UI automatically lemmatizes all inflected forms (verb conjugations, noun declensions) using the `lemmatization_index.json` file. This maps ~80% of inflectional variants to their base form, so clicking on inflected forms (e.g., կսրբեի → սրբել) displays the main entry instead of "not found".

### Lemmatization Index
```bash
# Rebuild the lemmatization index after updating alternative_forms
python3 build_lemmatization_index.py
```

This creates `lemmatization_index.json` which maps inflected forms to their lemmas via an Armenian morphology heuristic.

## Contributing

Contributions welcome! Areas for improvement:
- Additional etymological research
- More language coverage
- UI/UX enhancements
- Bug fixes and optimizations

## License

This project is open source. Please credit the original Wiktionary contributors.

## Credits

- Data sourced from Wiktionary's Armenian language sections
- Etymology research and compilation
- Web interface design and implementation

## Contact

For questions or contributions, please open an issue on GitHub.