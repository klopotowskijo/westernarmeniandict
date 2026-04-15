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

## Files

- `index.html` - Main web interface
- `western_armenian_wiktionary.json` - Dictionary data (15MB)
- `graph_web.json` - Graph visualization data (6.9MB)
- `analyze_dict.py` - Dictionary analysis and statistics
- `parser_fast.py` - Etymology parsing utilities
- `auto_fill_all.py` - Automated etymology generation
- `cleanup_dict.py` - Data cleaning and validation

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
```

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