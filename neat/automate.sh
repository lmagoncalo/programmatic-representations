#!/bin/bash
for i in {1..10}
do
  echo "Iteration: $i"
  python evolve.py $i 500 "sunset, bright colors"
done

for i in {1..10}
do
  echo "Iteration: $i"
  python evolve.py $i 500 "hot air balloon"
done

for i in {1..10}
do
  echo "Iteration: $i"
  python evolve.py $i 500 "smily"
done
