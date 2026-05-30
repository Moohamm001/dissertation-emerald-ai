# Explainability Report — proposal §5.11

Version: 0.2 · Generated: 2026-05-30

## Global feature attribution — mean(|SHAP|)

Exact TreeSHAP on the persisted model; signed column shows net direction.

| Feature | mean(\|SHAP\|) | mean signed SHAP |
|---|---|---|
| `Lender` | 0.4900 | +0.0036 |
| `Prod Rank` | 0.2855 | -0.0032 |
| `Points` | 0.2090 | +0.0040 |
| `Max Offer Received $` | 0.1732 | -0.0119 |
| `Payback` | 0.1681 | -0.0078 |
| `Prod Type` | 0.1651 | -0.0007 |
| `Product` | 0.1309 | -0.0131 |
| `Revenue` | 0.1288 | +0.0120 |
| `Borrower State` | 0.1284 | -0.0065 |
| `Marketing Mineral Group_4. Silver` | 0.1255 | +0.0030 |
| `Commission` | 0.1244 | +0.0047 |
| `Amount Sought` | 0.1170 | -0.0181 |
| `Average Monthly Sales` | 0.1157 | -0.0089 |
| `Borrower Zip` | 0.1072 | -0.0045 |
| `Credit Score` | 0.1010 | -0.0118 |
| `Payment Amount` | 0.1010 | -0.0020 |
| `Is Product Renewal` | 0.0818 | -0.0088 |
| `Closed Max Term` | 0.0741 | +0.0143 |
| `Amount Funded` | 0.0737 | +0.0148 |
| `# Borrower Renewals` | 0.0687 | +0.0006 |
| `Start Quarter Day` | 0.0665 | -0.0052 |
| `Time In Business` | 0.0568 | -0.0073 |
| `Marketing Credit Score` | 0.0568 | +0.0081 |
| `Industry` | 0.0561 | +0.0006 |
| `Loan Purpose` | 0.0440 | -0.0003 |

## Explanation fidelity

Faithfulness correlation (Bhatt et al., 2020) on 200 instances: **0.649** (∈[-1,1]; higher means SHAP attribution mass tracks the model's actual prediction drops under feature ablation).

