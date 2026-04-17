# Western Armenian Etymological Dictionary

An interactive web-based dictionary of Western Armenian with detailed etymological information.

## Features

- **18,938+ entries** with complete etymological data
- **Interactive search** with autocomplete suggestions
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

### Nayiri Scan Workflow
```bash
python3 download_nayiri_imaged_dictionary.py scans/nayiri_7 --dictionary-id 7 --start-page 78 --end-page 90
python3 ingest_nayiri_scans.py scans/nayiri_7 scans/nayiri_7/ocr/all_pages.txt --staged-json scans/nayiri_7/staged_entries.json --merge-output western_armenian_merged.json --source-name "Acharian Etymological Dictionary"
python3 review_merged_entries.py
```

`download_nayiri_imaged_dictionary.py` uses browser-style headers and referers so Nayiri scan PNGs can be fetched reliably. `ingest_nayiri_scans.py` depends on the macOS Swift toolchain and Vision framework.

The current site loads `western_armenian_merged.json` first when present, and falls back to `western_armenian_wiktionary.json` otherwise.

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