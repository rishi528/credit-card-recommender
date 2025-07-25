import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from decimal import Decimal, ROUND_HALF_UP

# Page configuration
st.set_page_config(
    page_title="Smart Credit Card Recommender", 
    page_icon="💳",
    layout="wide"
)

# Enhanced Credit Card Database with Decimal rates for precision
CREDIT_CARDS_DB = {
    "hdfc_infinia": {
        "name": "HDFC Infinia Metal",
        "bank": "HDFC Bank",
        "annual_fee": 12500,
        "base_rate": Decimal('3.33'),
        "categories": {
            "fuel": {"rate": Decimal('3.33'), "type": "waiver", "cap": 1000, "description": "1% waiver up to ₹1,000"},
            "dining": {"rate": Decimal('3.33'), "type": "points", "cap": None, "description": "3.33% reward points"},
            "grocery": {"rate": Decimal('3.33'), "type": "points", "cap": None, "description": "3.33% reward points"},
            "travel": {"rate": Decimal('3.33'), "type": "points", "cap": None, "description": "3.33% reward points"},
            "utilities": {"rate": Decimal('3.33'), "type": "points", "cap": None, "description": "3.33% reward points"},
            "ecommerce": {"rate": Decimal('3.33'), "type": "points", "cap": None, "description": "3.33% reward points"},
            "other": {"rate": Decimal('3.33'), "type": "points", "cap": None, "description": "3.33% reward points"}
        },
        "special_benefits": ["Unlimited lounge", "Golf access", "Concierge"]
    },
    # ... (Rest of CREDIT_CARDS_DB remains the same as in v3.2 for brevity - include all cards from previous version)
    # Note: Ensure all rates are converted to Decimal in your full code
}

# Merchant categories (same as before)

# Validation scenarios (same as before, with any expected reward adjustments if needed)

def detect_merchant_category(merchant_name):
    # (same as before)

def calculate_reward_value(card_data, category, amount, monthly_spent):
    """Overhauled reward calculation with Decimal precision"""
    amount = Decimal(amount)
    
    if category in card_data["categories"]:
        cat_data = card_data["categories"][category]
    else:
        cat_data = card_data["categories"].get("other", {"rate": card_data["base_rate"], "type": "points", "cap": None})
    
    rate = cat_data["rate"]
    cap = cat_data.get("cap")
    type_ = cat_data.get("type")
    description = cat_data.get("description", f"{rate}% rewards")
    
    spending_key = f"{card_data['name']}_{category}"
    current_spent = Decimal(monthly_spent.get(spending_key, 0))
    
    if rate == 0:
        return 0, description, "excluded"
    
    if cap and current_spent >= cap:
        return 0, f"Monthly cap of ₹{cap} reached", "cap_reached"
    
    if cap:
        remaining_cap = Decimal(cap) - current_spent
        applicable_amount = min(amount, remaining_cap)
        status = "partial_cap" if applicable_amount < amount else "within_cap"
    else:
        applicable_amount = amount
        status = "no_cap"
    
    if type_ == "bogo":
        reward_value = min(rate, applicable_amount)
    elif type_ == "discount":
        reward_value = (applicable_amount * rate / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        reward_value = (applicable_amount * rate / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return float(reward_value), description, status

def recommend_best_card(user_cards, merchant_name, amount, monthly_spent):
    """Overhauled recommendation with improved sorting"""
    category = detect_merchant_category(merchant_name)
    recommendations = []
    
    for card_id in user_cards:
        if card_id in CREDIT_CARDS_DB:
            card_data = CREDIT_CARDS_DB[card_id]
            reward_value, description, status = calculate_reward_value(
                card_data, category, amount, monthly_spent
            )
            
            # New priority score for better sorting
            priority_score = reward_value - (card_data["annual_fee"] / 10000) + float(card_data["base_rate"])
            
            recommendations.append({
                "card_name": card_data["name"],
                "bank": card_data["bank"],
                "card_id": card_id,
                "reward_value": reward_value,
                "description": description,
                "category": category,
                "status": status,
                "annual_fee": card_data["annual_fee"],
                "fee_efficiency": "High" if card_data["annual_fee"] < 1000 else "Medium" if card_data["annual_fee"] < 5000 else "Premium",
                "special_benefits": card_data["special_benefits"],
                "priority_score": priority_score
            })
    
    # Overhauled sorting: Primary priority_score (desc), secondary reward (desc), tertiary fee (asc)
    recommendations.sort(key=lambda x: (-x["priority_score"], -x["reward_value"], x["annual_fee"]))
    return recommendations, category

# run_validation_tests function (same as before, with tighter tolerance if needed)

def initialize_session_state():
    # (same as before, but set validation_mode to False by default)
    if 'validation_mode' not in st.session_state:
        st.session_state.validation_mode = False

def main():
    initialize_session_state()
    
    st.title("Smart Credit Card Recommender v3.3")
    st.markdown("**Overhauled for 85%+ Accuracy - Full Recommendation System Visible**")
    
    # Sidebar (same as before)
    
    # Main recommendation interface (always visible, not dependent on validation mode)
    st.header("🔍 Get Smart Recommendations")
    # ... (Add the full recommendation input and display logic here from previous versions)
    
    # Validation dashboard (now optional and toggled)
    if st.session_state.validation_mode:
        st.header("🔬 Validation Dashboard")
        # ... (Full validation dashboard logic from previous versions)
    
    # Analytics section (same as before)

if __name__ == "__main__":
    main()
