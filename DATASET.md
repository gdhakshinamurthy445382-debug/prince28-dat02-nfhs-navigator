
# NFHS Navigator Dataset

## Purpose

This dataset supports NFHS Navigator, a project for exploring and understanding indicators from the National Family Health Survey (NFHS).

## Initial Corpus Target

NFHS-5 (2019–21), Tamil Nadu:

- Tamil Nadu state fact sheet
- 32 district fact sheets (NFHS-5 survey coverage)
- Target total: 33 fact sheets

## Source

- Organization: International Institute for Population Sciences (IIPS)
- Survey: National Family Health Survey (NFHS)
- Official portal: http://rchiips.org/nfhs/

## License and Terms

Reuse and redistribution terms for each document have not yet been verified.

No blanket license is assumed for NFHS documents. Documents must be reviewed for applicable reuse terms before redistribution.

## Collection Status

- NFHS source portal identified (IIPS/NFHS).
- The original NFHS-5 Tamil Nadu compendium was previously recorded as manually collected.
- Historical compendium metadata records 204 pages and 33 fact sheets.
- The Tamil Nadu compendium PDF is currently missing from the local repository.
- Its historical SHA-256 and file metadata are retained in `data/sources/source_manifest.json`.
- NFHS-5 India Report downloaded successfully.
- NFHS-6 India and State Fact Sheets downloaded successfully.
- NFHS-5 Himachal Pradesh download was blocked by `robots.txt`.
- Current local corpus: 2 downloaded PDF documents.
- Download status, URLs, file paths, hashes, byte sizes, and source metadata are recorded in `data/manifest.jsonl`.
- Reuse/licensing terms remain unverified for downloaded documents.
- The NFHS-4 corpus has not been collected.

## Data Integrity

- Downloaded files are tracked using a manifest containing download status, source URL, file path, and SHA-256 hash where applicable.
- Original source documents are preserved separately from processed data.
- Raw PDFs are excluded from version control.

## Future Scope

The expanded corpus target includes NFHS-4 and NFHS-5:

- National reports
- State reports
- State fact sheets
- District fact sheets

The expanded corpus may contain 10,000+ pages. This is an estimate and will be refined after measuring actual downloaded documents.
