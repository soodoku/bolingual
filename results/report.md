# Hindi-English sound matching experiment

Benchmark size: **2959** items
Dev/Test split: **2219 / 740**
Unique English candidate words: **2673**
Experiment config: top_k=200, alpha=0.5, schwa_cost=0.3

## Test metrics

| method | top1 | top5 | top10 | mrr |
|---|---:|---:|---:|---:|
| Orthographic | 0.531 | 0.701 | 0.743 | 0.609 |
| Phonetic top-200 | 0.619 | 0.791 | 0.823 | 0.694 |
| Hybrid top-200 | 0.703 | 0.820 | 0.842 | 0.757 |

## Hard subset

Hard subset size: **639**
| method | top1 | top5 | top10 | mrr |
|---|---:|---:|---:|---:|
| Orthographic | 0.468 | 0.654 | 0.703 | 0.552 |
| Phonetic top-200 | 0.595 | 0.767 | 0.800 | 0.669 |
| Hybrid top-200 | 0.667 | 0.793 | 0.818 | 0.725 |

## Example improvements

- **सर्किट्स** → gold `circuits`; orth rank 164, hybrid rank 1; hybrid top5: circuits|scotts|socrates|markets|scout
- **कैम** → gold `came`; orth rank 126, hybrid rank 1; hybrid top5: came|claim|kamal|coman|champa
- **न्यू** → gold `new`; orth rank 122, hybrid rank 1; hybrid top5: new|no|nil|nick|neel
- **थैचर** → gold `thatcher`; orth rank 116, hybrid rank 1; hybrid top5: thatcher|theatre|tara|thayer|tower
- **डेटन** → gold `dayton`; orth rank 104, hybrid rank 1; hybrid top5: dayton|dana|dain|date|debt
- **केप** → gold `cape`; orth rank 94, hybrid rank 1; hybrid top5: cape|keep|cup|kelp|ke
- **गेट** → gold `gate`; orth rank 90, hybrid rank 1; hybrid top5: gate|greta|great|gai|leta
- **फेम** → gold `fame`; orth rank 74, hybrid rank 1; hybrid top5: fame|fermi|pharma|faith|fait
- **सक्सेशन** → gold `succession`; orth rank 67, hybrid rank 1; hybrid top5: succession|success|sagan|sachin|samsung
- **डोर** → gold `door`; orth rank 43, hybrid rank 1; hybrid top5: door|doren|dear|dorcas|kora