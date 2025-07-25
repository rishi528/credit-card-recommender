################################################################################
#                          Smart Credit-Card Recommender                       #
#                               version 4.0 (July-2025)                        #
################################################################################
import json

# 2) Add your merchant‐to‐category mapping dictionary BEFORE you reference it
MERCHANT_CATEGORIES = {
    "swiggy": "dining",   "zomato": "dining",
    "bigbasket": "grocery","grofers": "grocery",
    "amazon": "ecommerce","flipkart": "ecommerce"
    }

import streamlit as st
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

# ──────────────────────────────────────────────────────────────────────────────
#  1.  PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Smart Credit-Card Recommender",
                   page_icon="💳",
                   layout="wide")

# ------------------------------------------------------------------------------
#  2.  CONSTANT HELPERS
# ------------------------------------------------------------------------------
DEC_ZERO   = Decimal("0")
DEC_HUND   = Decimal("100")
ROUND_2    = lambda x: x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def dec(x: float|str|Decimal) -> Decimal:
    """Safe Decimal cast."""
    try:
        return Decimal(str(x))
    except (InvalidOperation, TypeError):
        return DEC_ZERO

# ------------------------------------------------------------------------------
#  3.  DATABASE – FULLY NORMALISED
# ------------------------------------------------------------------------------

CARD = dict[str, str|int|Decimal|dict]                   # type alias

def _card(name: str, bank: str, fee: int, base: float,
          cats: dict[str, dict], perks: list[str]) -> CARD:
    return dict(name=name, bank=bank,
                annual_fee=fee,
                base_rate=dec(base),
                categories=cats,
                perks=perks)

def cat(rate: float|Decimal,
        typ: str="points",
        cap: int|None=None,
        partners: list[str]|None=None,
        discount_cap: int|None=None) -> dict:
    return dict(rate=dec(rate),
                type=typ,
                cap=cap,
                partners=[p.lower() for p in partners] if partners else [],
                discount_cap=dec(discount_cap) if discount_cap else None)

CARDS: dict[str, CARD] = {
    # ───── HDFC ───────────────────────────────────────────────────────────────
    "hdfc_infinia": _card(
        "HDFC Infinia Metal", "HDFC Bank", 12_500, 3.33,
        {
            "other": cat(3.33)
        },
        ["Unlimited lounge access", "Golf", "Concierge"]
    ),
    "hdfc_diners_black": _card(
        "HDFC Diners Club Black", "HDFC Bank", 10_000, 3.33,
        {
            "dining" : cat(6.6, cap=1_000),
            "movies" : cat(500, typ="bogo", cap=2),
            "other"  : cat(3.33)
        },
        ["BOGO movies", "6.6 % weekend dining", "Unlimited lounge"]
    ),

    # ───── AXIS ───────────────────────────────────────────────────────────────
    "axis_ace": _card(
        "Axis ACE", "Axis Bank", 499, 1.5,
        {
            "utilities": cat(5, cap=500),
            "dining"   : cat(4, cap=500),
            "other"    : cat(1.5)
        },
        ["5 % GPay utilities", "4 lounge visits"]
    ),
    "axis_atlas": _card(
        "Axis Atlas", "Axis Bank", 5_000, 2.0,
        {
            "travel": cat(10),
            "other" : cat(2)
        },
        ["EDGE Miles", "8 lounges", "Travel-centric"]
    ),
    "axis_magnus": _card(
        "Axis Magnus", "Axis Bank", 30_000, 4.8,
        {
            "other": cat(4.8)
        },
        ["Unlimited lounge", "Premium concierge"]
    ),
    "flipkart_axis": _card(
        "Flipkart Axis", "Axis Bank", 500, 1.5,
        {
            "ecommerce": cat(5, partners=["flipkart", "myntra"]),
            "other": cat(1.5)
        },
        ["5 % on Flipkart/Myntra"]
    ),

    # ───── SBI ────────────────────────────────────────────────────────────────
    "sbi_cashback": _card(
        "SBI Cashback", "SBI", 999, 1,
        {
            "online_spends": cat(5, cap=5_000),
            "other": cat(1)
        },
        ["Unlimited 5 % online cashback"]
    ),
    "sbi_simplyclick": _card(
        "SBI SimplyCLICK", "SBI", 499, 0.25,
        {
            "ecommerce": cat(2.5,
                             partners=["amazon", "bookmyshow", "cleartrip"]),
            "other": cat(0.25)
        },
        ["10X partner rewards"]
    ),
    "sbi_prime": _card(
        "SBI Prime", "SBI", 2_999, 0.5,
        {
            "dining" : cat(2.5),
            "grocery": cat(2.5),
            "movies" : cat(2.5),
            "other"  : cat(0.5)
        },
        ["Club Vistara Silver", "Quarterly vouchers"]
    ),

    # ───── ICICI ──────────────────────────────────────────────────────────────
    "amazon_pay_icici": _card(
        "Amazon Pay ICICI", "ICICI", 0, 1,
        {
            "ecommerce": cat(5, partners=["amazon"]),
            "other"    : cat(1)
        },
        ["Lifetime free", "5 % on Amazon (Prime)"]
    ),
    "icici_coral": _card(
        "ICICI Coral", "ICICI", 500, 0.5,
        {
            "movies": cat(25, typ="discount", discount_cap=100),
            "other": cat(0.5)
        },
        ["25 % movie discount", "Railway lounge"]
    ),

    # ───── STANCHART ──────────────────────────────────────────────────────────
    "sc_super_value": _card(
        "SC Super Value", "Standard Chartered", 750, 0.25,
        {
            "fuel"     : cat(5, cap=200),
            "utilities": cat(5, cap=100),
            "other"    : cat(0.25)
        },
        ["5 % fuel + utilities"]
    ),

    # ───── HSBC ───────────────────────────────────────────────────────────────
    "hsbc_live_plus": _card(
        "HSBC Live+ Cashback", "HSBC", 999, 1.5,
        {
            "dining" : cat(10, cap=1_000),
            "grocery": cat(10, cap=1_000),
            "fuel"   : cat(0),
            "other"  : cat(1.5)
        },
        ["10 % dining/grocery", "Unlimited 1.5 % elsewhere"]
    ),

    # ───── RBL / INDUSIND ─────────────────────────────────────────────────────
    "rbl_world_safari": _card(
        "RBL World Safari", "RBL", 3_000, 0.75,
        {
            "travel": cat(1.87),
            "other" : cat(0.75)
        },
        ["0 % forex markup", "Travel insurance"]
    ),
    "indusind_pinnacle": _card(
        "IndusInd Pinnacle", "IndusInd", 15_000, 1.8,
        {
            "movies": cat(700, typ="bogo", cap=4),
            "other" : cat(1.8)
        },
        ["BOGO movies", "Golf"]
    )
}

################################################################################
# 4. VALIDATION SUITE (30 SCENARIOS) – COMPACT JSON‐LIST
################################################################################
SCENARIOS: list[dict] = pd.read_csv(                # we load directly from the
    "2025-07-25T15-36_export.csv").fillna("").to_dict("records")  # attached CSV
# The CSV from your attachment already contains the full 30-test matrix.

################################################################################
# 5. CATEGORY RESOLUTION
################################################################################
def merchant_category(merchant: str) -> str:
    m = merchant.lower()
    for key, cat in MERCHANT_CATEGORIES.items():
        if key in m:
            return cat
    # generic online fallback handled later
    return "other"

################################################################################
# 6. REWARD ENGINE
################################################################################
def reward_for(card: CARD, merchant: str, amount: int|float,
               month_spend: dict[str, Decimal]) -> tuple[Decimal, str]:
    cat = merchant_category(merchant)
    amt = dec(amount)
    cdata = card["categories"].get(cat, card["categories"].get("other"))
    if not cdata: return DEC_ZERO, "No matching category"

    # partner check
    if cdata["partners"] and all(p not in merchant.lower() for p in cdata["partners"]):
        cdata = card["categories"].get("other")

    rate         = cdata["rate"]
    reward_type  = cdata.get("type", "points")
    cap          = dec(cdata.get("cap")) if cdata.get("cap") else None
    discount_cap = cdata.get("discount_cap")

    spent_key = f"{card['name']}_{cat}"
    spent     = month_spend.get(spent_key, DEC_ZERO)
    if cap and spent >= cap: return DEC_ZERO, "Cap reached"

    eligible_amt = min(amt, cap - spent) if cap else amt

    if reward_type == "bogo":
        reward = min(eligible_amt, rate)
    elif reward_type == "discount":
        reward = min((eligible_amt * rate) / DEC_HUND, discount_cap)
    else:
        reward = (eligible_amt * rate) / DEC_HUND

    return ROUND_2(reward), f"{rate}% ({reward_type})"

def best_cards(card_ids: list[str], merchant: str, amount: int|float,
               month_spend: dict[str, Decimal]) -> list[dict]:
    recs = []
    for cid in card_ids:
        card = CARDS[cid]
        reward, note = reward_for(card, merchant, amount, month_spend)
        recs.append(dict(card_id=cid,
                         name=card["name"],
                         bank=card["bank"],
                         fee=card["annual_fee"],
                         reward=float(reward),
                         note=note))
    recs.sort(key=lambda r: (-r["reward"], r["fee"]))
    return recs

################################################################################
# 7. VALIDATION RUNNER
################################################################################
def run_suite():
    out = []
    for row in SCENARIOS:
        month_spent = {k: dec(v) for k, v in json.loads(row["current_month_spent"] or "{}").items()}
        lineup      = row["user_cards"].strip("[]").replace("'", "").split(",")
        lineup      = [c.strip() for c in lineup if c.strip()]
        top         = best_cards(lineup, row["merchant"], row["amount"], month_spent)[0]
        ok_card     = top["card_id"] == row["expected_winner"]
        ok_reward   = abs(top["reward"] - row["expected_reward"]) <= 0.02
        status, acc = ("✅ PASS", 100) if (ok_card and ok_reward) else \
                      ("⚠️ PARTIAL", 75) if ok_card else ("❌ FAIL", 0)
        out.append(dict(TestID=row["test_id"], Scenario=row["Scenario"],
                        Expected=row["Expected"], Got=f"{top['name']} ₹{top['reward']:.2f}",
                        Status=status, Accuracy=acc))
    return pd.DataFrame(out)

################################################################################
# 8. STREAMLIT INTERFACE
################################################################################
st.sidebar.header("Your Wallet")
selection = st.sidebar.multiselect("Choose cards you own",
                                   options=list(CARDS.keys()),
                                   format_func=lambda cid: CARDS[cid]["name"])
st.sidebar.markdown("---")
if st.sidebar.button("Reset"):
    selection.clear()

tab_rec, tab_val, tab_cards = st.tabs(["Recommendation", "Validation", "All Cards"])

# ─── Recommendation Tab ──────────────────────────────────────────────────────
with tab_rec:
    st.subheader("Get the Best Card for Your Purchase")
    colA, colB = st.columns(2)
    mer = colA.text_input("Merchant Name", "Amazon")
    amt = colB.number_input("Amount (₹)", min_value=1, value=2500, step=50)

    if not selection:
        st.info("Add cards to your wallet in the sidebar.")
    elif st.button("Recommend"):
        res = best_cards(selection, mer, amt, {})
        cat = merchant_category(mer)
        st.success(f"Detected Category: **{cat.title()}**")
        for i, rec in enumerate(res[:3]):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            st.write(f"{medal} **{rec['name']}** — Reward: ₹{rec['reward']:.2f} ({rec['note']}) | Annual fee: ₹{rec['fee']:,}")

# ─── Validation Tab ──────────────────────────────────────────────────────────
with tab_val:
    st.subheader("30-Test Accuracy Suite")
    if st.button("Run All Tests"):
        df = run_suite()
        st.session_state["val_df"] = df
    if (df := st.session_state.get("val_df")) is not None:
        st.dataframe(df, height=500, use_container_width=True)
        avg = df["Accuracy"].mean()
        st.metric("Overall Accuracy", f"{avg:.1f}%")
        if avg >= 85:
            st.balloons()
            st.success("Target met! 🎉")
        else:
            st.warning("Below target – inspect failed tests.")

# ─── Card Browser Tab ────────────────────────────────────────────────────────
with tab_cards:
    st.subheader("Card Database")
    df_cards = pd.DataFrame([dict(Name=v["name"], Bank=v["bank"], Fee=v["annual_fee"],
                                  BaseRate=float(v["base_rate"])) for v in CARDS.values()])
    st.dataframe(df_cards, height=400)
