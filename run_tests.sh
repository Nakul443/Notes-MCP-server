#!/bin/bash

# --- CONFIGURATION ---
VENV_PATH="./venv/bin/activate"
TEST_DIR="./tests"
CHROMA_DB="./chroma_db"

echo "========================================"
echo "    🚀 NOTES-MCP-SERVER TEST RUNNER    "
echo "========================================"

# 1. Check for Virtual Environment
if [ ! -f "$VENV_PATH" ]; then
    echo "❌ Error: Virtual environment not found at $VENV_PATH"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 2. Check for Database (Critical for RAG tests)
if [ ! -d "$CHROMA_DB" ]; then
    echo "⚠️  Warning: chroma_db folder not found."
    echo "You should probably run 'python3 src/seeder.py' before testing."
    echo "----------------------------------------"
fi

# 3. Activate Environment
source "$VENV_PATH"
echo "✅ Virtual environment activated."

# 4. Define Tests (Using your specific filenames)
# test_rag.py: Sync/Performance benchmark
# test_fixed_search.py: Async logic validator
TEST_FILES=("test_rag.py" "test_fixed_search.py")

FAILED=0

# 5. Run Tests
for FILE in "${TEST_FILES[@]}"; do
    FULL_PATH="$TEST_DIR/$FILE"
    
    if [ -f "$FULL_PATH" ]; then
        echo -e "\n----------------------------------------"
        echo "🏃 Running: $FILE"
        echo "----------------------------------------"
        
        # We use python3 from the activated venv
        python3 "$FULL_PATH"
        
        if [ $? -eq 0 ]; then
            echo -e "\n✨ $FILE: PASSED"
        else
            echo -e "\n🔥 $FILE: FAILED"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "❌ Error: Test file not found: $FULL_PATH"
        FAILED=$((FAILED + 1))
    fi
done

# 6. Final Report
echo -e "\n========================================"
if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
else
    echo "❌ $FAILED TEST(S) FAILED. Check the output above for errors."
fi
echo "========================================"

exit $FAILED