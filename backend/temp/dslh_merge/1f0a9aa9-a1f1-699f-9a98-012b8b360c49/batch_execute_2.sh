#!/bin/bash

echo "Executing shs_2/local_merge_1.sh..."
bash shs_2/local_merge_1.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_2/local_merge_1.sh"
  exit 1
fi
echo "shs_2/local_merge_1.sh executed successfully!"

echo "Executing shs_2/local_merge_2.sh..."
bash shs_2/local_merge_2.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_2/local_merge_2.sh"
  exit 1
fi
echo "shs_2/local_merge_2.sh executed successfully!"

echo "Executing shs_2/local_merge_3.sh..."
bash shs_2/local_merge_3.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_2/local_merge_3.sh"
  exit 1
fi
echo "shs_2/local_merge_3.sh executed successfully!"

if [ -f "shs_2/local_merge_single_4.sh" ]; then
  echo "Executing shs_2/local_merge_single_4.sh..."
  bash shs_2/local_merge_single_4.sh
  if [ $? -ne 0 ]; then
    echo "Error occurred while executing shs_2/local_merge_single_4.sh"
    exit 1
  fi
  echo "shs_2/local_merge_single_4.sh executed successfully!"
else
  echo "shs_2/local_merge_single_4.sh not found, skipping..."
fi

echo "All scripts executed successfully!"