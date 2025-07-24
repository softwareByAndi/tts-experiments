#!/bin/bash

# Piper TTS Test Runner
# Simple script to run the test suite with various options

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
MODEL="en_US-amy-medium"
OUTPUT_DIR="test_outputs"

# Function to display help
show_help() {
    echo "Piper TTS Test Runner"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -m, --model MODEL    Specify Piper model (default: en_US-amy-medium)"
    echo "  -o, --output DIR     Specify output directory (default: test_outputs)"
    echo "  -c, --category CAT   Run only specific test category"
    echo "  -l, --list           List available test categories"
    echo "  -q, --quick          Run quick test (baseline only)"
    echo ""
    echo "Examples:"
    echo "  $0                   # Run all tests"
    echo "  $0 -q                # Run quick baseline tests"
    echo "  $0 -c natural_speech_patterns  # Run only natural speech tests"
    echo "  $0 -m en_GB-alan-low          # Use different voice model"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -c|--category)
            CATEGORY="$2"
            shift 2
            ;;
        -l|--list)
            echo -e "${GREEN}Available test categories:${NC}"
            python3 -c "
import sys
sys.path.append('.')
from piper_tts_test_suite import TEST_SUITE
for cat, data in TEST_SUITE.items():
    print(f'  {cat}: {data[\"description\"]}')"
            exit 0
            ;;
        -q|--quick)
            CATEGORY="baseline_tests"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Check if Piper is installed
if ! command -v piper &> /dev/null; then
    echo -e "${RED}Error: Piper TTS is not installed or not in PATH${NC}"
    echo "Install from: https://github.com/OHF-Voice/piper1-gpl"
    exit 1
fi

# Check if Python script exists
if [ ! -f "piper_tts_test_suite.py" ]; then
    echo -e "${RED}Error: piper_tts_test_suite.py not found${NC}"
    echo "Make sure you're running this script from the piper-tts-tests directory"
    exit 1
fi

# Run the tests
echo -e "${GREEN}Starting Piper TTS Test Suite${NC}"
echo -e "Model: ${YELLOW}$MODEL${NC}"
echo -e "Output: ${YELLOW}$OUTPUT_DIR${NC}"

if [ -n "$CATEGORY" ]; then
    echo -e "Category: ${YELLOW}$CATEGORY${NC}"
    python3 -c "
import sys
sys.path.append('.')
from piper_tts_test_suite import run_test_suite, TEST_SUITE, generate_audio
from pathlib import Path
from datetime import datetime

# Filter test suite
if '$CATEGORY' not in TEST_SUITE:
    print(f'Error: Category {CATEGORY} not found')
    sys.exit(1)

filtered_suite = {'$CATEGORY': TEST_SUITE['$CATEGORY']}

# Run filtered tests
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
test_dir = Path('$OUTPUT_DIR') / f'piper_tests_{timestamp}'
test_dir.mkdir(parents=True, exist_ok=True)

print(f'Running category: $CATEGORY')
category_data = filtered_suite['$CATEGORY']
category_dir = test_dir / '$CATEGORY'
category_dir.mkdir(exist_ok=True)

for test in category_data['tests']:
    print(f\"Testing: {test['name']}\")
    output_file = category_dir / f\"{test['id']}_{test['name'].replace(' ', '_')}.wav\"
    generate_audio(test['text'], str(output_file), '$MODEL', **test['params'])

print(f'\\nTests complete! Output in: {test_dir}')
"
else
    # Run full test suite
    python3 piper_tts_test_suite.py
fi

echo -e "${GREEN}Test suite completed!${NC}"