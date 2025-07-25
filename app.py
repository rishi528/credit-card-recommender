import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Smart Credit Card Recommender", 
    page_icon="💳",
    layout="wide"
)

# Credit card database
CREDIT_CARDS_DB = {
    "hdfc_infinia": {
        "name": "HDFC Infinia Metal",
        "annual_fee": 12500,
        "base_rate": 3.33,
        "categories": {
            "fuel": {"rate": 3.33, "type": "waiver", "cap": 1000},
            "dining": {"rate": 3.33, "type": "points", "cap": None},
            "grocery": {"rate": 3.33, "type": "points", "cap": None},
            "travel": {"rate": 16.7, "type": "points", "cap": 15000},
            "utilities": {"rate": 3.33, "type": "points", "cap": None},
            "other": {"rate": 3.33, "type": "points", "cap": None}
        },
        "special_benefits": ["Unlimited lounge", "Golf access", "Concierge"]
    },
    "hdfc_diners_black": {
        "name": "HDFC Diners Club Black",
        "annual_fee": 10000,
        "base_rate": 3.33,
        "categories": {
            "fuel": {"rate": 3.33, "type": "waiver", "cap": 1000},
            "dining": {"rate": 6.6, "type": "points", "cap": 1000, "condition": "weekends"},
            "grocery": {"rate": 3.33, "type": "points", "cap": None},
            "movies": {"rate": 0, "type": "bogo", "cap": 2, "value": 500},
            "utilities": {"rate": 3.33, "type": "points", "cap": None},
            "other": {"rate": 3.33, "type": "points", "cap": None}
        },
        "special_benefits": ["BOGO movies", "Weekend dining bonus", "Monthly vouchers"]
    },
    "axis_ace": {
        "name": "Axis ACE",
        "annual_fee": 499,
        "base_rate": 1.5,
        "categories": {
            "fuel": {"rate": 1.5, "type": "waiver", "cap": 500},
            "dining": {"rate": 4.0, "type": "cashback", "cap": 500, "condition": "Swiggy/Zomato"},
            "grocery": {"rate": 1.5, "type": "cashback", "cap": None},
            "utilities": {"rate": 5.0, "type": "cashback", "cap": 500, "condition": "Google Pay"},
            "other": {"rate": 1.5, "type": "cashback", "cap": None}
        },
        "special_benefits": ["Low annual fee", "Good utility cashback"]
    },
    "sbi_cashback": {
        "name": "SBI Cashback",
        "annual_fee": 999,
        "base_rate": 1.0,
        "categories": {
            "fuel": {"rate": 1.0, "type": "waiver", "cap": 100},
            "dining": {"rate": 5.0, "type": "cashback", "cap": 5000, "condition": "online"},
            "grocery": {"rate": 5.0, "type": "cashback", "cap": 5000, "condition": "online"},
            "ecommerce": {"rate": 5.0, "type": "cashback", "cap": 5000},
            "utilities": {"rate": 5.0, "type": "cashback", "cap": 5000, "condition": "online"},
            "other": {"rate": 1.0, "type": "cashback", "cap": None}
        },
        "special_benefits": ["Unlimited online cashback", "Simple structure"]
    },
    "hsbc_live_plus": {
        "name": "HSBC Live+ Cashback",
        "annual_fee": 999,
        "base_rate": 1.5,
        "categories": {
            "dining": {"rate": 10.0, "type": "cashback", "cap": 1000},
            "grocery": {"rate": 10.0, "type": "cashback", "cap": 1000},
            "fuel": {"rate": 0, "type": "none", "cap": 0},
            "utilities": {"rate": 1.5, "type": "cashback", "cap": None},
            "other": {"rate": 1.5, "type": "cashback", "cap": None}
        },
        "special_benefits": ["High dining/grocery cashback", "Simple structure"]
    }
}

# Merchant category mapping
MERCHANT_CATEGORIES = {
    "swiggy": "dining",
    "zomato": "dining", 
    "dominos": "dining",
    "mcdonald": "dining",
    "kfc": "dining",
    "bigbasket": "grocery",
    "dmart": "grocery",
    "reliance fresh": "grocery",
    "spencer": "grocery",
    "indian oil": "fuel",
    "hp petrol": "fuel",
    "shell": "fuel",
    "bpcl": "fuel",
    "pvr": "movies",
    "inox": "movies",
    "bookmyshow": "movies",
    "amazon": "ecommerce",
    "flipkart": "ecommerce",
    "myntra": "ecommerce",
    "airtel": "utilities",
    "jio": "utilities",
    "bses": "utilities",
    "irctc": "travel",
    "makemytrip": "travel",
    "goibibo": "travel"
}

def detect_merchant_category(merchant_name):
    """Detect category from merchant name"""
    merchant_lower = merchant_name.lower()
    for merchant, category in MERCHANT_CATEGORIES.items():
        if merchant in merchant_lower:
            return category
    return "other"

def calculate_reward_value(card_data, category, amount, monthly_spent):
    """Calculate expected reward value for a transaction"""
    if category not in card_data["categories"]:
        category = "other"
    
    cat_data = card_data["categories"][category]
    rate = cat_data["rate"]
    cap = cat_data.get("cap")
    
    # Check if monthly cap is reached
    if cap and monthly_spent.get(f"{card_data['name']}_{category}", 0) >= cap:
        return 0, "Monthly cap reached"
    
    # Calculate applicable amount
    if cap:
        remaining_cap = cap - monthly_spent.get(f"{card_data['name']}_{category}", 0)
        applicable_amount = min(amount, remaining_cap)
    else:
        applicable_amount = amount
    
    reward_value = (applicable_amount * rate) / 100
    
    # Add special benefit info
    condition = cat_data.get("condition", "")
    benefit_type = cat_data.get("type", "points")
    
    return reward_value, f"{rate}% {benefit_type}" + (f" ({condition})" if condition else "")

def recommend_best_card(user_cards, merchant_name, amount, monthly_spent):
    """Main recommendation engine"""
    category = detect_merchant_category(merchant_name)
    recommendations = []
    
    for card_id in user_cards:
        if card_id in CREDIT_CARDS_DB:
            card_data = CREDIT_CARDS_DB[card_id]
            reward_value, description = calculate_reward_value(card_data, category, amount, monthly_spent)
            
            recommendations.append({
                "card_name": card_data["name"],
                "card_id": card_id,
                "reward_value": reward_value,
                "description": description,
                "category": category,
                "special_benefits": card_data["special_benefits"]
            })
    
    # Sort by reward value
    recommendations.sort(key=lambda x: x["reward_value"], reverse=True)
    return recommendations, category

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_cards' not in st.session_state:
        st.session_state.user_cards = []
    if 'monthly_spent' not in st.session_state:
        st.session_state.monthly_spent = {}
    if 'transaction_history' not in st.session_state:
        st.session_state.transaction_history = []

def main():
    initialize_session_state()
    
    # App header
    st.title("💳 Smart Credit Card Recommender")
    st.markdown("**Get personalized card recommendations for maximum rewards**")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Setup")
        
        # Card portfolio management
        st.subheader("Your Credit Cards")
        available_cards = list(CREDIT_CARDS_DB.keys())
        card_names = [CREDIT_CARDS_DB[card]["name"] for card in available_cards]
        
        selected_card_names = st.multiselect(
            "Select your credit cards:",
            card_names,
            default=card_names[:3] if len(card_names) >= 3 else card_names
        )
        
        # Convert names back to IDs
        st.session_state.user_cards = [
            card_id for card_id, card_data in CREDIT_CARDS_DB.items() 
            if card_data["name"] in selected_card_names
        ]
        
        # Monthly spending tracker
        st.subheader("📊 Monthly Spending")
        if st.button("Reset Monthly Spending"):
            st.session_state.monthly_spent = {}
            st.success("Monthly spending reset!")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Transaction Input")
        
        # Mock QR scan interface
        with st.container():
            st.subheader("Scan QR Code (Simulated)")
            
            merchant_input_type = st.radio(
                "Input method:",
                ["Select from common merchants", "Enter merchant name manually"]
            )
            
            if merchant_input_type == "Select from common merchants":
                common_merchants = list(MERCHANT_CATEGORIES.keys())
                merchant_name = st.selectbox(
                    "Select merchant:",
                    [""] + [m.title() for m in common_merchants]
                )
            else:
                merchant_name = st.text_input("Enter merchant name:")
            
            amount = st.number_input(
                "Transaction amount (₹):",
                min_value=1,
                max_value=100000,
                value=500,
                step=10
            )
        
        # Generate recommendations
        if merchant_name and amount > 0 and st.session_state.user_cards:
            recommendations, detected_category = recommend_best_card(
                st.session_state.user_cards, 
                merchant_name, 
                amount, 
                st.session_state.monthly_spent
            )
            
            st.header("🏆 Recommendations")
            
            # Display detected category
            category_emoji = {
                "dining": "🍽️", "grocery": "🛒", "fuel": "⛽", 
                "movies": "🎬", "travel": "✈️", "utilities": "💡",
                "ecommerce": "🛍️", "other": "📱"
            }
            
            st.info(f"**Detected Category:** {category_emoji.get(detected_category, '📱')} {detected_category.title()}")
            
            # Display recommendations
            for i, rec in enumerate(recommendations):
                if i == 0:
                    st.success(f"🥇 **BEST CHOICE:** {rec['card_name']}")
                elif i == 1:
                    st.warning(f"🥈 **SECOND OPTION:** {rec['card_name']}")
                else:
                    st.info(f"🥉 **BACKUP:** {rec['card_name']}")
                
                col_a, col_b, col_c = st.columns([2, 1, 1])
                
                with col_a:
                    st.write(f"**Reward:** ₹{rec['reward_value']:.2f}")
                    st.write(f"**Rate:** {rec['description']}")
                
                with col_b:
                    if st.button(f"Use This Card", key=f"use_{rec['card_id']}_{i}"):
                        # Record transaction
                        transaction = {
                            "timestamp": datetime.now(),
                            "merchant": merchant_name,
                            "amount": amount,
                            "card": rec['card_name'],
                            "category": detected_category,
                            "reward": rec['reward_value']
                        }
                        st.session_state.transaction_history.append(transaction)
                        
                        # Update monthly spending
                        spending_key = f"{rec['card_name']}_{detected_category}"
                        st.session_state.monthly_spent[spending_key] = \
                            st.session_state.monthly_spent.get(spending_key, 0) + amount
                        
                        st.success(f"Transaction completed with {rec['card_name']}!")
                        st.rerun()
                
                with col_c:
                    with st.expander("Benefits"):
                        for benefit in rec['special_benefits']:
                            st.write(f"• {benefit}")
                
                st.markdown("---")
    
    with col2:
        st.header("📈 Analytics")
        
        if st.session_state.transaction_history:
            # Recent transactions
            st.subheader("Recent Transactions")
            recent_transactions = st.session_state.transaction_history[-5:]
            
            for trans in reversed(recent_transactions):
                st.write(f"**{trans['merchant']}** - ₹{trans['amount']}")
                st.write(f"Card: {trans['card']}")
                st.write(f"Reward: ₹{trans['reward']:.2f}")
                st.markdown("---")
            
            # Monthly rewards summary
            st.subheader("Monthly Rewards")
            total_rewards = sum(t['reward'] for t in st.session_state.transaction_history)
            total_spent = sum(t['amount'] for t in st.session_state.transaction_history)
            
            st.metric("Total Rewards Earned", f"₹{total_rewards:.2f}")
            st.metric("Total Amount Spent", f"₹{total_spent:.2f}")
            
            if total_spent > 0:
                effective_rate = (total_rewards / total_spent) * 100
                st.metric("Effective Reward Rate", f"{effective_rate:.2f}%")
            
            # Category-wise spending chart
            if len(st.session_state.transaction_history) > 1:
                df = pd.DataFrame(st.session_state.transaction_history)
                category_spending = df.groupby('category')['amount'].sum()
                
                fig = px.pie(
                    values=category_spending.values, 
                    names=category_spending.index,
                    title="Spending by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("Complete a transaction to see analytics")
    
    # Footer
    st.markdown("---")
    st.markdown("**💡 Tip:** Add your actual credit cards in the sidebar to get personalized recommendations!")

if __name__ == "__main__":
    main()
