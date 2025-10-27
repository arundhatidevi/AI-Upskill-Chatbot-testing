#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          RUNNING CHATBOT PERFORMANCE TESTS                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Run performance tests
echo "🧪 Running performance tests..."
pytest tests/test_performance.py -v --log-cli-level=INFO

# Generate performance report
echo ""
echo "📊 Generating performance report..."
python3 << EOF
from src.utils.performance import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.generate_report()
EOF

echo ""
echo "✅ Performance testing complete!"
echo "📄 Report saved to: performance_report.txt"









