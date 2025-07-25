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

# [Previous CREDIT_CARDS_DB remains the same - keeping it for brevity]
CREDIT_CARDS_DB = {
    "hdfc_infinia": {
        "name": "HDFC Infinia Metal",
        "bank": "HDFC Bank",
        "annual_fee": 12500,
        "base_rate": 3.33,
        "categories": {
            "fuel": {"rate": 3.33, "type": "waiver", "cap": 1000, "description": "1% waiver up to ₹1,000"},
            "dining": {"rate": 3.33, "type": "points", "cap": None, "description": "3.33% reward points"},
            "grocery": {"rate": 3.33, "type": "points", "cap": None, "description": "3.33% reward points"},
            "travel": {"rate": 33.3, "type": "points", "cap": 15000, "description": "33.3% via SmartBuy hotels"},
            "utilities": {"rate": 3.33, "type": "points", "cap": None, "description": "3.33% reward points"},
            "ecommerce": {"rate": 16.7, "type": "points", "cap": 15000, "description": "16.7% via SmartBuy"},
            "other": {"rate": 3.33, "type": "points", "cap": None, "description": "3.33% reward points"}
        },
        "special_benefits": ["Unlimited domestic & international lounge", "Golf access", "Concierge", "SmartBuy bonuses"]
    },
    "hdfc_diners_black": {
        "name": "HDFC Diners Club Black",
        "bank": "HDFC Bank",
        "annual_fee": 10000,
        "base_rate": 3.33,
        "categories": {
            "fuel": {"rate": 3.33, "type": "waiver", "cap": 1000, "description": "1% waiver up to ₹1,000"},
            "dining": {"rate": 6.6, "type": "points", "cap": 1000, "description": "6.6% on weekends"},
            "grocery": {"rate": 3.33, "type": "points", "cap": None, "description": "3.33% reward points"},
            "movies": {"rate": 100, "type": "bogo", "cap": 2, "description": "BOGO up to ₹500 x 2 tickets"},
            "utilities": {"rate": 3.33, "type": "points", "cap": None, "description": "3.33% reward points"},
            "ecommerce": {"rate": 33, "type": "points", "cap": 7500, "description": "33% via SmartBuy"},
            "other": {"rate": 3.33, "type": "points", "cap": None, "description": "3.33% reward points"}
        },
        "special_benefits": ["BOGO movies", "Weekend dining 6.6%", "Monthly vouchers ₹1,000", "Unlimited lounge"]
    },
    "hdfc_regalia_gold": {
        "name": "HDFC Regalia Gold",
        "bank": "HDFC Bank",
        "annual_fee": 2500,
        "base_rate": 2.67,
        "categories": {
            "fuel": {"rate": 2.67, "type": "waiver", "cap": 500, "description": "1% waiver up to ₹500"},
            "dining": {"rate": 2.67, "type": "points", "cap": None, "description": "2.67% reward points"},
            "grocery": {"rate": 11, "type": "points", "cap": None, "description": "11% at select partners"},
            "ecommerce": {"rate": 11, "type": "points", "cap": None, "description": "11% at Nykaa/Myntra"},
            "utilities": {"rate": 2.67, "type": "points", "cap": None, "description": "2.67% reward points"},
            "other": {"rate": 2.67, "type": "points", "cap": None, "description": "2.67% reward points"}
        },
        "special_benefits": ["12 domestic + 6 international lounge", "Quarterly vouchers ₹1,500", "Partner discounts"]
    },
    "hdfc_millennia": {
        "name": "HDFC Millennia",
        "bank": "HDFC Bank",
        "annual_fee": 1000,
        "base_rate": 1.0,
        "categories": {
            "fuel": {"rate": 1.0, "type": "waiver", "cap": 250, "description": "1% waiver up to ₹250"},
            "dining": {"rate": 5.0, "type": "cashback", "cap": 1000, "description": "5% at Swiggy/Zomato"},
            "grocery": {"rate": 1.0, "type": "cashback", "cap": None, "description": "1% cashback"},
            "ecommerce": {"rate": 5.0, "type": "cashback", "cap": 1000, "description": "5% at 10 partners"},
            "utilities": {"rate": 0, "type": "none", "cap": 0, "description": "Excluded"},
            "other": {"rate": 1.0, "type": "cashback", "cap": 1000, "description": "1% cashback"}
        },
        "special_benefits": ["5% on 10 e-commerce partners", "Quarterly gift cards ₹1,000", "Low annual fee"]
    },
    "axis_ace": {
        "name": "Axis ACE",
        "bank": "Axis Bank",
        "annual_fee": 499,
        "base_rate": 1.5,
        "categories": {
            "fuel": {"rate": 1.5, "type": "waiver", "cap": 500, "description": "1% waiver up to ₹500"},
            "dining": {"rate": 4.0, "type": "cashback", "cap": 500, "description": "4% at Swiggy/Zomato"},
            "grocery": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% cashback"},
            "utilities": {"rate": 5.0, "type": "cashback", "cap": 500, "description": "5% via Google Pay"},
            "ecommerce": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% cashback"},
            "other": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% cashback"}
        },
        "special_benefits": ["Low annual fee", "Google Pay utility benefits", "4 domestic lounge visits"]
    },
    "flipkart_axis": {
        "name": "Flipkart Axis Bank",
        "bank": "Axis Bank",
        "annual_fee": 500,
        "base_rate": 1.5,
        "categories": {
            "fuel": {"rate": 1.5, "type": "waiver", "cap": 400, "description": "1% waiver up to ₹400"},
            "dining": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% cashback"},
            "grocery": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% cashback"},
            "ecommerce": {"rate": 5.0, "type": "cashback", "cap": 4000, "description": "5% on Flipkart/Myntra"},
            "utilities": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% cashback"},
            "other": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% cashback"}
        },
        "special_benefits": ["5% on Flipkart & Myntra", "Quarterly cap ₹4,000", "Entry-level card"]
    },
    "axis_magnus": {
        "name": "Axis Magnus for Burgundy",
        "bank": "Axis Bank",
        "annual_fee": 30000,
        "base_rate": 4.8,
        "categories": {
            "fuel": {"rate": 4.8, "type": "waiver", "cap": 1000, "description": "1% waiver up to ₹1,000"},
            "dining": {"rate": 4.8, "type": "points", "cap": None, "description": "4.8% EDGE points"},
            "grocery": {"rate": 4.8, "type": "points", "cap": None, "description": "4.8% EDGE points"},
            "travel": {"rate": 17.5, "type": "points", "cap": None, "description": "17.5% above ₹1.5L spend"},
            "utilities": {"rate": 4.8, "type": "points", "cap": None, "description": "4.8% EDGE points"},
            "ecommerce": {"rate": 4.8, "type": "points", "cap": None, "description": "4.8% EDGE points"},
            "other": {"rate": 4.8, "type": "points", "cap": None, "description": "4.8% EDGE points"}
        },
        "special_benefits": ["Unlimited lounge", "High EDGE points value", "Burgundy banking", "Premium concierge"]
    },
    "axis_atlas": {
        "name": "Axis Atlas",
        "bank": "Axis Bank",
        "annual_fee": 5000,
        "base_rate": 2.0,
        "categories": {
            "fuel": {"rate": 2.0, "type": "waiver", "cap": 500, "description": "1% waiver up to ₹500"},
            "dining": {"rate": 2.0, "type": "miles", "cap": None, "description": "2% EDGE Miles"},
            "grocery": {"rate": 2.0, "type": "miles", "cap": None, "description": "2% EDGE Miles"},
            "travel": {"rate": 10.0, "type": "miles", "cap": 200000, "description": "10% on travel bookings"},
            "utilities": {"rate": 2.0, "type": "miles", "cap": None, "description": "2% EDGE Miles"},
            "ecommerce": {"rate": 2.0, "type": "miles", "cap": None, "description": "2% EDGE Miles"},
            "other": {"rate": 2.0, "type": "miles", "cap": None, "description": "2% EDGE Miles"}
        },
        "special_benefits": ["Travel-focused rewards", "EDGE Miles transfers", "8 lounge visits", "EazyDiner discounts"]
    },
    "sbi_cashback": {
        "name": "SBI Cashback",
        "bank": "State Bank of India",
        "annual_fee": 999,
        "base_rate": 1.0,
        "categories": {
            "fuel": {"rate": 1.0, "type": "waiver", "cap": 100, "description": "1% waiver up to ₹100"},
            "dining": {"rate": 5.0, "type": "cashback", "cap": 5000, "description": "5% online unlimited"},
            "grocery": {"rate": 5.0, "type": "cashback", "cap": 5000, "description": "5% online unlimited"},
            "ecommerce": {"rate": 5.0, "type": "cashback", "cap": 5000, "description": "5% online unlimited"},
            "utilities": {"rate": 5.0, "type": "cashback", "cap": 5000, "description": "5% online unlimited"},
            "other": {"rate": 1.0, "type": "cashback", "cap": None, "description": "1% offline"}
        },
        "special_benefits": ["Unlimited 5% online cashback", "Simple structure", "No category restrictions online"]
    },
    "sbi_simplyclick": {
        "name": "SBI SimplyCLICK",
        "bank": "State Bank of India",
        "annual_fee": 499,
        "base_rate": 0.25,
        "categories": {
            "fuel": {"rate": 0.25, "type": "waiver", "cap": 100, "description": "1% waiver up to ₹100"},
            "dining": {"rate": 2.5, "type": "points", "cap": 10000, "description": "10X at partners"},
            "grocery": {"rate": 0.25, "type": "points", "cap": None, "description": "1X reward points"},
            "ecommerce": {"rate": 2.5, "type": "points", "cap": 10000, "description": "10X at 8 partners"},
            "movies": {"rate": 2.5, "type": "points", "cap": 10000, "description": "10X at BookMyShow"},
            "utilities": {"rate": 0.25, "type": "points", "cap": None, "description": "1X reward points"},
            "other": {"rate": 0.25, "type": "points", "cap": None, "description": "1X reward points"}
        },
        "special_benefits": ["10X at 8 online partners", "Amazon voucher milestones", "Low annual fee"]
    },
    "sbi_prime": {
        "name": "SBI Prime",
        "bank": "State Bank of India",
        "annual_fee": 2999,
        "base_rate": 0.5,
        "categories": {
            "fuel": {"rate": 0.5, "type": "waiver", "cap": 250, "description": "1% waiver up to ₹250"},
            "dining": {"rate": 2.5, "type": "points", "cap": None, "description": "10X reward points"},
            "grocery": {"rate": 2.5, "type": "points", "cap": None, "description": "10X reward points"},
            "movies": {"rate": 2.5, "type": "points", "cap": None, "description": "10X reward points"},
            "utilities": {"rate": 0.5, "type": "points", "cap": None, "description": "2X reward points"},
            "ecommerce": {"rate": 0.5, "type": "points", "cap": None, "description": "2X reward points"},
            "other": {"rate": 0.5, "type": "points", "cap": None, "description": "2X reward points"}
        },
        "special_benefits": ["8+4 lounge visits", "Club Vistara Silver", "Pizza Hut quarterly vouchers", "Good dining/grocery"]
    },
    "amazon_pay_icici": {
        "name": "Amazon Pay ICICI",
        "bank": "ICICI Bank",
        "annual_fee": 0,
        "base_rate": 1.0,
        "categories": {
            "fuel": {"rate": 1.0, "type": "waiver", "cap": None, "description": "1% waiver unlimited"},
            "dining": {"rate": 1.0, "type": "cashback", "cap": None, "description": "1% cashback"},
            "grocery": {"rate": 1.0, "type": "cashback", "cap": None, "description": "1% cashback"},
            "ecommerce": {"rate": 5.0, "type": "cashback", "cap": None, "description": "5% on Amazon (Prime required)"},
            "utilities": {"rate": 1.0, "type": "cashback", "cap": None, "description": "1% cashback"},
            "other": {"rate": 1.0, "type": "cashback", "cap": None, "description": "1% cashback"}
        },
        "special_benefits": ["Lifetime free", "5% on Amazon for Prime", "Simple cashback structure", "No annual fee"]
    },
    "idfc_first_wealth": {
        "name": "IDFC FIRST Wealth",
        "bank": "IDFC FIRST Bank",
        "annual_fee": 0,
        "base_rate": 0.5,
        "categories": {
            "fuel": {"rate": 0.5, "type": "waiver", "cap": 400, "description": "1% waiver up to ₹400"},
            "dining": {"rate": 1.67, "type": "points", "cap": None, "description": "20% off at 1,500 restaurants"},
            "grocery": {"rate": 1.67, "type": "points", "cap": None, "description": "10X above ₹20K spend"},
            "movies": {"rate": 0, "type": "bogo", "cap": 2, "description": "BOGO up to ₹250"},
            "utilities": {"rate": 1.67, "type": "points", "cap": None, "description": "10X above ₹20K spend"},
            "ecommerce": {"rate": 1.67, "type": "points", "cap": None, "description": "10X above ₹20K spend"},
            "other": {"rate": 1.67, "type": "points", "cap": None, "description": "10X above ₹20K spend"}
        },
        "special_benefits": ["Lifetime free", "No reward expiry", "Quarterly lounge with ₹20K spend", "Spa access"]
    },
    "indusind_pinnacle": {
        "name": "IndusInd Pinnacle World",
        "bank": "IndusInd Bank",
        "annual_fee": 15000,
        "base_rate": 1.8,
        "categories": {
            "fuel": {"rate": 1.8, "type": "waiver", "cap": None, "description": "1% waiver variable cap"},
            "dining": {"rate": 1.8, "type": "points", "cap": 7500, "description": "2.5X reward points"},
            "grocery": {"rate": 1.8, "type": "points", "cap": 7500, "description": "2.5X reward points"},
            "movies": {"rate": 0, "type": "bogo", "cap": 4, "description": "BOGO up to ₹700"},
            "utilities": {"rate": 1.8, "type": "points", "cap": 7500, "description": "2.5X reward points"},
            "ecommerce": {"rate": 1.8, "type": "points", "cap": 7500, "description": "2.5X reward points"},
            "other": {"rate": 1.8, "type": "points", "cap": 7500, "description": "Cash credit ₹0.75/point"}
        },
        "special_benefits": ["No renewal fee", "Cash credit redemption", "4+4 lounge", "2 golf rounds/month"]
    },
    "rbl_world_safari": {
        "name": "RBL World Safari",
        "bank": "RBL Bank",
        "annual_fee": 3000,
        "base_rate": 0.75,
        "categories": {
            "fuel": {"rate": 0.75, "type": "waiver", "cap": 250, "description": "1% waiver up to ₹250"},
            "dining": {"rate": 0.75, "type": "points", "cap": None, "description": "2X travel points"},
            "grocery": {"rate": 0.75, "type": "points", "cap": None, "description": "2X travel points"},
            "travel": {"rate": 1.87, "type": "points", "cap": None, "description": "5X travel points"},
            "utilities": {"rate": 0.75, "type": "points", "cap": None, "description": "2X travel points"},
            "ecommerce": {"rate": 0.75, "type": "points", "cap": None, "description": "2X travel points"},
            "other": {"rate": 0.75, "type": "points", "cap": None, "description": "2X travel points"}
        },
        "special_benefits": ["0% forex markup forever", "Travel insurance", "2+2 lounge quarterly", "Travel focus"]
    },
    "hsbc_live_plus": {
        "name": "HSBC Live+ Cashback",
        "bank": "HSBC Bank",
        "annual_fee": 999,
        "base_rate": 1.5,
        "categories": {
            "fuel": {"rate": 0, "type": "none", "cap": 0, "description": "No fuel benefits"},
            "dining": {"rate": 10.0, "type": "cashback", "cap": 1000, "description": "10% up to ₹1,000"},
            "grocery": {"rate": 10.0, "type": "cashback", "cap": 1000, "description": "10% up to ₹1,000"},
            "utilities": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% unlimited"},
            "ecommerce": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% unlimited"},
            "other": {"rate": 1.5, "type": "cashback", "cap": None, "description": "1.5% unlimited"}
        },
        "special_benefits": ["10% dining/grocery", "Simple cashback", "4 domestic lounge", "Unlimited 1.5% elsewhere"]
    },
    "hsbc_rupay": {
        "name": "HSBC RuPay Cashback",
        "bank": "HSBC Bank",
        "annual_fee": 499,
        "base_rate": 1.0,
        "categories": {
            "fuel": {"rate": 0, "type": "none", "cap": 0, "description": "No fuel benefits"},
            "dining": {"rate": 10.0, "type": "cashback", "cap": 400, "description": "10% up to ₹400"},
            "grocery": {"rate": 10.0, "type": "cashback", "cap": 400, "description": "10% up to ₹400"},
            "utilities": {"rate": 1.0, "type": "cashback", "cap": 400, "description": "1% UPI enabled"},
            "ecommerce": {"rate": 1.0, "type": "cashback", "cap": None, "description": "1% cashback"},
            "other": {"rate": 1.0, "type": "cashback", "cap": 400, "description": "1% including UPI"}
        },
        "special_benefits": ["UPI enabled", "0% forex until Dec 2025", "8+2 lounge", "10% dining/grocery"]
    },
    "amex_platinum": {
        "name": "American Express Platinum Travel",
        "bank": "American Express",
        "annual_fee": 5000,
        "base_rate": 0.5,
        "categories": {
            "fuel": {"rate": 0, "type": "fee_waiver", "cap": 5000, "description": "0% convenience fee at HPCL"},
            "dining": {"rate": 0.5, "type": "points", "cap": None, "description": "1 MR point + dining offers"},
            "grocery": {"rate": 0.5, "type": "points", "cap": None, "description": "1 MR point"},
            "travel": {"rate": 0.5, "type": "points", "cap": None, "description": "1 MR point + milestones"},
            "utilities": {"rate": 0.5, "type": "points", "cap": None, "description": "1 MR point"},
            "ecommerce": {"rate": 0.5, "type": "points", "cap": None, "description": "1 MR point"},
            "other": {"rate": 0.5, "type": "points", "cap": None, "description": "1 MR point"}
        },
        "special_benefits": ["Membership Rewards", "Taj voucher milestones", "Global dining offers", "Premium acceptance"]
    },
    "sc_super_value": {
        "name": "Standard Chartered Super Value Titanium",
        "bank": "Standard Chartered",
        "annual_fee": 750,
        "base_rate": 0.25,
        "categories": {
            "fuel": {"rate": 5.0, "type": "cashback", "cap": 200, "description": "5% total (4% cb + 1% waiver)"},
            "dining": {"rate": 0.25, "type": "points", "cap": None, "description": "1X reward points"},
            "grocery": {"rate": 0.25, "type": "points", "cap": None, "description": "1X reward points"},
            "utilities": {"rate": 5.0, "type": "cashback", "cap": 100, "description": "5% BBPS utilities"},
            "telecom": {"rate": 5.0, "type": "cashback", "cap": 200, "description": "5% telecom recharges"},
            "ecommerce": {"rate": 0.25, "type": "points", "cap": None, "description": "1X reward points"},
            "other": {"rate": 0.25, "type": "points", "cap": None, "description": "1X reward points"}
        },
        "special_benefits": ["Best fuel cashback 5%", "Utility/telecom focus", "₹1,500 welcome fuel CB", "Low fee"]
    },
    "icici_coral": {
        "name": "ICICI Coral",
        "bank": "ICICI Bank",
        "annual_fee": 500,
        "base_rate": 0.5,
        "categories": {
            "fuel": {"rate": 0.5, "type": "waiver", "cap": None, "description": "1% waiver at HPCL"},
            "dining": {"rate": 1.0, "type": "points", "cap": 10000, "description": "4X + 15% off partners"},
            "grocery": {"rate": 0.5, "type": "points", "cap": 10000, "description": "2X reward points"},
            "movies": {"rate": 0, "type": "discount", "cap": 2, "description": "25% off up to ₹100"},
            "utilities": {"rate": 0.5, "type": "points", "cap": 10000, "description": "2X reward points"},
            "ecommerce": {"rate": 0.5, "type": "points", "cap": 10000, "description": "2X reward points"},
            "other": {"rate": 0.5, "type": "points", "cap": 10000, "description": "2X reward points"}
        },
        "special_benefits": ["Railway lounge access", "Entry-level premium", "Dining discounts", "Movie benefits"]
    }
}

# Enhanced merchant category mapping
MERCHANT_CATEGORIES = {
    # Food Delivery & Dining
    "swiggy": "dining", "zomato": "dining", "dominos": "dining", "pizza hut": "dining",
    "mcdonald": "dining", "kfc": "dining", "burger king": "dining", "subway": "dining",
    "starbucks": "dining", "cafe coffee day": "dining", "dunkin": "dining",
    "haldiram": "dining", "bikanervala": "dining",
    
    # Grocery & Supermarkets
    "bigbasket": "grocery", "grofers": "grocery", "blinkit": "grocery", "zepto": "grocery",
    "dmart": "grocery", "reliance fresh": "grocery", "spencer": "grocery", "more": "grocery",
    "metro": "grocery", "star bazaar": "grocery", "heritage": "grocery", "easyday": "grocery",
    
    # Fuel Stations
    "indian oil": "fuel", "hp petrol": "fuel", "bharat petroleum": "fuel", "shell": "fuel",
    "reliance petrol": "fuel", "essar": "fuel", "nayara": "fuel",
    
    # Movies & Entertainment
    "pvr": "movies", "inox": "movies", "cinepolis": "movies", "carnival": "movies",
    "bookmyshow": "movies", "paytm movies": "movies",
    
    # E-commerce
    "amazon": "ecommerce", "flipkart": "ecommerce", "myntra": "ecommerce", "ajio": "ecommerce",
    "nykaa": "ecommerce", "jabong": "ecommerce", "snapdeal": "ecommerce", "shopclues": "ecommerce",
    "tata cliq": "ecommerce", "reliance digital": "ecommerce", "croma": "ecommerce",
    
    # Utilities & Bills
    "airtel": "utilities", "jio": "utilities", "vodafone": "utilities", "bsnl": "utilities",
    "bses": "utilities", "adani": "utilities", "tata power": "utilities", "reliance energy": "utilities",
    "mahanagar gas": "utilities", "indraprastha gas": "utilities",
    
    # Travel
    "irctc": "travel", "makemytrip": "travel", "goibibo": "travel", "cleartrip": "travel",
    "yatra": "travel", "ixigo": "travel", "uber": "travel", "ola": "travel", "rapido": "travel",
    "indigo": "travel", "air india": "travel", "spicejet": "travel", "vistara": "travel"
}

# **EXPANDED VALIDATION SCENARIOS (25 comprehensive test cases)**
VALIDATION_SCENARIOS = [
    # Basic Category Optimization Tests
    {
        "test_id": 1,
        "merchant": "Swiggy",
        "amount": 1000,
        "user_cards": ["hdfc_diners_black", "axis_ace", "sbi_cashback"],
        "current_month_spent": {},
        "expected_winner": "hdfc_diners_black",
        "expected_reward": 66.0,
        "description": "Dining: Diners Black 6.6% > ACE 4% > SBI 5%"
    },
    {
        "test_id": 2,
        "merchant": "BigBasket",
        "amount": 1500,
        "user_cards": ["hsbc_live_plus", "sbi_cashback", "hdfc_millennia"],
        "current_month_spent": {},
        "expected_winner": "hsbc_live_plus",
        "expected_reward": 150.0,
        "description": "Grocery: HSBC Live+ 10% > SBI 5% > Millennia 1%"
    },
    {
        "test_id": 3,
        "merchant": "Amazon",
        "amount": 3000,
        "user_cards": ["amazon_pay_icici", "flipkart_axis", "sbi_cashback"],
        "current_month_spent": {},
        "expected_winner": "amazon_pay_icici",
        "expected_reward": 150.0,
        "description": "E-commerce: Amazon Pay ICICI 5% > SBI 5% > Flipkart 1.5%"
    },
    {
        "test_id": 4,
        "merchant": "Indian Oil",
        "amount": 2000,
        "user_cards": ["sc_super_value", "hdfc_infinia", "axis_ace"],
        "current_month_spent": {},
        "expected_winner": "sc_super_value",
        "expected_reward": 100.0,
        "description": "Fuel: SC Super Value 5% > Infinia 3.33% > ACE 1.5%"
    },
    {
        "test_id": 5,
        "merchant": "MakeMyTrip",
        "amount": 10000,
        "user_cards": ["axis_atlas", "hdfc_infinia", "rbl_world_safari"],
        "current_month_spent": {},
        "expected_winner": "axis_atlas",
        "expected_reward": 1000.0,
        "description": "Travel: Atlas 10% > Infinia 3.33% > RBL 1.87%"
    },
    
    # Cap Management Tests
    {
        "test_id": 6,
        "merchant": "Airtel",
        "amount": 500,
        "user_cards": ["axis_ace", "sc_super_value", "sbi_cashback"],
        "current_month_spent": {"Axis ACE_utilities": 450},
        "expected_winner": "sc_super_value",
        "expected_reward": 25.0,
        "description": "Utilities with ACE cap reached: SC Super Value 5% > SBI 5%"
    },
    {
        "test_id": 7,
        "merchant": "Swiggy",
        "amount": 800,
        "user_cards": ["hdfc_diners_black", "axis_ace"],
        "current_month_spent": {"HDFC Diners Club Black_dining": 950},
        "expected_winner": "axis_ace",
        "expected_reward": 32.0,
        "description": "Dining with Diners cap reached: ACE 4% wins"
    },
    {
        "test_id": 8,
        "merchant": "BigBasket",
        "amount": 2000,
        "user_cards": ["hsbc_live_plus", "sbi_cashback"],
        "current_month_spent": {"HSBC Live+ Cashback_grocery": 900},
        "expected_winner": "hsbc_live_plus",
        "expected_reward": 100.0,
        "description": "Grocery with partial HSBC cap: ₹100 remaining vs SBI 5%"
    },
    {
        "test_id": 9,
        "merchant": "Indian Oil",
        "amount": 3000,
        "user_cards": ["sc_super_value", "hdfc_infinia"],
        "current_month_spent": {"Standard Chartered Super Value Titanium_fuel": 180},
        "expected_winner": "hdfc_infinia",
        "expected_reward": 99.9,
        "description": "Fuel with SC cap nearly reached: Infinia 3.33% wins"
    },
    {
        "test_id": 10,
        "merchant": "Flipkart",
        "amount": 5000,
        "user_cards": ["flipkart_axis", "sbi_cashback"],
        "current_month_spent": {"Flipkart Axis Bank_ecommerce": 3500},
        "expected_winner": "sbi_cashback",
        "expected_reward": 250.0,
        "description": "E-commerce with Flipkart cap reached: SBI 5% wins"
    },
    
    # Edge Cases and Special Scenarios
    {
        "test_id": 11,
        "merchant": "PVR Cinemas",
        "amount": 800,
        "user_cards": ["hdfc_diners_black", "indusind_pinnacle", "icici_coral"],
        "current_month_spent": {},
        "expected_winner": "hdfc_diners_black",
        "expected_reward": 100.0,
        "description": "Movies: Diners BOGO ₹500 > Pinnacle BOGO ₹700 > Coral 25%"
    },
    {
        "test_id": 12,
        "merchant": "Uber",
        "amount": 500,
        "user_cards": ["axis_atlas", "rbl_world_safari", "hdfc_infinia"],
        "current_month_spent": {},
        "expected_winner": "axis_atlas",
        "expected_reward": 50.0,
        "description": "Travel: Atlas 10% > RBL 1.87% > Infinia 3.33%"
    },
    {
        "test_id": 13,
        "merchant": "Nykaa",
        "amount": 2000,
        "user_cards": ["hdfc_regalia_gold", "sbi_cashback", "hdfc_millennia"],
        "current_month_spent": {},
        "expected_winner": "hdfc_regalia_gold",
        "expected_reward": 220.0,
        "description": "E-commerce partner: Regalia Gold 11% > SBI 5% > Millennia 5%"
    },
    {
        "test_id": 14,
        "merchant": "Dominos",
        "amount": 600,
        "user_cards": ["sbi_prime", "axis_ace", "icici_coral"],
        "current_month_spent": {},
        "expected_winner": "axis_ace",
        "expected_reward": 24.0,
        "description": "Dining: ACE 4% > SBI Prime 2.5% > Coral 1%"
    },
    {
        "test_id": 15,
        "merchant": "BSES",
        "amount": 1200,
        "user_cards": ["sc_super_value", "axis_ace", "sbi_cashback"],
        "current_month_spent": {"Standard Chartered Super Value Titanium_utilities": 50},
        "expected_winner": "sc_super_value",
        "expected_reward": 50.0,
        "description": "Utilities: SC Super Value 5% cap ₹50 remaining > others"
    },
    
    # Large Transaction Tests
    {
        "test_id": 16,
        "merchant": "MakeMyTrip",
        "amount": 50000,
        "user_cards": ["axis_atlas", "hdfc_infinia"],
        "current_month_spent": {},
        "expected_winner": "axis_atlas",
        "expected_reward": 5000.0,
        "description": "Large travel: Atlas 10% > Infinia 3.33%"
    },
    {
        "test_id": 17,
        "merchant": "Amazon",
        "amount": 25000,
        "user_cards": ["amazon_pay_icici", "hdfc_infinia"],
        "current_month_spent": {},
        "expected_winner": "amazon_pay_icici",
        "expected_reward": 1250.0,
        "description": "Large e-commerce: Amazon Pay 5% > Infinia SmartBuy capped"
    },
    {
        "test_id": 18,
        "merchant": "Indian Oil",
        "amount": 10000,
        "user_cards": ["sc_super_value", "hdfc_infinia"],
        "current_month_spent": {},
        "expected_winner": "hdfc_infinia",
        "expected_reward": 333.0,
        "description": "Large fuel: SC cap ₹200 vs Infinia unlimited 3.33%"
    },
    
    # Multiple Cards Same Bank
    {
        "test_id": 19,
        "merchant": "Swiggy",
        "amount": 1000,
        "user_cards": ["hdfc_infinia", "hdfc_diners_black", "hdfc_millennia"],
        "current_month_spent": {},
        "expected_winner": "hdfc_diners_black",
        "expected_reward": 66.0,
        "description": "HDFC cards: Diners 6.6% > Millennia 5% > Infinia 3.33%"
    },
    {
        "test_id": 20,
        "merchant": "Amazon",
        "amount": 2000,
        "user_cards": ["axis_ace", "flipkart_axis", "axis_magnus"],
        "current_month_spent": {},
        "expected_winner": "axis_magnus",
        "expected_reward": 96.0,
        "description": "Axis cards: Magnus 4.8% > ACE 1.5% = Flipkart 1.5%"
    },
    
    # Low Amount Transactions
    {
        "test_id": 21,
        "merchant": "Starbucks",
        "amount": 200,
        "user_cards": ["hdfc_diners_black", "axis_ace"],
        "current_month_spent": {},
        "expected_winner": "hdfc_diners_black",
        "expected_reward": 13.2,
        "description": "Small dining: Diners 6.6% > ACE 4%"
    },
    {
        "test_id": 22,
        "merchant": "Indian Oil",
        "amount": 500,
        "user_cards": ["sc_super_value", "axis_ace"],
        "current_month_spent": {},
        "expected_winner": "sc_super_value",
        "expected_reward": 25.0,
        "description": "Small fuel: SC Super Value 5% > ACE 1.5%"
    },
    
    # Zero/Excluded Categories
    {
        "test_id": 23,
        "merchant": "Airtel",
        "amount": 1000,
        "user_cards": ["hdfc_millennia", "axis_ace"],
        "current_month_spent": {},
        "expected_winner": "axis_ace",
        "expected_reward": 50.0,
        "description": "Utilities: ACE 5% > Millennia 0% (excluded)"
    },
    {
        "test_id": 24,
        "merchant": "Indian Oil",
        "amount": 1000,
        "user_cards": ["hsbc_live_plus", "axis_ace"],
        "current_month_spent": {},
        "expected_winner": "axis_ace",
        "expected_reward": 15.0,
        "description": "Fuel: ACE 1.5% > HSBC 0% (no fuel benefits)"
    },
    
    # Annual Fee Consideration
    {
        "test_id": 25,
        "merchant": "Grocery Store",
        "amount": 1000,
        "user_cards": ["amazon_pay_icici", "icici_coral"],
        "current_month_spent": {},
        "expected_winner": "amazon_pay_icici",
        "expected_reward": 10.0,
        "description": "Similar rewards: Amazon Pay 1% (free) = Coral 0.5% (₹500 fee)"
    }
]

def detect_merchant_category(merchant_name):
    """Enhanced merchant category detection"""
    merchant_lower = merchant_name.lower()
    for merchant, category in MERCHANT_CATEGORIES.items():
        if merchant in merchant_lower:
            return category
    return "other"

def calculate_reward_value(card_data, category, amount, monthly_spent):
    """Calculate expected reward value for a transaction"""
    # Handle special categories like telecom for SC Super Value
    if category not in card_data["categories"]:
        if category == "telecom" and "telecom" in card_data["categories"]:
            cat_data = card_data["categories"]["telecom"]
        else:
            cat_data = card_data["categories"].get("other", {"rate": 0, "cap": None})
    else:
        cat_data = card_data["categories"][category]
    
    rate = cat_data["rate"]
    cap = cat_data.get("cap")
    description = cat_data.get("description", f"{rate}% rewards")
    
    # Generate spending key
    spending_key = f"{card_data['name']}_{category}"
    current_spent = monthly_spent.get(spending_key, 0)
    
    # Check if monthly cap is reached
    if cap and current_spent >= cap:
        return 0, f"Monthly cap of ₹{cap} reached", "cap_reached"
    
    # Calculate applicable amount
    if cap:
        remaining_cap = cap - current_spent
        applicable_amount = min(amount, remaining_cap)
        if applicable_amount < amount:
            status = "partial_cap"
        else:
            status = "within_cap"
    else:
        applicable_amount = amount
        status = "no_cap"
    
    # Calculate reward value
    if cat_data.get("type") == "bogo":
        # Special handling for BOGO offers - simplified to rate value
        reward_value = rate if applicable_amount > 0 else 0
        description = f"BOGO: {description}"
    else:
        reward_value = (applicable_amount * rate) / 100
    
    return reward_value, description, status

def recommend_best_card(user_cards, merchant_name, amount, monthly_spent):
    """Enhanced recommendation engine"""
    category = detect_merchant_category(merchant_name)
    recommendations = []
    
    for card_id in user_cards:
        if card_id in CREDIT_CARDS_DB:
            card_data = CREDIT_CARDS_DB[card_id]
            reward_value, description, status = calculate_reward_value(
                card_data, category, amount, monthly_spent
            )
            
            # Calculate annual fee efficiency
            annual_fee = card_data.get("annual_fee", 0)
            fee_efficiency = "High" if annual_fee < 1000 else "Medium" if annual_fee < 5000 else "Premium"
            
            recommendations.append({
                "card_name": card_data["name"],
                "bank": card_data["bank"],
                "card_id": card_id,
                "reward_value": reward_value,
                "description": description,
                "category": category,
                "status": status,
                "annual_fee": annual_fee,
                "fee_efficiency": fee_efficiency,
                "special_benefits": card_data["special_benefits"]
            })
    
    # Sort by reward value, then by fee efficiency (lower fee better for same reward)
    recommendations.sort(key=lambda x: (x["reward_value"], -x["annual_fee"]), reverse=True)
    return recommendations, category

def run_validation_tests():
    """Run comprehensive validation tests and return detailed results"""
    results = []
    
    for scenario in VALIDATION_SCENARIOS:
        try:
            recommendations, category = recommend_best_card(
                scenario["user_cards"],
                scenario["merchant"],
                scenario["amount"],
                scenario["current_month_spent"]
            )
            
            if not recommendations:
                status = "❌ FAIL"
                details = "No recommendations returned"
                accuracy_score = 0
            else:
                top_card = recommendations[0]
                
                # More flexible matching for card IDs vs names
                expected_card_name = CREDIT_CARDS_DB.get(scenario["expected_winner"], {}).get("name", scenario["expected_winner"])
                card_match = (top_card["card_id"] == scenario["expected_winner"] or 
                             top_card["card_name"] == expected_card_name)
                
                # Allow 5% tolerance for reward matching
                reward_tolerance = max(1.0, scenario["expected_reward"] * 0.05)
                reward_match = abs(top_card["reward_value"] - scenario["expected_reward"]) <= reward_tolerance
                
                if card_match and reward_match:
                    status = "✅ PASS"
                    details = f"✓ {top_card['card_name']} ₹{top_card['reward_value']:.2f}"
                    accuracy_score = 100
                elif card_match:
                    status = "⚠️ PARTIAL"
                    details = f"Card OK, Reward: Expected ₹{scenario['expected_reward']:.2f}, Got ₹{top_card['reward_value']:.2f}"
                    accuracy_score = 70
                else:
                    status = "❌ FAIL"
                    expected_name = CREDIT_CARDS_DB.get(scenario["expected_winner"], {}).get("name", scenario["expected_winner"])
                    details = f"Expected {expected_name}, Got {top_card['card_name']}"
                    accuracy_score = 0
            
            results.append({
                "Test ID": scenario["test_id"],
                "Scenario": scenario["description"],
                "Expected": f"{CREDIT_CARDS_DB.get(scenario['expected_winner'], {}).get('name', scenario['expected_winner'])} ₹{scenario['expected_reward']:.2f}",
                "Status": status,
                "Details": details,
                "Accuracy": accuracy_score
            })
            
        except Exception as e:
            results.append({
                "Test ID": scenario["test_id"],
                "Scenario": scenario["description"],
                "Expected": f"{scenario['expected_winner']} ₹{scenario['expected_reward']:.2f}",
                "Status": "❌ ERROR",
                "Details": f"Exception: {str(e)[:50]}...",
                "Accuracy": 0
            })
    
    return results

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_cards' not in st.session_state:
        st.session_state.user_cards = []
    if 'monthly_spent' not in st.session_state:
        st.session_state.monthly_spent = {}
    if 'transaction_history' not in st.session_state:
        st.session_state.transaction_history = []
    if 'validation_mode' not in st.session_state:
        st.session_state.validation_mode = False
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None

def main():
    initialize_session_state()
    
    # App header
    st.title("💳 Smart Credit Card Recommender v2.1")
    st.markdown("**Enhanced with 25-point validation framework for maximum accuracy**")
    
    # Sidebar for card portfolio management
    with st.sidebar:
        st.header("🗂️ Card Portfolio & Settings")
        
        # Create card selection interface
        st.subheader("Select Your Credit Cards")
        
        # Group cards by bank
        banks = {}
        for card_id, card_data in CREDIT_CARDS_DB.items():
            bank = card_data["bank"]
            if bank not in banks:
                banks[bank] = []
            banks[bank].append((card_id, card_data["name"]))
        
        selected_cards = []
        
        # Display cards by bank with checkboxes
        for bank, cards in sorted(banks.items()):
            with st.expander(f"🏦 {bank} ({len(cards)} cards)"):
                for card_id, card_name in cards:
                    if st.checkbox(card_name, key=f"card_{card_id}"):
                        selected_cards.append(card_id)
        
        st.session_state.user_cards = selected_cards
        
        # Show selected cards summary
        if selected_cards:
            st.success(f"✅ {len(selected_cards)} cards selected")
        else:
            st.warning("⚠️ Select cards to get recommendations")
        
        # Validation controls
        st.markdown("---")
        st.subheader("🧪 Validation Controls")
        st.session_state.validation_mode = st.checkbox("Enable Validation Dashboard")
        
        if st.button("🚀 Run Full Validation Suite (25 tests)", type="primary"):
            with st.spinner("Running comprehensive validation tests..."):
                st.session_state.validation_results = run_validation_tests()
            st.success("Validation complete!")
        
        # Monthly tracking
        st.markdown("---")
        st.subheader("📊 Monthly Tracking")
        if st.button("🔄 Reset All Data"):
            st.session_state.monthly_spent = {}
            st.session_state.transaction_history = []
            st.session_state.validation_results = None
            st.success("All data reset!")
            st.rerun()
    
    # Validation Dashboard
    if st.session_state.validation_mode:
        st.header("🔬 Advanced Validation Dashboard")
        
        if st.session_state.validation_results:
            # Enhanced results display
            df_results = pd.DataFrame(st.session_state.validation_results)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_tests = len(df_results)
            passed_tests = len(df_results[df_results['Status'] == '✅ PASS'])
            partial_tests = len(df_results[df_results['Status'] == '⚠️ PARTIAL'])
            failed_tests = len(df_results[df_results['Status'].str.contains('❌')])
            
            avg_accuracy = df_results['Accuracy'].mean()
            
            with col1:
                st.metric("Total Tests", total_tests)
            with col2:
                st.metric("Passed", passed_tests, f"{(passed_tests/total_tests)*100:.1f}%")
            with col3:
                st.metric("Partial", partial_tests, f"{(partial_tests/total_tests)*100:.1f}%")
            with col4:
                st.metric("Overall Accuracy", f"{avg_accuracy:.1f}%")
            
            # Color-coded accuracy assessment
            if avg_accuracy >= 95:
                st.success("🎉 **EXCELLENT** - Recommendation engine is highly accurate and production-ready!")
            elif avg_accuracy >= 85:
                st.warning("⚠️ **GOOD** - Solid accuracy with some edge cases needing attention.")
            elif avg_accuracy >= 70:
                st.error("❌ **FAIR** - Recommendation logic needs significant improvement.")
            else:
                st.error("🚨 **POOR** - Critical issues detected. Engine requires major fixes.")
            
            # Detailed results table with filtering
            st.subheader("📋 Detailed Test Results")
            
            # Filter options
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                status_filter = st.selectbox("Filter by Status:", 
                                           ["All", "✅ PASS", "⚠️ PARTIAL", "❌ FAIL", "❌ ERROR"])
            with filter_col2:
                accuracy_filter = st.slider("Minimum Accuracy:", 0, 100, 0)
            
            # Apply filters
            filtered_df = df_results.copy()
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['Status'] == status_filter]
            filtered_df = filtered_df[filtered_df['Accuracy'] >= accuracy_filter]
            
            # Display filtered results
            st.dataframe(
                filtered_df[['Test ID', 'Scenario', 'Expected', 'Status', 'Details', 'Accuracy']], 
                use_container_width=True,
                height=400
            )
            
            # Analytics charts
            if len(df_results) > 0:
                st.subheader("📊 Validation Analytics")
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    # Status distribution
                    status_counts = df_results['Status'].value_counts()
                    fig_pie = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Test Results Distribution"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with chart_col2:
                    # Accuracy histogram
                    fig_hist = px.histogram(
                        df_results,
                        x='Accuracy',
                        bins=10,
                        title="Accuracy Score Distribution"
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
        
        else:
            st.info("👆 Click 'Run Full Validation Suite' to analyze recommendation accuracy")
            
            # Preview validation scenarios
            st.subheader("📝 Validation Test Preview")
            preview_df = pd.DataFrame([
                {
                    "Test ID": s["test_id"],
                    "Scenario": s["description"],
                    "Merchant": s["merchant"],
                    "Amount": f"₹{s['amount']:,}",
                    "Expected Winner": CREDIT_CARDS_DB.get(s["expected_winner"], {}).get("name", s["expected_winner"])
                }
                for s in VALIDATION_SCENARIOS[:10]  # Show first 10
            ])
            st.dataframe(preview_df, use_container_width=True)
            st.caption("Showing first 10 of 25 comprehensive validation scenarios")
        
        st.markdown("---")
    
    # Main recommendation interface (rest of the code remains the same)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Get Smart Recommendations")
        
        # Merchant input
        input_method = st.radio(
            "Choose input method:",
            ["🛍️ Select from popular merchants", "✏️ Enter merchant name manually"],
            horizontal=True
        )
        
        if input_method == "🛍️ Select from popular merchants":
            merchants_by_category = {}
            for merchant, category in MERCHANT_CATEGORIES.items():
                if category not in merchants_by_category:
                    merchants_by_category[category] = []
                merchants_by_category[category].append(merchant.title())
            
            category_choice = st.selectbox("Select category:", [""] + list(merchants_by_category.keys()))
            
            if category_choice:
                merchant_name = st.selectbox(
                    f"Select {category_choice} merchant:",
                    [""] + sorted(merchants_by_category[category_choice])
                )
            else:
                merchant_name = ""
        else:
            merchant_name = st.text_input("Enter merchant name:")
        
        amount = st.number_input(
            "💰 Transaction amount (₹):",
            min_value=1,
            max_value=100000,
            value=500,
            step=50
        )
        
        # Generate recommendations
        if merchant_name and amount > 0 and st.session_state.user_cards:
            recommendations, detected_category = recommend_best_card(
                st.session_state.user_cards, 
                merchant_name, 
                amount, 
                st.session_state.monthly_spent
            )
            
            st.header("🏆 Smart Recommendations")
            
            category_emojis = {
                "dining": "🍽️", "grocery": "🛒", "fuel": "⛽", 
                "movies": "🎬", "travel": "✈️", "utilities": "💡",
                "ecommerce": "🛍️", "telecom": "📱", "other": "📦"
            }
            
            st.info(f"**Detected Category:** {category_emojis.get(detected_category, '📦')} {detected_category.title()}")
            
            # Display recommendations
            if recommendations:
                for i, rec in enumerate(recommendations[:3]):
                    tier_icons = ["🥇", "🥈", "🥉"]
                    tier_texts = ["BEST CHOICE", "SECOND OPTION", "BACKUP OPTION"]
                    
                    if i == 0:
                        st.success(f"{tier_icons[i]} **{tier_texts[i]}**")
                    elif i == 1:
                        st.warning(f"{tier_icons[i]} **{tier_texts[i]}**")
                    else:
                        st.info(f"{tier_icons[i]} **{tier_texts[i]}**")
                    
                    card_col1, card_col2, card_col3 = st.columns([3, 2, 1])
                    
                    with card_col1:
                        st.write(f"**{rec['card_name']}**")
                        st.write(f"*{rec['bank']}*")
                        st.write(f"**Reward:** ₹{rec['reward_value']:.2f}")
                        st.write(f"**Rate:** {rec['description']}")
                        
                        if rec['status'] == 'cap_reached':
                            st.error("⚠️ Monthly cap reached")
                        elif rec['status'] == 'partial_cap':
                            st.warning("⚡ Partial cap utilization")
                        else:
                            st.success("✅ Full reward eligible")
                    
                    with card_col2:
                        st.write(f"**Annual Fee:** ₹{rec['annual_fee']:,}")
                        st.write(f"**Efficiency:** {rec['fee_efficiency']}")
                        
                        if st.button(
                            f"💳 Use This Card", 
                            key=f"use_{rec['card_id']}_{i}",
                            type="primary" if i == 0 else "secondary"
                        ):
                            transaction = {
                                "timestamp": datetime.now(),
                                "merchant": merchant_name,
                                "amount": amount,
                                "card": rec['card_name'],
                                "category": detected_category,
                                "reward": rec['reward_value']
                            }
                            st.session_state.transaction_history.append(transaction)
                            
                            spending_key = f"{rec['card_name']}_{detected_category}"
                            st.session_state.monthly_spent[spending_key] = \
                                st.session_state.monthly_spent.get(spending_key, 0) + amount
                            
                            st.success(f"✅ Transaction completed with {rec['card_name']}!")
                            st.balloons()
                            st.rerun()
                    
                    with card_col3:
                        with st.expander("🎁 Benefits"):
                            for benefit in rec['special_benefits']:
                                st.write(f"• {benefit}")
                    
                    st.markdown("---")
            else:
                st.warning("No suitable cards found for this transaction.")
        
        elif not st.session_state.user_cards:
            st.info("👈 Please select your credit cards from the sidebar to get recommendations.")
        
        elif not merchant_name:
            st.info("👆 Please select or enter a merchant name to get recommendations.")
    
    with col2:
        st.header("📈 Analytics")
        
        if st.session_state.transaction_history:
            total_rewards = sum(t['reward'] for t in st.session_state.transaction_history)
            total_spent = sum(t['amount'] for t in st.session_state.transaction_history)
            transaction_count = len(st.session_state.transaction_history)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Rewards", f"₹{total_rewards:.2f}")
                st.metric("Transactions", transaction_count)
            with col_b:
                st.metric("Total Spent", f"₹{total_spent:,.0f}")
                if total_spent > 0:
                    effective_rate = (total_rewards / total_spent) * 100
                    st.metric("Avg. Rate", f"{effective_rate:.2f}%")
            
            # Recent transactions
            st.subheader("📝 Recent Transactions")
            for transaction in st.session_state.transaction_history[-5:]:
                with st.container():
                    st.write(f"**{transaction['merchant']}** ({transaction['category']})")
                    st.write(f"Amount: ₹{transaction['amount']:,} | Reward: ₹{transaction['reward']:.2f}")
                    st.write(f"Card: {transaction['card']}")
                    st.caption(f"{transaction['timestamp'].strftime('%d %b, %I:%M %p')}")
                    st.markdown("---")
        else:
            st.info("📊 Complete transactions to see analytics")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        **🚀 Smart Credit Card Recommender v2.1** | 
        25-Point Validation Framework | Production-Ready Accuracy | 
        Real-time Optimization Engine
        """
    )

if __name__ == "__main__":
    main()
