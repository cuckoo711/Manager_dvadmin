#!/bin/bash

echo "Executing shs_4/local_merge_1.sh..."
bash shs_4/local_merge_1.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_4/local_merge_1.sh"
  exit 1
fi
echo "shs_4/local_merge_1.sh executed successfully!"

if [ -f "shs_4/local_merge_single_2.sh" ]; then
  echo "Executing shs_4/local_merge_single_2.sh..."
  bash shs_4/local_merge_single_2.sh
  if [ $? -ne 0 ]; then
    echo "Error occurred while executing shs_4/local_merge_single_2.sh"
    exit 1
  fi
  echo "shs_4/local_merge_single_2.sh executed successfully!"
else
  echo "shs_4/local_merge_single_2.sh not found, skipping..."
fi

echo "All scripts executed successfully!"