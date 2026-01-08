#!/bin/bash

echo "Executing shs_5/local_merge_1.sh..."
bash shs_5/local_merge_1.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_5/local_merge_1.sh"
  exit 1
fi
echo "shs_5/local_merge_1.sh executed successfully!"

if [ -f "shs_5/local_merge_single_2.sh" ]; then
  echo "Executing shs_5/local_merge_single_2.sh..."
  bash shs_5/local_merge_single_2.sh
  if [ $? -ne 0 ]; then
    echo "Error occurred while executing shs_5/local_merge_single_2.sh"
    exit 1
  fi
  echo "shs_5/local_merge_single_2.sh executed successfully!"
else
  echo "shs_5/local_merge_single_2.sh not found, skipping..."
fi

echo "All scripts executed successfully!"