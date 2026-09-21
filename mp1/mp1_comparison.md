# MP1 Strategy Evaluation Comparison

## Summary by Strategy

| Strategy | Accuracy (mean of 3) | Parse Rate | Judge Score (1-4) | Total Cost ($) | Latency p50 (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **cot** | 3.00 / 3 | 100% | 3.80 / 4 | $0.000652 | 2.24s |
| **few_shot** | 2.90 / 3 | 100% | 3.70 / 4 | $0.000403 | 1.82s |
| **structured** | 3.00 / 3 | 100% | 3.90 / 4 | $0.000436 | 1.86s |
| **zero_shot** | 3.00 / 3 | 100% | 3.50 / 4 | $0.000340 | 1.99s |

## Detailed Per-Snippet Execution Log (40 Runs)

| # | Strategy | Snippet ID | Accuracy (/ 3) | Parse Success | Judge Score (1-4) | Cost ($) | Latency (s) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | zero_shot | j01 | 3 | True | 3 | $0.000033 | 2.72s |
| 1 | zero_shot | j02 | 3 | True | 3 | $0.000032 | 1.97s |
| 2 | zero_shot | j03 | 3 | True | 4 | $0.000034 | 2.04s |
| 3 | zero_shot | j04 | 3 | True | 4 | $0.000034 | 2.12s |
| 4 | zero_shot | j05 | 3 | True | 4 | $0.000033 | 1.80s |
| 5 | zero_shot | j06 | 3 | True | 3 | $0.000035 | 1.92s |
| 6 | zero_shot | j07 | 3 | True | 3 | $0.000033 | 2.04s |
| 7 | zero_shot | j08 | 3 | True | 4 | $0.000035 | 1.95s |
| 8 | zero_shot | j09 | 3 | True | 3 | $0.000034 | 2.01s |
| 9 | zero_shot | j10 | 3 | True | 4 | $0.000037 | 1.96s |
| 10 | few_shot | j01 | 3 | True | 4 | $0.000039 | 1.86s |
| 11 | few_shot | j02 | 3 | True | 3 | $0.000039 | 1.96s |
| 12 | few_shot | j03 | 3 | True | 4 | $0.000041 | 1.87s |
| 13 | few_shot | j04 | 3 | True | 4 | $0.000040 | 1.83s |
| 14 | few_shot | j05 | 3 | True | 3 | $0.000039 | 1.80s |
| 15 | few_shot | j06 | 3 | True | 4 | $0.000041 | 1.74s |
| 16 | few_shot | j07 | 3 | True | 4 | $0.000039 | 1.78s |
| 17 | few_shot | j08 | 3 | True | 4 | $0.000042 | 1.82s |
| 18 | few_shot | j09 | 2 | True | 3 | $0.000040 | 1.75s |
| 19 | few_shot | j10 | 3 | True | 4 | $0.000042 | 1.81s |
| 20 | structured | j01 | 3 | True | 4 | $0.000043 | 1.92s |
| 21 | structured | j02 | 3 | True | 3 | $0.000042 | 1.90s |
| 22 | structured | j03 | 3 | True | 4 | $0.000044 | 1.83s |
| 23 | structured | j04 | 3 | True | 4 | $0.000044 | 1.90s |
| 24 | structured | j05 | 3 | True | 4 | $0.000043 | 1.95s |
| 25 | structured | j06 | 3 | True | 4 | $0.000044 | 1.84s |
| 26 | structured | j07 | 3 | True | 4 | $0.000043 | 1.84s |
| 27 | structured | j08 | 3 | True | 4 | $0.000045 | 1.88s |
| 28 | structured | j09 | 3 | True | 4 | $0.000043 | 1.81s |
| 29 | structured | j10 | 3 | True | 4 | $0.000045 | 1.77s |
| 30 | cot | j01 | 3 | True | 4 | $0.000060 | 2.13s |
| 31 | cot | j02 | 3 | True | 3 | $0.000059 | 2.15s |
| 32 | cot | j03 | 3 | True | 4 | $0.000062 | 2.26s |
| 33 | cot | j04 | 3 | True | 4 | $0.000061 | 2.05s |
| 34 | cot | j05 | 3 | True | 3 | $0.000070 | 2.23s |
| 35 | cot | j06 | 3 | True | 4 | $0.000076 | 2.30s |
| 36 | cot | j07 | 3 | True | 4 | $0.000060 | 2.25s |
| 37 | cot | j08 | 3 | True | 4 | $0.000065 | 2.36s |
| 38 | cot | j09 | 3 | True | 4 | $0.000071 | 2.46s |
| 39 | cot | j10 | 3 | True | 4 | $0.000069 | 2.05s |
