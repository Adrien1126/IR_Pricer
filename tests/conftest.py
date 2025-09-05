import pytest
from datetime import date
import QuantLib as ql

from pricer.instruments.fixed_coupon import FixedCouponModel


@pytest.fixture(scope="session", autouse=True)
def setup_quantlib_eval_date():
    """
    Fixe une date d'évaluation globale QuantLib pour tous les tests.
    """
    ql.Settings.instance().evaluationDate = ql.Date(1, 1, 2025)


@pytest.fixture
def valid_fixed_coupon_model():
    """Coupon fixe valide pour les tests"""
    return FixedCouponModel(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 7, 1),
        payment_date=date(2025, 7, 3),
        notional=1_000_000,
        fixed_rate=0.05,
        calendar="TARGET",
        day_count="Actual360",
    )
