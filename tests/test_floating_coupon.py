import pytest
from datetime import date
from pydantic import ValidationError
import QuantLib as ql

from pricer.instruments.floating_coupon import FloatingCouponModel, FloatingCoupon

# Setup global QuantLib evaluation date pour les tests
@pytest.fixture(autouse=True)
def set_ql_evaluation_date():
    todays_date = ql.Date(31, 1, 2025)
    ql.Settings.instance().evaluationDate = todays_date


def get_flat_curve(rate=0.03):
    today = ql.Settings.instance().evaluationDate
    curve = ql.FlatForward(today, rate, ql.Actual360())
    return ql.YieldTermStructureHandle(curve)


def test_valid_model_creation():
    model = FloatingCouponModel(
        start_date=date(2025, 1, 31),
        end_date=date(2025, 4, 30),
        payment_date=date(2025, 5, 2),
        notional=1_000_000,
        spread=0.0025,
        index_name="EURIBOR3M",
        calendar="TARGET",
        day_count="Actual360",
        fixing_lag=2,
        convention="ModifiedFollowing"
    )
    assert model.notional == 1_000_000
    assert model.spread == 0.0025


def test_invalid_notional():
    with pytest.raises(ValidationError, match="notionnel"):
        FloatingCouponModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 4, 30),
            payment_date=date(2025, 5, 2),
            notional=0,
            spread=0.0,
            index_name="EURIBOR3M"
        )


def test_invalid_calendar():
    with pytest.raises(ValidationError, match="Calendrier non supporté"):
        FloatingCouponModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 4, 30),
            payment_date=date(2025, 5, 2),
            notional=1_000_000,
            calendar="INVALID_CAL",
            spread=0.0,
        )


def test_invalid_day_count():
    with pytest.raises(ValidationError, match="Day count non supporté"):
        FloatingCouponModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 4, 30),
            payment_date=date(2025, 5, 2),
            notional=1_000_000,
            day_count="InvalidDC",
            spread=0.0,
        )


def test_invalid_fixing_lag():
    with pytest.raises(ValidationError, match="Fixing lag doit être positif"):
        FloatingCouponModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 4, 30),
            payment_date=date(2025, 5, 2),
            notional=1_000_000,
            fixing_lag=-1,
        )


def test_invalid_convention():
    with pytest.raises(ValidationError, match="Convention 'InvalidConv' non supportée"):
        FloatingCouponModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 4, 30),
            payment_date=date(2025, 5, 2),
            notional=1_000_000,
            convention="InvalidConv",
        )


def test_invalid_dates_order():
    with pytest.raises(ValidationError, match="date de fin doit être après"):
        FloatingCouponModel(
            start_date=date(2025, 4, 30),
            end_date=date(2025, 1, 31),
            payment_date=date(2025, 5, 2),
            notional=1_000_000,
        )

    with pytest.raises(ValidationError, match="date de paiement doit être après"):
        FloatingCouponModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 4, 30),
            payment_date=date(2025, 4, 29),
            notional=1_000_000,
        )


def test_floating_coupon_amount_forward_curve():
    model = FloatingCouponModel(
        start_date=date(2025, 1, 31),
        end_date=date(2025, 4, 30),
        payment_date=date(2025, 5, 2),
        notional=1_000_000,
        spread=0.001,
        calendar="TARGET",
        day_count="Actual360",
        fixing_lag=2,
        convention="ModifiedFollowing"
    )
    curve_handle = get_flat_curve(0.03)
    index = ql.Euribor3M(curve_handle)

    coupon = FloatingCoupon(model, index)
    # Convertir les dates en QuantLib Date
    ql_start = ql.Date(model.start_date.day, model.start_date.month, model.start_date.year)
    ql_end = ql.Date(model.end_date.day, model.end_date.month, model.end_date.year)

    amount = coupon.amount()

    accrual = coupon.day_count.yearFraction(ql_start, ql_end)

    expected_amount = model.notional * (coupon.index_rate + model.spread) * accrual

    assert abs(amount - expected_amount) < 1e-6

def test_floating_coupon_amount_with_fixing():
    # Setup du modèle
    model = FloatingCouponModel(
        start_date=date(2025, 1, 31),
        end_date=date(2025, 4, 30),
        payment_date=date(2025, 5, 2),
        notional=1_000_000,
        spread=0.001,
        calendar="TARGET",
        day_count="Actual360",
        fixing_lag=2,
        convention="ModifiedFollowing"
    )

    # Courbe plate à 3%
    curve_handle = get_flat_curve(0.03)
    index = ql.Euribor3M(curve_handle)

    # 1ère instanciation temporaire pour récupérer la fixing_date
    temp_coupon = FloatingCoupon(model, index)
    fixing_date = temp_coupon.fixing_date

    # Ajouter un fixing historique à cette date
    index.addFixing(fixing_date, 0.025)

    # 2ème instanciation : cette fois le taux utilisera le fixing
    coupon = FloatingCoupon(model, index)
    amount = coupon.amount()

    # Vérification du montant attendu
    accrual = coupon.day_count.yearFraction(
        ql.Date(model.start_date.day, model.start_date.month, model.start_date.year),
        ql.Date(model.end_date.day, model.end_date.month, model.end_date.year)
    )
    expected_amount = 1_000_000 * (0.025 + 0.001) * accrual
    assert abs(amount - expected_amount) < 1e-8


def test_repr_contains_key_fields():
    model = FloatingCouponModel(
        start_date=date(2025, 1, 31),
        end_date=date(2025, 4, 30),
        payment_date=date(2025, 5, 2),
        notional=1_000_000,
        spread=0.001,
        calendar="TARGET",
        day_count="Actual360",
        fixing_lag=2,
        convention="ModifiedFollowing"
    )
    curve_handle = get_flat_curve(0.03)
    index = ql.Euribor3M(curve_handle)

    coupon = FloatingCoupon(model, index)
    rep = repr(coupon)

    assert "FloatingCoupon" in rep
    assert "January 31st, 2025" in rep
    assert "April 30th, 2025" in rep
    assert "May 2nd, 2025" in rep
    assert "notional=1000000.0" in rep or "notional=1000000" in rep
    assert "EURIBOR3M" in rep
    assert f"spread={model.spread:.6f}" in rep

