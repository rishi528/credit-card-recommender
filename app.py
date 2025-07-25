import streamlit as st
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Credit Card Recommender",
    page_icon="💳",
    layout="wide"
)

# --- Full Database and Scenarios ---

# Full Credit Card Database with Decimal rates for precision
CREDIT_CARDS_DB = {
    "hdfc_infinia": {
        "name": "HDFC Infinia Metal", "bank": "HDFC Bank", "annual_fee": 12500, "base_rate": Decimal('3.33'),
        "categories": {
            "fuel": {"rate": Decimal('3.33')}, "dining": {"rate": Decimal('3.33')}, "grocery": {"rate": Decimal('3.33')},
            "travel": {"rate": Decimal('3.33')}, "utilities": {"rate": Decimal('3.33')}, "ecommerce": {"rate": Decimal('3.33')},
            "other": {"rate": Decimal('3.33')}
        }, "special_benefits": ["Unlimited lounge", "Golf access", "Concierge"]
    },
    "hdfc_diners_black": {
        "name": "HDFC Diners Club Black", "bank": "HDFC Bank", "annual_fee": 10000, "base_rate": Decimal('3.33'),
        "categories": {
            "dining": {"rate": Decimal('6.6'), "cap": 1000},
            "movies": {"type": "bogo", "rate": Decimal('500'), "cap": 2},
            "other": {"rate": Decimal('3.33')}
        }, "special_benefits": ["BOGO movies", "Weekend dining 6.6%", "Unlimited lounge"]
    },
    "hdfc_regalia_gold": {
        "name": "HDFC Regalia Gold", "bank": "HDFC Bank", "annual_fee": 2500, "base_rate": Decimal('2.67'),
        "categories": {
            "ecommerce": {"rate": Decimal('11'), "partner_merchants": ["nykaa", "myntra"]},
            "grocery": {"rate": Decimal('11'), "partner_merchants": ["spencer", "reliance smart"]},
            "other": {"rate": Decimal('2.67')}
        }, "special_benefits": ["12 domestic + 6 international lounge", "Partner discounts"]
    },
    "hdfc_millennia": {
        "name": "HDFC Millennia", "bank": "HDFC Bank", "annual_fee": 1000, "base_rate": Decimal('1.0'),
        "categories": {
            "ecommerce": {"rate": Decimal('5.0'), "cap": 1000, "partner_merchants": ["amazon", "flipkart", "myntra", "ajio"]},
            "dining": {"rate": Decimal('5.0'), "cap": 1000, "partner_merchants": ["swiggy", "zomato"]},
            "utilities": {"rate": Decimal('0')},
            "other": {"rate": Decimal('1.0')}
        }, "special_benefits": ["5% on 10+ e-commerce partners", "Low annual fee"]
    },
    "axis_ace": {
        "name": "Axis ACE", "bank": "Axis Bank", "annual_fee": 499, "base_rate": Decimal('1.5'),
        "categories": {
            "utilities": {"rate": Decimal('5.0'), "cap": 500},
            "dining": {"rate": Decimal('4.0'), "cap": 500},
            "other": {"rate": Decimal('1.5')}
        }, "special_benefits": ["Google Pay utility benefits", "4 domestic lounge visits"]
    },
    "flipkart_axis": {
        "name": "Flipkart Axis Bank", "bank": "Axis Bank", "annual_fee": 500, "base_rate": Decimal('1.5'),
        "categories": {
            "ecommerce": {"rate": Decimal('5.0'), "partner_merchants": ["flipkart", "myntra"]},
            "other": {"rate": Decimal('1.5')}
        }, "special_benefits": ["5% on Flipkart & Myntra"]
    },
    "axis_magnus": {
        "name": "Axis Magnus for Burgundy", "bank": "Axis Bank", "annual_fee": 30000, "base_rate": Decimal('4.8'),
        "categories": {"other": {"rate": Decimal('4.8')}},
        "special_benefits": ["Unlimited lounge", "High EDGE points value"]
    },
    "axis_atlas": {
        "name": "Axis Atlas", "bank": "Axis Bank", "annual_fee": 5000, "base_rate": Decimal('2.0'),
        "categories": {"travel": {"rate": Decimal('10.0')}, "other": {"rate": Decimal('2.0')}},
        "special_benefits": ["Travel-focused rewards", "EDGE Miles transfers"]
    },
    "sbi_cashback": {
        "name": "SBI Cashback", "bank": "State Bank of India", "annual_fee": 999, "base_rate": Decimal('1.0'),
        "categories": {"online_spends": {"rate": Decimal('5.0'), "cap": 5000}, "other": {"rate": Decimal('1.0')}},
        "special_benefits": ["5% on all online spends", "Simple structure"]
    },
    "sbi_simplyclick": {
        "name": "SBI SimplyCLICK", "bank": "State Bank of India", "annual_fee": 499, "base_rate": Decimal('0.25'),
        "categories": {"ecommerce": {"rate": Decimal('2.5'), "partner_merchants": ["amazon", "bookmyshow", "cleartrip"]}, "other": {"rate": Decimal('0.25')}},
        "special_benefits": ["10X rewards on partners", "Amazon voucher"]
    },
    "sbi_prime": {
        "name": "SBI Prime", "bank": "State Bank of India", "annual_fee": 2999, "base_rate": Decimal('0.5'),
        "categories": {"dining": {"rate": Decimal('2.5')}, "grocery": {"rate": Decimal('2.5')}, "movies": {"rate": Decimal('2.5')}, "other": {"rate": Decimal('0.5')}},
        "special_benefits": ["Club Vistara Silver", "Quarterly vouchers"]
    },
    "icici_coral": {
        "name": "ICICI Coral", "bank": "ICICI Bank", "annual_fee": 500, "base_rate": Decimal('0.5'),
        "categories": {"movies": {"type": "discount", "rate": Decimal('25'), "discount_cap": Decimal('100')}, "other": {"rate": Decimal('0.5')}},
        "special_benefits": ["Railway lounge access", "Movie benefits"]
    },
    "amazon_pay_icici": {
        "name": "Amazon Pay ICICI", "bank": "ICICI Bank", "annual_fee": 0, "base_rate": Decimal('1.0'),
        "categories": {"ecommerce": {"rate": Decimal('5.0'), "partner_merchants": ["amazon"]}, "other": {"rate": Decimal('1.0')}},
        "special_benefits": ["Lifetime free", "5% on Amazon for Prime"]
    },
    "sc_super_value": {
        "name": "Standard Chartered Super Value Titanium", "bank": "Standard Chartered", "annual_fee": 750, "base_rate": Decimal('0.25'),
        "categories": {"fuel": {"rate": Decimal('5.0'), "cap": 200}, "utilities": {"rate": Decimal('5.0'), "cap": 100}, "other": {"rate": Decimal('0.25')}},
        "special_benefits": ["Best fuel cashback 5%", "Utility/telecom focus"]
    },
    "hsbc_live_plus": {
        "name": "HSBC Live+ Cashback", "bank": "HSBC Bank", "annual_fee": 999, "base_rate": Decimal('1.5'),
        "categories": {"dining": {"rate": Decimal('10.0'), "cap": 1000}, "grocery": {"rate": Decimal('10.0'), "cap": 1000}, "fuel": {"rate": Decimal('0')}, "other": {"rate": Decimal('1.5')}},
        "special_benefits": ["10% dining/grocery", "Unlimited 1.5% elsewhere"]
    },
    "rbl_world_safari": {
        "name": "RBL World Safari", "bank": "RBL Bank", "annual_fee": 3000, "base_rate": Decimal('0.75'),
        "categories": {"travel": {"rate": Decimal('1.87')}, "other": {"rate": Decimal('0.75')}},
        "special_benefits": ["0% forex markup", "Travel insurance"]
    },
    "indusind_pinnacle": {
        "name": "IndusInd Pinnacle World", "bank": "IndusInd Bank", "annual_fee": 15000, "base_rate": Decimal('1.8'),
        "categories": {"movies": {"type": "bogo", "rate": Decimal('700'), "cap": 4}, "other": {"rate": Decimal('1.8')}},
        "special_benefits": ["BOGO movies", "Golf access"]
    }
}

MERCHANT_CATEGORIES = {
    "swiggy": "dining", "zomato": "dining", "dominos": "dining", "pizza hut": "dining", "mcdonald": "dining", "kfc": "dining", "burger king": "dining", "subway": "dining", "starbucks": "dining",
    "bigbasket": "grocery", "grofers": "grocery", "blinkit": "grocery", "zepto": "grocery", "dmart": "grocery", "reliance fresh": "grocery", "spencer": "grocery", "more": "grocery", "metro": "grocery", "grocery store": "grocery",
    "indian oil": "fuel", "hp petrol": "fuel", "bharat petroleum": "fuel", "shell": "fuel",
    "pvr": "movies", "inox": "movies", "cinepolis": "movies", "bookmyshow": "movies", "paytm movies": "movies", "pvr cinemas": "movies",
    "amazon": "ecommerce", "flipkart": "ecommerce", "myntra": "ecommerce", "ajio": "ecommerce", "nykaa": "ecommerce",
    "airtel": "utilities", "jio": "utilities", "vodafone": "utilities", "bses": "utilities", "tata power": "utilities",
    "irctc": "travel", "makemytrip": "travel", "goibibo": "travel", "cleartrip": "travel", "yatra": "travel", "uber": "travel", "ola": "travel",
    "default_online": "online_spends"
}

VALIDATION_SCENARIOS = [
    # Basic Category Optimization
    {"test_id": 1, "merchant": "Swiggy", "amount": 1000, "user_cards": ["hdfc_diners_black", "axis_ace", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "hdfc_diners_black", "expected_reward": 66.0, "description": "Dining: Diners Black 6.6% > SBI 5% > ACE 4%"},
    {"test_id": 2, "merchant": "BigBasket", "amount": 1500, "user_cards": ["hsbc_live_plus", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "hsbc_live_plus", "expected_reward": 150.0, "description": "Grocery: HSBC Live+ 10% > SBI 5%"},
    {"test_id": 3, "merchant": "Amazon", "amount": 3000, "user_cards": ["amazon_pay_icici", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "amazon_pay_icici", "expected_reward": 150.0, "description": "E-commerce: Amazon Pay 5% vs SBI 5%"},
    {"test_id": 4, "merchant": "Indian Oil", "amount": 2000, "user_cards": ["sc_super_value", "hdfc_infinia", "axis_ace"], "current_month_spent": {}, "expected_winner": "sc_super_value", "expected_reward": 100.0, "description": "Fuel: SC Super Value 5% > Infinia 3.33%"},
    {"test_id": 5, "merchant": "MakeMyTrip", "amount": 10000, "user_cards": ["axis_atlas", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "axis_atlas", "expected_reward": 1000.0, "description": "Travel: Atlas 10% > SBI 5%"},
    {"test_id": 6, "merchant": "PVR Cinemas", "amount": 800, "user_cards": ["hdfc_diners_black", "indusind_pinnacle", "icici_coral"], "current_month_spent": {}, "expected_winner": "indusind_pinnacle", "expected_reward": 400.0, "description": "Movies: Pinnacle BOGO (800/2) > Diners BOGO (500) > Coral"}, # Corrected BOGO logic
    {"test_id": 7, "merchant": "Nykaa", "amount": 2000, "user_cards": ["hdfc_regalia_gold", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "hdfc_regalia_gold", "expected_reward": 220.0, "description": "E-commerce partner: Regalia Gold 11%"},
    {"test_id": 8, "merchant": "Dominos", "amount": 600, "user_cards": ["axis_ace", "sbi_prime"], "current_month_spent": {}, "expected_winner": "axis_ace", "expected_reward": 24.0, "description": "Dining: ACE 4% > SBI Prime 2.5%"},
    {"test_id": 9, "merchant": "Flipkart", "amount": 4000, "user_cards": ["flipkart_axis", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "flipkart_axis", "expected_reward": 200.0, "description": "E-commerce: Flipkart Axis 5% vs SBI 5%"},
    {"test_id": 10, "merchant": "Airtel", "amount": 1000, "user_cards": ["axis_ace", "sc_super_value"], "current_month_spent": {}, "expected_winner": "axis_ace", "expected_reward": 50.0, "description": "Utilities: ACE 5% vs SC 5%"},
    # Cap Management
    {"test_id": 11, "merchant": "Swiggy", "amount": 800, "user_cards": ["hdfc_diners_black", "axis_ace"], "current_month_spent": {"HDFC Diners Club Black_dining": Decimal("950")}, "expected_winner": "axis_ace", "expected_reward": 32.0, "description": "Cap: Diners cap almost full, ACE wins"},
    {"test_id": 12, "merchant": "BigBasket", "amount": 2000, "user_cards": ["hsbc_live_plus", "sbi_cashback"], "current_month_spent": {"HSBC Live+ Cashback_grocery": Decimal("900")}, "expected_winner": "sbi_cashback", "expected_reward": 100.0, "description": "Cap: HSBC partial cap, SBI wins"},
    {"test_id": 13, "merchant": "Indian Oil", "amount": 3000, "user_cards": ["sc_super_value", "hdfc_infinia"], "current_month_spent": {"Standard Chartered Super Value Titanium_fuel": Decimal("180")}, "expected_winner": "hdfc_infinia", "expected_reward": 99.9, "description": "Cap: SC cap nearly full, Infinia wins"},
    {"test_id": 14, "merchant": "Airtel", "amount": 500, "user_cards": ["axis_ace", "sc_super_value"], "current_month_spent": {"Axis ACE_utilities": Decimal("450")}, "expected_winner": "sc_super_value", "expected_reward": 25.0, "description": "Cap: ACE cap nearly full"},
    {"test_id": 15, "merchant": "Flipkart", "amount": 5000, "user_cards": ["flipkart_axis", "sbi_cashback"], "current_month_spent": {"SBI Cashback_online_spends": Decimal("4500")}, "expected_winner": "flipkart_axis", "expected_reward": 250.0, "description": "Cap: SBI cap nearly full"},
    # Large Transactions
    {"test_id": 16, "merchant": "MakeMyTrip", "amount": 50000, "user_cards": ["axis_atlas", "hdfc_infinia"], "current_month_spent": {}, "expected_winner": "axis_atlas", "expected_reward": 5000.0, "description": "Large travel: Atlas 10%"},
    {"test_id": 17, "merchant": "Amazon", "amount": 25000, "user_cards": ["amazon_pay_icici", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "amazon_pay_icici", "expected_reward": 1250.0, "description": "Large e-commerce"},
    {"test_id": 18, "merchant": "Indian Oil", "amount": 10000, "user_cards": ["sc_super_value", "hdfc_infinia"], "current_month_spent": {}, "expected_winner": "hdfc_infinia", "expected_reward": 333.0, "description": "Large fuel: Infinia (no cap) > SC (capped)"},
    {"test_id": 19, "merchant": "BigBasket", "amount": 15000, "user_cards": ["hsbc_live_plus", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "sbi_cashback", "expected_reward": 750.0, "description": "Large grocery: SBI (high cap) > HSBC (low cap)"},
    {"test_id": 20, "merchant": "Swiggy", "amount": 8000, "user_cards": ["hdfc_diners_black", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "sbi_cashback", "expected_reward": 400.0, "description": "Large dining: SBI (high cap) > Diners (low cap)"},
    # Multi-Bank & Tie-Breaking
    {"test_id": 21, "merchant": "Swiggy", "amount": 1000, "user_cards": ["hdfc_infinia", "hdfc_diners_black", "hdfc_millennia"], "current_month_spent": {}, "expected_winner": "hdfc_diners_black", "expected_reward": 66.0, "description": "HDFC cards: Diners 6.6% wins"},
    {"test_id": 22, "merchant": "Myntra", "amount": 2000, "user_cards": ["axis_ace", "flipkart_axis", "axis_magnus", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "sbi_cashback", "expected_reward": 100.0, "description": "Tie-break: SBI (lower fee) > Flipkart"},
    {"test_id": 23, "merchant": "BigBasket", "amount": 1000, "user_cards": ["sbi_cashback", "sbi_prime", "sbi_simplyclick"], "current_month_spent": {}, "expected_winner": "sbi_cashback", "expected_reward": 50.0, "description": "SBI cards: Cashback 5% wins"},
    # Small Amounts
    {"test_id": 24, "merchant": "Starbucks", "amount": 200, "user_cards": ["hdfc_diners_black", "axis_ace"], "current_month_spent": {}, "expected_winner": "hdfc_diners_black", "expected_reward": 13.2, "description": "Small dining"},
    {"test_id": 25, "merchant": "Indian Oil", "amount": 500, "user_cards": ["sc_super_value", "axis_ace"], "current_month_spent": {}, "expected_winner": "sc_super_value", "expected_reward": 25.0, "description": "Small fuel"},
    {"test_id": 26, "merchant": "Metro", "amount": 300, "user_cards": ["hsbc_live_plus", "sbi_cashback"], "current_month_spent": {}, "expected_winner": "hsbc_live_plus", "expected_reward": 30.0, "description": "Small grocery"},
    # Edge Cases & Exclusions
    {"test_id": 27, "merchant": "Airtel", "amount": 1000, "user_cards": ["hdfc_millennia", "axis_ace"], "current_month_spent": {}, "expected_winner": "axis_ace", "expected_reward": 50.0, "description": "Exclusion: Millennia has 0% on utilities"},
    {"test_id": 28, "merchant": "Indian Oil", "amount": 1000, "user_cards": ["hsbc_live_plus", "axis_ace"], "current_month_spent": {}, "expected_winner": "axis_ace", "expected_reward": 15.0, "description": "Exclusion: HSBC has 0% on fuel"},
    {"test_id": 29, "merchant": "Grocery Store", "amount": 1000, "user_cards": ["amazon_pay_icici", "icici_coral"], "current_month_spent": {}, "expected_winner": "amazon_pay_icici", "expected_reward": 10.0, "description": "Generic (Other): Amazon Pay (1%) > Coral (0.5%)"},
    {"test_id": 30, "merchant": "BookMyShow", "amount": 1000, "user_cards": ["sbi_simplyclick", "icici_coral", "axis_ace"], "current_month_spent": {}, "expected_winner": "icici_coral", "expected_reward": 100.0, "description": "Discount Logic: Coral 25% discount capped at ₹100"}
]


# --- Core Functions ---

def detect_merchant_category(merchant_name, is_online=True):
    merchant_lower = merchant_name.lower().strip()
    if is_online and any(kw in merchant_lower for kw in MERCHANT_CATEGORIES):
        pass # It's a known online partner
    elif is_online:
        return "online_spends" # Fallback for general online
    
    for m, c in MERCHANT_CATEGORIES.items():
        if m in merchant_lower:
            return c
    return "other"

def calculate_reward_value(card_data, category, merchant_name, amount, monthly_spent):
    amount_dec = Decimal(str(amount))
    cat_settings = card_data["categories"].get(category, card_data["categories"].get("other"))

    if "partner_merchants" in cat_settings:
        if not any(partner in merchant_name.lower() for partner in cat_settings["partner_merchants"]):
            cat_settings = card_data["categories"].get("other")
    
    if not cat_settings:
        return Decimal("0.00"), "N/A", "not_applicable"

    rate = cat_settings.get("rate", card_data.get("base_rate", Decimal('0')))
    cap = cat_settings.get("cap")
    reward_type = cat_settings.get("type", "points")
    discount_cap = cat_settings.get("discount_cap")

    if rate == 0:
        return Decimal("0.00"), "Excluded Category", "excluded"

    spending_key = f"{card_data['name']}_{category}"
    current_spent = monthly_spent.get(spending_key, Decimal("0.00"))
    if cap and current_spent >= cap:
        return Decimal("0.00"), f"Cap ₹{cap} Reached", "cap_reached"

    applicable_amount = amount_dec
    if cap:
        applicable_amount = min(amount_dec, Decimal(str(cap)) - current_spent)

    reward_value = Decimal("0.00")
    if reward_type == "bogo":
        reward_value = min(amount_dec / 2, rate) # Reward is half the txn value, capped at `rate`
    elif reward_type == "discount":
        potential_reward = (applicable_amount * rate) / Decimal("100")
        reward_value = min(potential_reward, discount_cap)
    else:
        reward_value = (applicable_amount * rate) / Decimal("100")
        
    desc = f"{rate}%"
    if reward_type == "bogo": desc = f"BOGO up to ₹{rate}"
    if reward_type == "discount": desc = f"{rate}% off, cap ₹{discount_cap}"
    
    return reward_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), desc, "ok"

def recommend_best_card(user_cards, merchant_name, amount, monthly_spent):
    category = detect_merchant_category(merchant_name)
    recommendations = []
    for card_id in user_cards:
        if card_id in CREDIT_CARDS_DB:
            card_data = CREDIT_CARDS_DB[card_id]
            reward_value, desc, status = calculate_reward_value(card_data, category, merchant_name, amount, monthly_spent)
            recommendations.append({
                "card_name": card_data["name"], "card_id": card_id, "reward_value": float(reward_value),
                "annual_fee": card_data["annual_fee"], "description": desc, "status": status
            })
    recommendations.sort(key=lambda x: (-x["reward_value"], x["annual_fee"]))
    return recommendations, category

def run_validation_tests():
    results = []
    for scenario in VALIDATION_SCENARIOS:
        monthly_spent_dec = {k: Decimal(str(v)) for k, v in scenario["current_month_spent"].items()}
        recs, _ = recommend_best_card(scenario["user_cards"], scenario["merchant"], scenario["amount"], monthly_spent_dec)
        if not recs:
            status, details, accuracy = "❌ FAIL", "No recommendations", 0
        else:
            top_card = recs[0]
            card_ok = top_card["card_id"] == scenario["expected_winner"]
            reward_ok = abs(top_card["reward_value"] - scenario["expected_reward"]) < 0.02
            if card_ok and reward_ok:
                status, details, accuracy = "✅ PASS", f"✓ Got ₹{top_card['reward_value']:.2f}", 100
            elif card_ok:
                status, details, accuracy = "⚠️ PARTIAL", f"Card OK, Reward Wrong (Got ₹{top_card['reward_value']:.2f})", 75
            else:
                status, details, accuracy = "❌ FAIL", f"Got {top_card['card_name']}, Exp {scenario['expected_winner']}", 0
        results.append({"Test": scenario["description"], "Status": status, "Details": details, "Accuracy": accuracy})
    return results

# --- Streamlit App UI ---

st.title("💳 Smart Credit Card Recommender v3.6")
st.markdown("An intelligent system to find the best credit card for your transaction.")

# Sidebar for Card Selection
with st.sidebar:
    st.header("🗂️ Your Wallet")
    st.write("Select the credit cards you own.")
    user_cards_selection = []
    for cid, cdata in sorted(CREDIT_CARDS_DB.items(), key=lambda item: item[1]['name']):
        if st.checkbox(cdata["name"], key=f"card_{cid}"):
            user_cards_selection.append(cid)
    if 'user_cards' not in st.session_state:
        st.session_state.user_cards = []
    st.session_state.user_cards = user_cards_selection

# Main App with Tabs
tab1, tab2 = st.tabs(["🧠 Recommendation", "🧪 Validation"])

with tab1:
    st.header("Find the Best Card")
    if not st.session_state.user_cards:
        st.warning("Please select at least one credit card from the sidebar to get a recommendation.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            merchant_name = st.text_input("Merchant Name", "Amazon")
        with col2:
            amount = st.number_input("Transaction Amount (₹)", min_value=1, value=5000, step=100)

        if st.button("Get Recommendation", type="primary"):
            monthly_spent = {}
            recommendations, category = recommend_best_card(st.session_state.user_cards, merchant_name, amount, monthly_spent)
            
            st.subheader("🏆 Your Top Cards for this Transaction")
            st.info(f"Detected Category: **{category.title()}**")

            if recommendations:
                for i, rec in enumerate(recommendations):
                    icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                    with st.container(border=True):
                        st.markdown(f"##### {icon} {rec['card_name']}")
                        c1, c2 = st.columns(2)
                        c1.metric("Expected Reward", f"₹{rec['reward_value']:.2f}", help=rec['description'])
                        c2.metric("Annual Fee", f"₹{rec['annual_fee']:,}")
            else:
                st.error("No suitable recommendation found based on your cards and the transaction.")

with tab2:
    st.header("System Accuracy Dashboard")
    st.write("This section runs a suite of 30 predefined tests to check the recommendation logic.")
    if st.button("Run Full Validation Suite"):
        with st.spinner("Running 30 validation tests..."):
            validation_results = run_validation_tests()
            df_results = pd.DataFrame(validation_results)
            st.session_state.validation_results = df_results
    
    if 'validation_results' in st.session_state and st.session_state.validation_results is not None:
        df = st.session_state.validation_results
        st.dataframe(df)
        
        avg_accuracy = df['Accuracy'].mean()
        st.metric("Overall Accuracy", f"{avg_accuracy:.1f}%")

        if avg_accuracy >= 85:
            st.success("🎉 TARGET ACHIEVED! System is operating at high accuracy.")
        else:
            st.error(f"❌ TARGET NOT MET. Further debugging is required. Current accuracy is {avg_accuracy:.1f}%.")
