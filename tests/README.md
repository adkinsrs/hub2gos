# Testing notes

Our tests simply check that the returned Gosling Spec is correct, not that the paths are streamable. There is a HTML page called `quick_viewer.html` on the top-level of this repository that can be used to validate the Gosling visualization itself.

Gosling requires data sources to come from http/https instead of local file paths, whereas the UCSC track hub can use relative paths.