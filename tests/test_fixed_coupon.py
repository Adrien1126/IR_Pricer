import pytest
from datetime import date
from pydantic import ValidationError
import QuantLib as ql
from pricer.instruments.fixed_coupon import FixedCouponModel, FixedCoupon


def test_valid_coupon_amount():
    """Montant calculé correctement avec Actual/360"""
    model = FixedCouponModel(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 7, 1),
        payment_date=date(2025, 7, 3),
        notional=1_000_000,
        fixed_rate=0.05,
        calendar="TARGET",
        day_count="Actual360",
    )
    coupon = FixedCoupon(model)

    montant = coupon.amount()
    expected = 1_000_000 * 0.05 * ql.Actual360().yearFraction(
        ql.Date(1,1,2025), ql.Date(1,7,2025)
    )
    assert pytest.approx(montant, rel=1e-6) == expected



def test_invalid_notional():
    """Notionnel doit être positif"""
    with pytest.raises(ValidationError):
        FixedCouponModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 7, 1),
            payment_date=date(2025, 7, 3),
            notional=0,
            fixed_rate=0.05,
        )


def test_invalid_rate():
    """Le taux doit être entre 0 et 1"""
    with pytest.raises(ValidationError):
        FixedCouponModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 7, 1),
            payment_date=date(2025, 7, 3),
            notional=1_000_000,
            fixed_rate=1.5,
        )


def test_invalid_dates():
    """Les dates doivent être cohérentes"""
    # end_date <= start_date
    with pytest.raises(ValidationError):
        FixedCouponModel(
            start_date=date(2025, 7, 1),
            end_date=date(2025, 1, 1),
            payment_date=date(2025, 7, 3),
            notional=1_000_000,
            fixed_rate=0.05,
        )

    # payment_date < end_date
    with pytest.raises(ValidationError):
        FixedCouponModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 7, 1),
            payment_date=date(2025, 6, 30),
            notional=1_000_000,
            fixed_rate=0.05,
        )


def test_repr_contains_fields():
    """__repr__ doit contenir les champs clés"""
    model = FixedCouponModel(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 7, 1),
        payment_date=date(2025, 7, 3),
        notional=1_000_000,
        fixed_rate=0.05,
    )
    coupon = FixedCoupon(model)
    rep = repr(coupon)
    assert "FixedCoupon" in rep
    assert "January 1st" in rep
    assert "July 1st" in rep
    assert "July 3rd" in rep
    assert "0.05" in rep

