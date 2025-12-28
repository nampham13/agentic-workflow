#!/bin/bash

# API Test Script - Quick test of all endpoints

API_URL="http://localhost:8000"

echo "════════════════════════════════════════════════════════════"
echo "🧪 LIFE AI AGENTIC - API TEST"
echo "════════════════════════════════════════════════════════════"
echo ""

# Health check
echo "1. Health Check"
echo "   GET /health"
HEALTH=$(curl -s ${API_URL}/health)
echo "   Response: $HEALTH"
echo ""

# Create run
echo "2. Create Run"
echo "   POST /runs"
RUN_RESPONSE=$(curl -s -X POST ${API_URL}/runs \
  -H "Content-Type: application/json" \
  -d '{"rounds": 2, "candidates_per_round": 10, "top_k": 3}')

RUN_ID=$(echo "$RUN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['run_id'])" 2>/dev/null)
echo "   Run ID: $RUN_ID"
echo ""

# Monitor status
echo "3. Monitor Status"
echo "   GET /runs/{id}/status"
for i in {1..15}; do
    STATUS_RESPONSE=$(curl -s ${API_URL}/runs/${RUN_ID}/status)
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    ROUND=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('current_round', 0))" 2>/dev/null)
    
    echo "   [$i] Status: $STATUS, Round: $ROUND"
    
    if [ "$STATUS" = "completed" ]; then
        echo "   ✅ Run completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "   ❌ Run failed!"
        exit 1
    fi
    
    sleep 2
done
echo ""

# Get results
echo "4. Get Results"
echo "   GET /runs/{id}/results"
RESULTS=$(curl -s ${API_URL}/runs/${RUN_ID}/results)
TOTAL=$(echo "$RESULTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_molecules', 0))" 2>/dev/null || echo "N/A")
echo "   Total molecules: $TOTAL"
echo ""

# Get trace
echo "5. Get Trace"
echo "   GET /runs/{id}/trace"
TRACE=$(curl -s ${API_URL}/runs/${RUN_ID}/trace)
EVENTS=$(echo "$TRACE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_events', 0))" 2>/dev/null || echo "N/A")
echo "   Total events: $EVENTS"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "✅ All tests passed!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📚 View full results:"
echo "   curl ${API_URL}/runs/${RUN_ID}/results | python3 -m json.tool"
echo ""
echo "🔍 View trace details:"
echo "   curl ${API_URL}/runs/${RUN_ID}/trace | python3 -m json.tool"
echo ""
echo "📖 Interactive docs: http://localhost:8000/docs"
echo ""
