# tests/test_swap.py

from datetime import date
import QuantLib as ql
from pricer.instruments.swap import SwapModel, Swap


def test_swap_construction():
    trade_date = date(2025, 1, 31)
    end_date = date(2026, 1, 31)

    ql.Settings.instance().evaluationDate = ql.Date(trade_date.day, trade_date.month, trade_date.year)

    # Courbe plate pour simplification
    curve = ql.FlatForward(ql.Settings.instance().evaluationDate, 0.03, ql.Actual360())
    index_handle = ql.YieldTermStructureHandle(curve)
    index = ql.Euribor3M(index_handle)

    model = SwapModel(
        trade_date=trade_date,
        end_date=end_date,
        notional=1_000_000,
        fixed_rate=0.05,
        fixed_frequency="1M",
        floating_frequency="1M",
        spread=0.0025,
        floating_payment_lag=2,
    )

    swap = Swap(model, floating_index=index)

    # Test basiques
    assert swap.fixed_leg is not None
    assert swap.floating_leg is not None
    assert len(swap.fixed_leg.coupons) == len(swap.floating_leg.coupons)

    # Vérifie le premier coupon fixed
    first_fixed_coupon = swap.fixed_leg.coupons[0]
    assert first_fixed_coupon.amount() > 0

    # Vérifie le premier coupon floating
    first_floating_coupon = swap.floating_leg.coupons[0]
    assert first_floating_coupon.amount() > 0
