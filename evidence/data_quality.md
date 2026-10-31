# Data-quality review

| Item | Observed | Treatment / implication |
|---|---:|---|
| Training export rows | 12,029 | Supplied training CSV |
| Explicit undecided labels | 215 | Excluded from supervised fitting |
| Unique labelled rows after de-duplication | 11,146 | One row per `claim_id`, first timestamp retained |
| Labelled fraud outcomes after de-duplication | 141 | Rare positive class (about 1.27%) |
| Labelled non-fraud outcomes after de-duplication | 11,005 | Includes possible unresolved Zoho rows mis-exported as 0 |
| Repeated labelled rows removed | 668 | Email confirms repeated claim IDs can be resubmissions |
| Test rows | 2,252 | One score emitted per row |
| Partner reference rows | 380 | All claim partner IDs matched |
| Product reference rows | 21 | All claim SKUs matched |

## Material caveats
- Email-thread warning: legacy Zoho could not store blank outcomes; unresolved cases may have migrated as `0`. There is no reliable flag in this pack to recover them.
- The explicit 215 blank outcomes are CRM rows; all explicit blanks were excluded.
- Submitted timestamps are treated as IST. The operations policy's UTC migration caveat concerns resolution events.
- Serial numbers are partner-entered and inconsistently formatted; normalization and simple format checks are used, but no ground-truth serial registry was supplied.
- Kestrel Shield enrollment/coverage is not a field in the supplied claim/product/partner exports.
