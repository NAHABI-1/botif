from __future__ import annotations

from sqlalchemy import JSON, Numeric

JSON_DOCUMENT = JSON
PRICE_NUMERIC = Numeric(18, 6)
MONEY_NUMERIC = Numeric(18, 4)
VOLUME_NUMERIC = Numeric(18, 6)
SCORE_NUMERIC = Numeric(18, 6)
RATIO_NUMERIC = Numeric(18, 6)
