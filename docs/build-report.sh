#!/bin/bash
cd "$(dirname "$0")"
pandoc technical-report.md -o technical-report.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=2.5cm \
  -V fontsize=11pt
echo "Created technical-report.pdf"
