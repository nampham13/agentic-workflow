#!/bin/bash

# Demo Script - Quick demonstration of the agentic pipeline

API_URL="http://localhost:8000"

echo "════════════════════════════════════════════════════════════"
echo "🧬 LIFE AI AGENTIC - LIVE DEMO"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check server
echo "🔍 Checking server..."
if ! curl -s ${API_URL}/health > /dev/null 2>&1; then
    echo "❌ Server not running. Starting server..."
    echo ""
    ./run.sh &
    SERVER_PID=$!
    echo "⏳ Waiting for server startup..."
    sleep 5
    
    if ! curl -s ${API_URL}/health > /dev/null 2>&1; then
        echo "❌ Failed to start server"
        exit 1
    fi
    echo "✅ Server started (PID: $SERVER_PID)"
else
    echo "✅ Server is running"
fi

echo ""
echo "────────────────────────────────────────────────────────────"
echo "DEMO: Generating drug-like molecules"
echo "────────────────────────────────────────────────────────────"
echo ""

# Create run
echo "📝 Creating pipeline run..."
echo "   • 2 rounds of generation"
echo "   • 15 candidates per round"
echo "   • Select top 3 molecules"
echo ""

RUN_RESPONSE=$(curl -s -X POST ${API_URL}/runs \
  -H "Content-Type: application/json" \
  -d '{
    "rounds": 2,
    "candidates_per_round": 15,
    "top_k": 3,
    "max_violations": 1,
    "scoring_penalty": 0.1
  }')

RUN_ID=$(echo "$RUN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['run_id'])" 2>/dev/null)

if [ -z "$RUN_ID" ]; then
    echo "❌ Failed to create run"
    exit 1
fi

echo "✅ Run created: $RUN_ID"
echo ""

# Monitor progress
echo "⚙️  Pipeline executing..."
echo ""

LAST_ROUND=""
MAX_WAIT=60  # 60 iterations = up to 2 minutes
for i in $(seq 1 $MAX_WAIT); do
    RESPONSE=$(curl -s ${API_URL}/runs/${RUN_ID}/status 2>/dev/null)
    
    if [ -z "$RESPONSE" ]; then
        echo "⚠️  No response from server"
        sleep 2
        continue
    fi
    
    STATUS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")
    CURRENT_ROUND=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('current_round', 0))" 2>/dev/null || echo "0")
    PROGRESS_MSG=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('progress_message', ''))" 2>/dev/null || echo "")
    
    if [ "$CURRENT_ROUND" != "$LAST_ROUND" ] && [ "$CURRENT_ROUND" != "0" ]; then
        echo "   Round $CURRENT_ROUND/2: $PROGRESS_MSG"
        LAST_ROUND="$CURRENT_ROUND"
    fi
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "✅ Pipeline completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo "❌ Pipeline failed!"
        exit 1
    fi
    
    sleep 2
    
    if [ $i -eq $MAX_WAIT ]; then
        echo ""
        echo "⚠️  Timeout waiting for completion (status: $STATUS)"
        echo "    You can check results later with: curl ${API_URL}/runs/${RUN_ID}/results"
        exit 0
    fi
done

echo ""
echo "────────────────────────────────────────────────────────────"
echo "RESULTS"
echo "────────────────────────────────────────────────────────────"
echo ""

# Get results
echo "📊 Fetching results..."

RESULTS=$(curl -s ${API_URL}/runs/${RUN_ID}/results)

if [ -z "$RESULTS" ] || [ "$RESULTS" = "null" ]; then
    echo "⚠️  No results returned"
    exit 0
fi

# Save to temp file and process
echo "$RESULTS" > /tmp/demo_results.json

python3 << 'EOF'
import sys, json

try:
    # Read from file
    with open('/tmp/demo_results.json', 'r') as f:
        raw = f.read().strip()
    
    if not raw:
        print("⚠️  Empty response from server")
        sys.exit(0)
    
    data = json.loads(raw)
    
    if 'error' in data or 'detail' in data:
        print(f"⚠️  Error: {data.get('error') or data.get('detail')}")
        sys.exit(0)
    
    print(f"📊 Generated {data.get('total_molecules', 0)} molecules")
    
    top_mols = data.get('top_molecules', [])
    if not top_mols:
        print("⚠️  No top molecules found")
        sys.exit(0)
        
    print(f"🏆 Top {len(top_mols)} selected:\n")
    
    for i, mol in enumerate(top_mols, 1):
        print(f"  {i}. SMILES: {mol['smiles']}")
        print(f"     Score:  {mol['score']:.4f}")
        print(f"     QED:    {mol['properties']['qed']:.3f}")
        print(f"     MW:     {mol['properties']['mw']:.1f}")
        print(f"     LogP:   {mol['properties']['logp']:.2f}")
        print(f"     Rules:  {mol['screening_result']['violations']} violations")
        print()
        
except json.JSONDecodeError as e:
    print(f"⚠️  Invalid JSON response: {e}")
    print(f"Raw response: {raw[:200] if 'raw' in locals() else 'N/A'}")
except KeyError as e:
    print(f"⚠️  Unexpected response format: missing {e}")
except Exception as e:
    print(f"⚠️  Error processing results: {e}")
EOF

# Get trace summary
TRACE=$(curl -s ${API_URL}/runs/${RUN_ID}/trace)
EVENT_COUNT=$(echo "$TRACE" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_events'])" 2>/dev/null || echo "0")

echo "────────────────────────────────────────────────────────────"
echo ""
echo "✨ Demo completed successfully!"
echo ""
echo "📈 Agent trace: $EVENT_COUNT events logged"
echo "🔬 View details: curl ${API_URL}/runs/${RUN_ID}/trace"
echo "📚 API docs: http://localhost:8000/docs"
echo ""
echo "════════════════════════════════════════════════════════════"
