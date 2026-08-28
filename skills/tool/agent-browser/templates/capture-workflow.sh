#!/bin/bash
# Template: Content Capture Workflow
# Extract content from web pages with optional authentication

set -euo pipefail

TARGET_URL="${1:?Usage: $0 <url> [output-dir]}"
OUTPUT_DIR="${2:-.}"

echo "Capturing content from: $TARGET_URL"
mkdir -p "$OUTPUT_DIR"

# Authenticated capture must use the authenticated-session owner and prove that
# restored state reaches the expected protected route. Never load unvalidated
# state and publish a captured login/error page as successful output.

# Navigate to target page
agent-browser open "$TARGET_URL"
agent-browser wait --load networkidle

# Get page metadata
PAGE_TITLE="$(agent-browser get title)"
PAGE_URL="$(agent-browser get url)"
echo "Page title: $PAGE_TITLE"
echo "Page URL: $PAGE_URL"

# Capture full page screenshot
agent-browser screenshot --full "$OUTPUT_DIR/page-full.png"
echo "Screenshot saved: $OUTPUT_DIR/page-full.png"

# Get page structure
agent-browser snapshot -i > "$OUTPUT_DIR/page-structure.txt"
echo "Structure saved: $OUTPUT_DIR/page-structure.txt"

# Extract main content
# Adjust selector based on target site structure
# agent-browser get text @e1 > "$OUTPUT_DIR/main-content.txt"

# Extract specific elements (uncomment as needed)
# agent-browser get text "article" > "$OUTPUT_DIR/article.txt"
# agent-browser get text "main" > "$OUTPUT_DIR/main.txt"
# agent-browser get text ".content" > "$OUTPUT_DIR/content.txt"

# Get full page text
agent-browser get text body > "$OUTPUT_DIR/page-text.txt"
echo "Text content saved: $OUTPUT_DIR/page-text.txt"

# Optional: Save as PDF
agent-browser pdf "$OUTPUT_DIR/page.pdf"
echo "PDF saved: $OUTPUT_DIR/page.pdf"

# Optional: Capture with scrolling for infinite scroll pages
# scroll_and_capture() {
#     local count=0
#     while [[ $count -lt 5 ]]; do
#         agent-browser scroll down 1000
#         agent-browser wait 1000
#         ((count++))
#     done
#     agent-browser screenshot --full "$OUTPUT_DIR/page-scrolled.png"
# }
# scroll_and_capture

# Cleanup
agent-browser close

echo ""
echo "Capture complete! Files saved to: $OUTPUT_DIR"
ls -la "$OUTPUT_DIR"
