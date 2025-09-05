import pytest
from datetime import date
import QuantLib as ql
from pydantic import ValidationError

from pricer.instruments.fixed_coupon import FixedCouponModel, FixedCoupon


def test_coupon_amount_actual360(valid_fixed_coupon_model):
    """Montant calculé correctement avec Actual/360"""
    coupon = FixedCoupon(valid_fixed_coupon_model)

    expected = valid_fixed_coupon_model.notional * valid_fixed_coupon_model.fixed_rate * ql.Actual360().yearFraction(
        ql.Date(1, 1, 2025), ql.Date(1, 7, 2025)
    )
    assert pytest.approx(coupon.amount(), rel=1e-6) == expected


def test_coupon_amount_actual365():
    """Test du montant avec Actual/365Fixed"""
    model = FixedCouponModel(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 7, 1),
        payment_date=date(2025, 7, 3),
        notional=1_000_000,
        fixed_rate=0.05,
        calendar="TARGET",
        day_count="Actual365Fixed",
    )
    coupon = FixedCoupon(model)

    expected = model.notional * model.fixed_rate * ql.Actual365Fixed().yearFraction(
        ql.Date(1, 1, 2025), ql.Date(1, 7, 2025)
    )
    assert pytest.approx(coupon.amount(), rel=1e-6) == expected


def test_invalid_notional():
    """Erreur si notional <= 0"""
    with pytest.raises(ValidationError, match="strictement positif"):
        FixedCouponModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 7, 1),
            payment_date=date(2025, 7, 3),
            notional=0,
            fixed_rate=0.05,
        )


def test_invalid_rate():
    """Erreur si taux > 1"""
    with pytest.raises(ValidationError, match="entre 0 et 1"):
        FixedCouponModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 7, 1),
            payment_date=date(2025, 7, 3),
            notional=1_000_000,
            fixed_rate=1.5,
        )


def test_invalid_dates():
    """Vérifie que les dates incohérentes lèvent une erreur"""
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


def test_invalid_day_count():
    """Erreur si day_count non reconnu"""
    with pytest.raises(ValueError, match="Day count.*non supporté"):
        FixedCouponModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 7, 1),
            payment_date=date(2025, 7, 3),
            notional=1_000_000,
            fixed_rate=0.05,
            day_count="FAUX_JOUR",
        )


def test_repr_output(valid_fixed_coupon_model):
    """__repr__ contient les informations clés du coupon"""
    coupon = FixedCoupon(valid_fixed_coupon_model)
    rep = repr(coupon)

    assert "FixedCoupon" in rep
    assert "January 1st" in rep
    assert "July 1st" in rep
    assert "July 3rd" in rep
    assert "0.05" in rep
