# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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