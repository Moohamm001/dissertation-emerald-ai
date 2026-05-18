# EDA Report — 2019 All Funded Green Loan dataset

_Companion to `datasheet.md` and `feature_catalogue.yaml`. Operates on the 90 permitted features after the proposal §5.3 leakage audit; rows with missing labels (113 of 14,135) are excluded._

Version: 0.1 · Generated: 2026-05-18


## 1. Univariate distributions

Numeric columns report mean / std / skewness / kurtosis and the 1/25/50/75/99 percentile spine. Categorical columns report the top level, its frequency, and Shannon entropy of the value distribution (a high-entropy categorical is more informative than a degenerate one)._

_36 numeric features, 54 categorical features._


### 1.1 Numeric features (top 20 by absolute skewness)

| feature | miss% | mean | std | skew | kurt | p01 | p50 | p99 |
|---|---|---|---|---|---|---|---|---|
| Amount Sought | 0.3 | 184552.943 | 8730190.512 | 109.203 | 12361.409 | 4999.000 | 50000.000 | 500000.000 |
| Average Monthly Sales | 0.0 | 95400.896 | 898450.506 | 99.259 | 10925.935 | 0.000 | 38348.597 | 723646.664 |
| Factor | 41.6 | 1.620 | 11.911 | 80.387 | 6902.299 | 1.070 | 1.380 | 1.500 |
| Payment Amount | 37.4 | 995.991 | 8801.929 | 69.201 | 5249.124 | 0.000 | 350.000 | 6347.000 |
| Payback | 0.1 | 49413.241 | 131663.698 | 64.883 | 6008.943 | 0.000 | 26250.000 | 306272.901 |
| Marketing Avg Monthly Sales | 2.1 | 85970.601 | 204400.492 | 34.326 | 1620.977 | 0.000 | 39999.000 | 400000.000 |
| Marketing Time in Business | 2.1 | 60.815 | 100.503 | 29.651 | 1892.283 | 0.000 | 59.000 | 402.740 |
| Mktg Has Ownership | 0.0 | 0.997 | 0.055 | -17.977 | 321.211 | 1.000 | 1.000 | 1.000 |
| Amount Funded | 0.0 | 43326.628 | 73015.897 | 16.416 | 551.710 | 500.000 | 25000.000 | 250000.000 |
| # Borrower Renewals | 0.0 | 0.774 | 2.473 | 10.271 | 157.410 | 0.000 | 0.000 | 9.000 |
| Max Offer Received $ | 0.0 | 60932.086 | 92039.275 | 9.815 | 230.320 | 1500.000 | 33222.500 | 375000.000 |
| Closed Max Term | 0.0 | 12.943 | 14.647 | 6.802 | 62.676 | 4.000 | 12.000 | 120.000 |
| # Offers Received | 0.0 | 4.352 | 5.100 | 6.443 | 106.782 | 1.000 | 3.000 | 25.000 |
| Time In Business | 0.2 | 70.727 | 83.962 | 5.465 | 57.419 | 5.000 | 60.000 | 430.140 |
| Points | 0.0 | 6.221 | 3.910 | 4.790 | 103.343 | 0.200 | 5.000 | 12.000 |
| Days Since Last Opportunity | 0.0 | 65.100 | 146.333 | 4.696 | 30.079 | 0.000 | 0.000 | 789.580 |
| Revenue | 0.0 | 2404.801 | 3326.071 | 3.890 | 24.139 | 30.000 | 1342.500 | 16499.328 |
| Commission | 0.0 | 2296.608 | 3317.947 | 3.864 | 23.829 | 25.000 | 1200.000 | 16200.000 |
| Current Tier | 0.0 | 1.425 | 0.777 | 2.509 | 7.535 | 1.000 | 1.000 | 5.000 |
| Tier | 0.0 | 1.426 | 0.778 | 2.507 | 7.525 | 1.000 | 1.000 | 5.000 |


### 1.2 Categorical features (top 20 by entropy)

| feature | miss% | n_unique | top_value | top_freq% | entropy_bits |
|---|---|---|---|---|---|
| App Sent TS | 0.0 | 13480 | 2019-05-28 16:51:00 | 0.0 | 13.697 |
| Offer Received TS | 0.7 | 13312 | 2019-11-26 17:42:00 | 0.0 | 13.675 |
| Contacted TS | 17.6 | 11208 | 2019-11-12 19:26:00 | 0.0 | 13.435 |
| Borrower Created | 0.0 | 11636 | 2017-05-26 03:32:00 | 0.1 | 13.401 |
| Created | 0.0 | 11636 | 2017-05-26 03:32:00 | 0.1 | 13.401 |
| Offer Accepted TS | 0.0 | 12132 | 2019-12-31 18:38:00 | 0.1 | 13.389 |
| End TS | 0.0 | 12023 | 2019-12-31 18:38:00 | 0.1 | 13.362 |
| DocPrep TS | 21.8 | 10545 | 2017-11-09 20:26:00 | 0.0 | 13.343 |
| Current Assigned TS | 7.9 | 11235 | 2019-06-03 19:15:00 | 0.2 | 13.338 |
| Processor Assigned TS | 21.9 | 10217 | 2019-05-09 16:30:00 | 0.1 | 13.278 |
| Attempted TS | 11.8 | 10834 | 2019-07-31 14:01:00 | 0.1 | 13.259 |
| Start TS | 0.0 | 11931 | 2018-12-26 22:36:00 | 0.2 | 13.230 |
| Opportunity Start | 0.0 | 11931 | 2018-12-26 22:36:00 | 0.2 | 13.230 |
| Online App Complete TS | 14.4 | 9893 | 2017-05-26 03:47:00 | 0.1 | 13.164 |
| Contract Out TS | 0.0 | 11592 | 2019-09-30 05:59:00 | 0.2 | 13.140 |
| Contract Signed TS | 0.0 | 11605 | 2019-05-31 05:59:00 | 0.3 | 13.130 |
| Assigned TS | 1.9 | 11078 | 2018-12-26 22:36:00 | 0.2 | 13.130 |
| Deal Closed TS | 0.0 | 11534 | 2019-05-31 06:00:00 | 0.3 | 13.115 |
| Borrower City | 0.9 | 4367 | Houston | 1.2 | 11.009 |
| Shared w/ Funding Desk | 21.8 | 794 | 1970-01-01 09:46:00 | 0.3 | 9.279 |


## 2. Bivariate association with Y

_Mutual information is reported in nats; Pearson / Spearman are defined for numeric features only. Sorted by MI to surface the highest-signal features regardless of monotonicity._

| feature | dtype | Pearson(Y) | Spearman(Y) | MI(Y) [nats] |
|---|---|---|---|---|
| Contract Signed TS | datetime64[ns] | — | — | 0.0237 |
| End TS | datetime64[ns] | — | — | 0.0236 |
| Deal Closed TS | datetime64[ns] | — | — | 0.0236 |
| DocPrep TS | datetime64[ns] | — | — | 0.0236 |
| Offer Received TS | datetime64[ns] | — | — | 0.0235 |
| App Sent TS | datetime64[ns] | — | — | 0.0233 |
| Contract Out TS | datetime64[ns] | — | — | 0.0232 |
| Processor Assigned TS | datetime64[ns] | — | — | 0.0232 |
| Offer Accepted TS | datetime64[ns] | — | — | 0.0229 |
| Attempted TS | datetime64[ns] | — | — | 0.0229 |
| Opportunity Start | datetime64[ns] | — | — | 0.0229 |
| Start TS | datetime64[ns] | — | — | 0.0229 |
| Contacted TS | datetime64[ns] | — | — | 0.0228 |
| Created | datetime64[ns] | — | — | 0.0228 |
| Borrower Created | datetime64[ns] | — | — | 0.0228 |
| Current Assigned TS | datetime64[ns] | — | — | 0.0221 |
| Assigned TS | datetime64[ns] | — | — | 0.0220 |
| Online App Complete TS | datetime64[ns] | — | — | 0.0214 |
| Borrower City | object | — | — | 0.0154 |
| Shared w/ Funding Desk | datetime64[ns] | — | — | 0.0103 |
| Lender | object | — | — | 0.0079 |
| Current Assigned | datetime64[ns] | — | — | 0.0078 |
| Attempted | datetime64[ns] | — | — | 0.0077 |
| DocPrep | datetime64[ns] | — | — | 0.0077 |
| Contacted | datetime64[ns] | — | — | 0.0075 |


## 3. Conditional delinquent rates by segment

_Y=0 = delinquent (default ∪ behind). Wilson 95% CIs widen sharply on segments with few observations — these are flagged. The underlying base rate is 0.36% (50 of 14,022)._


### 3.1 By `Industry`

| segment | n | delinquent | rate % | 95% CI % | flag |
|---|---|---|---|---|---|
| firearms | 11 | 1 | 9.09 | [1.62, 37.74] | small-N |
| manufacturing | 446 | 6 | 1.35 | [0.62, 2.90] |  |
| legalServices | 154 | 1 | 0.65 | [0.11, 3.59] |  |
| transportation | 510 | 3 | 0.59 | [0.20, 1.72] |  |
| freightTrucking | 542 | 3 | 0.55 | [0.19, 1.61] |  |
| informationMedia | 577 | 3 | 0.52 | [0.18, 1.52] |  |
| realEstate | 455 | 2 | 0.44 | [0.12, 1.59] |  |
| restaurants | 1832 | 8 | 0.44 | [0.22, 0.86] |  |
| construction | 2096 | 9 | 0.43 | [0.23, 0.81] |  |
| education | 250 | 1 | 0.40 | [0.07, 2.23] |  |
| other | 2901 | 8 | 0.28 | [0.14, 0.54] |  |
| automotive | 366 | 1 | 0.27 | [0.05, 1.53] |  |
| finance | 367 | 1 | 0.27 | [0.05, 1.53] |  |
| healthcare | 953 | 2 | 0.21 | [0.06, 0.76] |  |
| retail | 1328 | 1 | 0.08 | [0.01, 0.43] |  |


### 3.2 By `Borrower State`

| segment | n | delinquent | rate % | 95% CI % | flag |
|---|---|---|---|---|---|
| WV | 48 | 1 | 2.08 | [0.37, 10.90] |  |
| AR | 97 | 2 | 2.06 | [0.57, 7.21] |  |
| CT | 172 | 3 | 1.74 | [0.59, 5.00] |  |
| IN | 197 | 3 | 1.52 | [0.52, 4.38] |  |
| SC | 210 | 3 | 1.43 | [0.49, 4.12] |  |
| MS | 92 | 1 | 1.09 | [0.19, 5.90] |  |
| NC | 463 | 5 | 1.08 | [0.46, 2.50] |  |
| CO | 337 | 3 | 0.89 | [0.30, 2.58] |  |
| KS | 119 | 1 | 0.84 | [0.15, 4.61] |  |
| MO | 245 | 2 | 0.82 | [0.22, 2.93] |  |
| AL | 154 | 1 | 0.65 | [0.11, 3.59] |  |
| IL | 464 | 3 | 0.65 | [0.22, 1.88] |  |
| MN | 169 | 1 | 0.59 | [0.10, 3.28] |  |
| MI | 340 | 2 | 0.59 | [0.16, 2.12] |  |
| AZ | 399 | 2 | 0.50 | [0.14, 1.81] |  |


## 4. Distribution-shift diagnostics (quarterly PSI)

_PSI per feature, computed against Q1 2019 as the reference. Conventional thresholds: <0.10 stable; 0.10–0.25 moderate shift; ≥0.25 material._

| feature | period | psi_vs_Q1 | n_ref | n_cur |
|---|---|---|---|---|
| Start Month | Q2 | 15.991 | 3406 | 3232 |
| Start Month | Q3 | 15.965 | 3406 | 3678 |
| Start Month | Q4 | 15.721 | 3406 | 3706 |
| Lender Identifier | Q2 | 14.397 | 3406 | 3232 |
| Lender Identifier | Q3 | 13.838 | 3406 | 3678 |
| Published | Q3 | 11.932 | 3406 | 3678 |
| Lender Identifier | Q4 | 10.776 | 3406 | 3706 |
| Published | Q4 | 10.767 | 3406 | 3706 |
| Published | Q2 | 10.651 | 3406 | 3232 |
| Attempted | Q3 | 9.335 | 3406 | 3678 |
| Attempted | Q4 | 9.250 | 3406 | 3706 |
| Assigned | Q4 | 9.182 | 3406 | 3706 |
| Assigned | Q3 | 8.940 | 3406 | 3678 |
| Attempted | Q2 | 8.700 | 3406 | 3232 |
| Assigned | Q2 | 8.523 | 3406 | 3232 |
| Contacted | Q3 | 8.473 | 3406 | 3678 |
| Start Annual Day | Q2 | 8.171 | 3406 | 3232 |
| Start Annual Day | Q4 | 8.171 | 3406 | 3706 |
| Start Annual Day | Q3 | 8.171 | 3406 | 3678 |
| DocPrep | Q3 | 8.036 | 3406 | 3678 |
