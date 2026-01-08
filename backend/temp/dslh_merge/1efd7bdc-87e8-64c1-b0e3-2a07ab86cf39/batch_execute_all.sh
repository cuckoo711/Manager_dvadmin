#!/bin/bash

echo "Executing ./batch_execute_1.sh..."
bash ./batch_execute_1.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing ./batch_execute_1.sh"
  exit 1
fi
echo "./batch_execute_1.sh executed successfully!"

echo "Executing ./batch_execute_2.sh..."
bash ./batch_execute_2.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing ./batch_execute_2.sh"
  exit 1
fi
echo "./batch_execute_2.sh executed successfully!"

echo "Executing ./batch_execute_3.sh..."
bash ./batch_execute_3.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing ./batch_execute_3.sh"
  exit 1
fi
echo "./batch_execute_3.sh executed successfully!"

echo "Executing ./batch_execute_4.sh..."
bash ./batch_execute_4.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing ./batch_execute_4.sh"
  exit 1
fi
echo "./batch_execute_4.sh executed successfully!"

echo "Executing ./batch_execute_5.sh..."
bash ./batch_execute_5.sh
if [ $? -ne 0 ]; then
  echo "Error occurred while executing ./batch_execute_5.sh"
  exit 1
fi
echo "./batch_execute_5.sh executed successfully!"
