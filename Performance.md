# Dense vectors performance information

### Tests Indices

| Index Name | Number of Documents | Index Size |
| :-: |:-: |:-: |
| dug1         | 6071                | 86.9 mb    |
| dug3         | 30355               | 437.8 mb   |
| dug10        | 60710               | 876.3 mb   |
| dug10-shard4 | 60710               | 876.3 mb   |
| dug100       | 607100              | 8.5 gb      |

### Query results
Query used is http://localhost:5000/query?query=blood%20sugar. All times in seconds. Test machine: Mac Mini, 3.2 GHz 6-Core Intel Core i7, 64 GB 2667 MHz DDR4

| Index Name | Try 1  | Try 2 | Try 3 | Try 4 | Try 5
| :-: |:-: |:-: | :-: |:-: |:-: |
| dug1         | .094 | .032 | .027 | .028 | .027 |
| dug3         | .357 | .112 | .105 | .100 | .108 |
| dug10        | .873 | .202 | .218 | .200 | .208 |
| dug10-shard4 | .341 | .075 | .076 | .069 | .070 |
| dug100       | 9.25 | 1.85 | 1.82 | 1.77 | 1.78 |
