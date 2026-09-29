# LinkedIn draft — Post 4: Transform + tests

**Hook:** I don’t trust a mart until transforms have tests the way backend services do.

**Body:**
- Quality rules in YAML + executable checks (quantities, required columns).
- Polars transforms: line revenue, category coalesce from supplement.
- pytest on silver outputs—CI on every push.

**CTA:** Link to `tests/test_transform_quality.py` and green CI badge.

**Tradeoff:** Not every rule belongs in YAML vs code—I keep structural checks in YAML and business math in code.
