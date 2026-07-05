# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Notes

- Currently the trackhub parsing works only for local files. The code from where this package originated actually parses remote copies of files, so I plan to make this work for local and remote trackhub files soon.

### Added

- Added pytest CI/CD Github Action with an accompanying badge in the README
- Assembly CLI argument (-a) to specify assembly for a standard UCSC trackhub file. This is important because the genomes.txt file can reference trackDb files for multiple assemblies. This argument is not needed for the useOneFile mode, as only one assembly is allowed for that

### Changed

- Changing default track height from 25 to 50px
- Added "axis=top" to the x-axis property for each track.
- HiC tracks will use the "width" value for width and height.  This helps with keeping the aspect ratio square.

### Fixed

- Fixing bug with width not being set properly for non-multiwig track files
- Uploading from a standard UCSC normal Trackhub file works now.

## [0.1.1] - 2026-07-03

### Added

- A CHANGELOG.md

### Changed

- Changing minimum python version from 3.10 to 3.11 as the end-of-life for 3.10 is in October 2026
- Adjusting some things in the pyproject.toml

## [0.1.0] - 2026-07-03

### Added

- Core implementation of the Track Hub parsing engine.
- Data models for various Gosling tracks.
  - BAM
  - BigBed
  - BigInteract
  - BigWig
  - HiC
  - VCF
- Container management for `MultiWigSpec` overlay View.
- Central `TrackSpecFactory` for dynamic track initialization.
- Central `ViewSpecFactory` for dynamic view initialization
- Command-line interface via `hub2gos.cli`.
- Comprehensive test suite covering compiler and factory modules. All tests passed... for now.