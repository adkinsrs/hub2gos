# hub2gos

[![PyPI Version](https://img.shields.io/pypi/v/hub2gos)](https://pypi.org/project/hub2gos/) [![Supported Python Versions](https://img.shields.io/pypi/pyversions/hub2gos)](https://pypi.org/project/hub2gos/) [![License](https://img.shields.io/github/license/adkinsrs/hub2gos)](https://github.com/adkinsrs/hub2gos/blob/main/LICENSE)

[![Tests](https://github.com/adkinsrs/hub2gos/actions/workflows/test.yml/badge.svg)](https://github.com/adkinsrs/hub2gos/actions/workflows/test.yml) [![codecov](https://codecov.io/github/adkinsrs/hub2gos/graph/badge.svg?token=8AXL4214PT)](https://codecov.io/github/adkinsrs/hub2gos)


Transpiler to map a UCSC Trackhub configuration to a Gosling spec

## Installation

Install the package directly from PyPI:

```bash
pip install hub2gos
```

## Quickstart

To compile a UCSC trackhub into a Gosling specification from the command line, simply point the transpiler at your hub.txt file:

```bash
python -m hub2gos.cli path/to/hub.txt
```

hub2gos supports both the standard UCSC Trackhub mode and the useOneFile mode.

## CLI Usage

```text
usage: python -m hub2gos.cli [-h] [-o OUTPUT] [-c COORDS] [-a ASSEMBLY] [-v] hub_file

Convert UCSC TrackHub track information to a Gosling Spec

positional arguments:
  hub_file              Path to local hub.txt file. Supports both standard and useOneFile modes.

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Output JSON file path (prints to stdout if omitted)
  -c, --coords COORDS   Optional coordinates to set starting domain of tracks.
                        Must be in the format 'chr:start-end' (e.g., 'chr1:1000000-2000000')
  -a, --assembly ASSEMBLY
                        Optional genome assembly (e.g., 'hg38', 'mm10').
                        If not provided, will throw an error in standard mode.
                        This value is not used in useOneFile mode.
  -v, --verbose         Enable detailed logging output
```

## Input Data Specifications & Compression Rules

When converting a UCSC Track Hub configuration using `hub2gos`, input data URLs must adhere strictly to the coordinate streaming capabilities of modern web browsers. In addition, some UCSC Track Hub file types are not compatible and must have an alternate file path under the `gos_url` property that will be used to read the data into Gosling instead.  Otherwise the transpiler will use the `bigDataUrl` property instead.

This utility will return a Gosling Spec for the UCSC trackhub input, but does not validate that the supplied paths are streamable. There is a HTML page called `quick_viewer.html` on the top-level of this repository that can be used to validate the Gosling visualization itself by passing in the JSON spec.

### Supported Formats & Compression Matrices

| UCSC Track Type | Expected File Suffix(es) | gos_url file? | Tabix Index Required? | Work-in-progress? |
| :--- | :--- | :--- | :--- | :--- |
| **BAM** | `.bam` | No | Yes (`.bam.bai`) | Yes |
| **BigBed** | `.bb`, `.bigbed` | `.bed.gz` | **Yes (BGZF-formatted `.tbi`)**  | No |
| **BigInteract** | `.bi`, `.bigInteract` | "beddb" HiGlass tileset | No | No |
| **BigWig** | `.bw`, `.bigwig` | No | No | No |
| **HiC** | `.hic` | "cooler" HiGlass tileset | No | No |
| **VCF** | `.vcf.gz` | No | **Yes (BGZF-formatted `.tbi`)** | Yes |

> ⚠️ **Performance Note on BAM Tracks:** While natively supported by Gosling, rendering BAM files over a broad genomic coordinate range can degrade client-side performance. For better performance, consider converting BAM files to BigWig (for depth density) or BigBed/BED (for structural mutations) during your server pipeline staging.

### Crucial Constraints

None of these contraints will prevent you from generating the Gosling spec JSON. They will however prevent you from streaming the data in the Gosling viewer.

1. **Plaintext Text Files:** Uncompressed tabular streams (e.g., raw `.bed` or `.vcf` text targets) are unsupported for chunked client-side streaming. Text tracking formats must be block-gzipped using `bgzip` before indexing. [Documentation on bgzip](https://www.htslib.org/doc/bgzip.html)
2. **Alternative Compressors:** High-ratio archival compressors such as `bzip2` (`.bz2`) or `xz` (`.xz`) are completely unsupported. These engines do not produce block-level byte partitions, making selective genomic coordinate slicing over network requests impossible.
3. For any track type that recommends serving files on a HiGlass server, you can peruse the [HiGlass documentation](https://docs.higlass.io/) to learn how to set up a HiGlass server, aggregate files with Clodius, and ingest them into HiGlass.