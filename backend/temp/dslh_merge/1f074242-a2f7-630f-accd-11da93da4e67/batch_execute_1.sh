#!/bin/bash

echo "Executing shs_1/local_merge_1.sh..."
bash shs_1/local_merge_1.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_1/local_merge_1.sh"
  exit 1
fi
echo "shs_1/local_merge_1.sh executed successfully!"

echo "Executing shs_1/local_merge_2.sh..."
bash shs_1/local_merge_2.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_1/local_merge_2.sh"
  exit 1
fi
echo "shs_1/local_merge_2.sh executed successfully!"

echo "Executing shs_1/local_merge_3.sh..."
bash shs_1/local_merge_3.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_1/local_merge_3.sh"
  exit 1
fi
echo "shs_1/local_merge_3.sh executed successfully!"

echo "Executing shs_1/local_merge_4.sh..."
bash shs_1/local_merge_4.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_1/local_merge_4.sh"
  exit 1
fi
echo "shs_1/local_merge_4.sh executed successfully!"

echo "Executing shs_1/local_merge_5.sh..."
bash shs_1/local_merge_5.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_1/local_merge_5.sh"
  exit 1
fi
echo "shs_1/local_merge_5.sh executed successfully!"

echo "Executing shs_1/local_merge_6.sh..."
bash shs_1/local_merge_6.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing shs_1/local_merge_6.sh"
  exit 1
fi
echo "shs_1/local_merge_6.sh executed successfully!"

if [ -f "shs_1/local_merge_single_7.sh" ]; then
  echo "Executing shs_1/local_merge_single_7.sh..."
  bash shs_1/local_merge_single_7.sh
  if [ $? -ne 0 ]; then
    echo "Error occurred while executing shs_1/local_merge_single_7.sh"
    exit 1
  fi
  echo "shs_1/local_merge_single_7.sh executed successfully!"
else
  echo "shs_1/local_merge_single_7.sh not found, skipping..."
fi

echo "All scripts executed successfully!"