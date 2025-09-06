from pricer.pricers.base_pricer import BasePricer
from pricer.instruments.fixed_coupon import FixedCoupon
from pricer.instruments.floating_coupon import FloatingCoupon
from pricer.curves.discount_curve import DiscountCurve
from pricer.utils.dates import to_pydate


class DiscountingPricer(BasePricer):
    """
    Pricer par actualisation des cash flows.
    Compatible avec FixedCoupon et FloatingCoupon.
    """

    def price(self, instrument, curve: DiscountCurve) -> float:
        if isinstance(instrument, (FixedCoupon, FloatingCoupon)):
            amount = instrument.amount()
            df = curve.discount_factor(to_pydate(instrument.payment_date))
            print(f"Montant: {amount}, DF({to_pydate(instrument.payment_date)}) = {df}")
            return amount * df

        else:
            raise ValueError(
                f"Type d'instrument non supporté: {type(instrument)}. "
                f"Seuls FixedCoupon et FloatingCoupon sont supportés pour l'instant."
            )

    


from datetime import date
import QuantLib as ql

from pricer.instruments.fixed_coupon import FixedCoupon, FixedCouponModel
from pricer.instruments.floating_coupon import FloatingCoupon, FloatingCouponModel
from pricer.curves.discount_curve import DiscountCurveModel, DiscountCurve
from pricer.pricers.discounting import DiscountingPricer
from pricer.utils.dates import advance_date, to_pydate


def main():
    today = date.today()

    # ---------------------------
    # 1️⃣ FixedCoupon
    # ---------------------------
    fixed_model = FixedCouponModel(
        start_date=today,
        end_date=advance_date(today, "6M"),
        payment_date=advance_date(today, "6M", convention="Following"),
        notional=1_000_000,
        fixed_rate=0.05,
        day_count="Actual360",
        calendar="TARGET"
    )
    fixed_coupon = FixedCoupon(fixed_model)

    # ---------------------------
    # 2️⃣ FloatingCoupon
    # ---------------------------
    # 2a. Initialisation QuantLib
    ql_today = ql.Date(today.day, today.month, today.year)
    ql.Settings.instance().evaluationDate = ql_today

    flat_curve = ql.FlatForward(ql_today, 0.03, ql.Actual360())  # taux 3%
    curve_handle = ql.YieldTermStructureHandle(flat_curve)
    euribor3m = ql.Euribor3M(curve_handle)

    # 2b. Modèle FloatingCoupon
    float_model = FloatingCouponModel(
        start_date=today,
        end_date=advance_date(today, "3M"),
        payment_date=advance_date(today, "3M", convention="Following"),
        notional=1_000_000,
        spread=0.0025,          # 25bps
        index_name="EURIBOR3M",
        calendar="TARGET",
        day_count="Actual360",
        fixing_lag=2,
        convention="ModifiedFollowing"
    )
    float_coupon = FloatingCoupon(float_model, euribor3m)

    # ---------------------------
    # 3️⃣ Courbe de discount
    # ---------------------------
    discount_model = DiscountCurveModel(
        value_date=today,
        pillars=[("0D", 1.0), ("3M", 0.995), ("6M", 0.98), ("1Y", 0.95)],
        interp_method="linear",
        interpolation_on="log_discount",
        allow_extrapolation=True,
        day_count="Actual360",
        calendar="TARGET",
        business_day_convention="ModifiedFollowing",
        currency="EUR",
        curve_id="EUR_EONIA_DISC"
    )
    discount_curve = DiscountCurve.from_model(discount_model)

    # ---------------------------
    # 4️⃣ Pricing avec DiscountingPricer
    # ---------------------------
    pricer = DiscountingPricer()

    fixed_npv = pricer.price(fixed_coupon, discount_curve)
    print(f"NPV du FixedCoupon : {fixed_npv:,.2f} EUR")

    float_npv = pricer.price(float_coupon, discount_curve)
    print(f"NPV du FloatingCoupon : {float_npv:,.2f} EUR")


if __name__ == "__main__":
    main()
