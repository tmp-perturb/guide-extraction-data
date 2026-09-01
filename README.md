# guide-extraction-data

Omnibenchmark data-importer module for the K562 lane01 guide-extraction
benchmark. It materialises the externally supplied guide library, GEX matrix,
sgRNA FASTQ files, and reference matrix as first-stage DAG outputs.

Single files are symlinked; comma-separated FASTQ parts are concatenated. The
module performs no scientific processing.
