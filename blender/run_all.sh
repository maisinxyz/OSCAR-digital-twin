#!/bin/bash
cd /home/claude/bl; rm -rf out; mkdir -p out
R="--rx 1600 --ry 900 --s 56"; Q="--rx 1300 --ry 740 --s 56"
for c in 0 -4 4; do python3 oscar.py --view hero --cart $c $R --out out/hero_$c.png > out/log_hero_$c.txt 2>&1; done
python3 oscar.py --view cart --cart 0 $Q --out out/cart_0.png > out/log_cart.txt 2>&1
python3 oscar.py --view right --cart 0 $Q --out out/right_0.png > out/log_right.txt 2>&1
python3 oscar.py --view motor --cart 0 $Q --out out/motor_0.png > out/log_motor.txt 2>&1
echo CORE > out/core.txt
for c in -2 2; do python3 oscar.py --view hero --cart $c $R --out out/hero_$c.png > out/log_hero_$c.txt 2>&1; done
echo ALLDONE > out/done.txt
