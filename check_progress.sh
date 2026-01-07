#!/bin/bash
# Monitor data generation progress

while true; do
  count=$(ls data/*.jsonl 2>/dev/null | wc -l)
  echo "Completed batches: $count / 40"

  if [ "$count" -eq 40 ]; then
    echo "All batches complete!"
    break
  fi

  sleep 5
done
