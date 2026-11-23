*# Corpus Capacity Estimate*



*## Scope*



*The initial collection target is NFHS-5 Tamil Nadu:*



*- 1 Tamil Nadu state fact sheet*

*- 32 survey-era district fact sheets*

*- Total target: 33 fact sheets*



*The expanded target includes NFHS-4 and NFHS-5 national, state,*

*and district reports and fact sheets.*



*## Current Measurement Status*



*One NFHS-5 Tamil Nadu state and district fact-sheet compendium*

*has been manually collected and registered.*



*### Actual measurements*



*- Collected PDF documents: 1*

*- Fact sheets identified: 33*

*- State fact sheets: 1*

*- District fact sheets: 32*

*- Total PDF pages: 204*

*- Fact-sheet section pages: 198*

*- Front matter pages: 4*

*- Closing pages: 2*

*- File size: 6,779,076 bytes*

*- File size: approximately 6.47 MiB*

*- Average fact-sheet pages: 6*

*- Average storage per fact sheet (rough allocation): approximately 0.196 MiB*

*- SHA-256 verified against the download manifest*

*- Collection method: Manual download*



*The per-fact-sheet storage value is an allocation estimate based on*

*the complete compendium size. It is not the measured size of an*

*individual fact-sheet PDF.*



*## Estimation Method*



*Capacity estimates use actual collected and verified documents.*



*For each document, record:*



*- Document title*

*- Survey round*

*- Geography*

*- File size in bytes*

*- PDF page count*

*- Source URL*

*- SHA-256 hash*

*- Collection method*

*- Licence/reuse status*



*Calculate:*



*- Total document count*

*- Total fact-sheet count*

*- Total page count*

*- Average pages per document*

*- Total storage size*

*- Average storage size per document*



*## Scaling the Corpus*



*The initial measured baseline is one 204-page compendium containing*

*33 fact sheets and occupying approximately 6.47 MiB.*



*Use this baseline cautiously when planning expanded NFHS-4 and NFHS-5*

*corpus storage. Individual documents may vary significantly in page*

*count, image resolution, tables, and PDF compression.*



*Expanded corpus estimates remain planning estimates until additional*

*documents are acquired and measured.*



*## Limitations*



*- Only one compendium has been collected and measured.*

*- Actual original individual fact-sheet PDF sizes have not been measured; reconstructed extraction sizes are experimental and inflated by duplicated PDF resources.*

*- Expanded NFHS-4/NFHS-5 corpus size is not yet measured.*

*- Licence and reuse terms remain unverified.*

*- Source access restrictions and reuse terms must be respected.*


## Experimental Individual Fact-Sheet Extraction

Using pypdf 7.1.1, all 33 six-page fact-sheet sections were reconstructed in memory from the collected 204-page compendium. No individual PDFs were saved and the original PDF was not modified.

### Reconstructed PDF measurements

- Fact sheets reconstructed: 33
- Minimum reconstructed size: 1,416,968 bytes
- Maximum reconstructed size: 1,480,499 bytes
- Mean reconstructed size: 1,419,212.88 bytes
- Median reconstructed size: 1,417,242 bytes
- Total reconstructed size: 46,834,025 bytes
- Original compendium size: 6,779,076 bytes
- Reconstruction inflation ratio: 6.91x

### Interpretation and limitations

- These are reconstructed PDF sizes, not original individual source-PDF sizes.
- Reconstructing pages duplicates shared PDF resources, inflating the total to approximately 6.91 times the original compendium size.
- The measurements must not be used as actual individual-download storage estimates.
- The original rough allocation of approximately 0.196 MiB per fact sheet remains the baseline storage allocation for this single compendium only.
- Actual individual fact-sheet file sizes remain unverified.
