################################################################################
#           ML-Based Credit Card Recommender with Hyperparameter Tuning       #
#                    Adapted for Your Spending Pattern Dataset                #
#                               Version 5.1 (January-2025)                    #
################################################################################

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import cross_val_score, train_test_split
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ML Credit Card Recommender", 
    page_icon="🤖",
    layout="wide"
)

# ──────────────────────────────────────────────────────────────────────────────
#  SESSION STATE INITIALIZATION
# ──────────────────────────────────────────────────────────────────────────────
if 'trained_model' not in st.session_state:
    st.session_state.trained_model = None
if 'feature_columns' not in st.session_state:
    st.session_state.feature_columns = None
if 'label_encoder' not in st.session_state:
    st.session_state.label_encoder = None
if 'scaler' not in st.session_state:
    st.session_state.scaler = None
if 'training_metrics' not in st.session_state:
    st.session_state.training_metrics = None
if 'validation_metrics' not in st.session_state:
    st.session_state.validation_metrics = None
if 'test_metrics' not in st.session_state:
    st.session_state.test_metrics = None

# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE ENGINEERING FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
def engineer_features(df):
    """Create advanced features for better model performance"""
    df_processed = df.copy()
    
    # Spending category features
    spending_cols = ['Dining', 'Grocery', 'Fuel', 'E-commerce', 'Utilities', 'Travel', 'Movies', 'Other']
    
    # Total spending
    df_processed['total_spending'] = df_processed[spending_cols].sum(axis=1)
    
    # Category ratios
    for col in spending_cols:
        df_processed[f'{col}_ratio'] = df_processed[col] / (df_processed['total_spending'] + 1)
    
    # Top spending categories
    df_processed['max_spending_category'] = df_processed[spending_cols].idxmax(axis=1)
    df_processed['max_spending_amount'] = df_processed[spending_cols].max(axis=1)
    df_processed['min_spending_amount'] = df_processed[spending_cols].min(axis=1)
    df_processed['spending_variance'] = df_processed[spending_cols].var(axis=1)
    df_processed['spending_std'] = df_processed[spending_cols].std(axis=1)
    
    # Binary features for high spending categories (>5000)
    for col in spending_cols:
        df_processed[f'{col}_high'] = (df_processed[col] > 5000).astype(int)
    
    # Spending patterns
    df_processed['travel_heavy'] = (df_processed['Travel'] > 15000).astype(int)
    df_processed['ecommerce_heavy'] = (df_processed['E-commerce'] > 15000).astype(int)
    df_processed['dining_heavy'] = (df_processed['Dining'] > 5000).astype(int)
    
    # Encode categorical features
    max_cat_encoder = LabelEncoder()
    df_processed['max_category_encoded'] = max_cat_encoder.fit_transform(df_processed['max_spending_category'])
    
    return df_processed, max_cat_encoder

# ──────────────────────────────────────────────────────────────────────────────
#  ML MODEL CLASS
# ──────────────────────────────────────────────────────────────────────────────
class MLRecommender:
    def __init__(self, model_type, hyperparameters, scaler_type='standard'):
        self.model_type = model_type
        self.hyperparameters = hyperparameters
        self.model = self._create_model()
        self.label_encoder = LabelEncoder()
        self.scaler_type = scaler_type
        self.scaler = StandardScaler() if scaler_type == 'standard' else MinMaxScaler()
        self.feature_columns = None
        self.max_cat_encoder = None
        
    def _create_model(self):
        if self.model_type == "Random Forest":
            return RandomForestClassifier(**self.hyperparameters, random_state=42)
        elif self.model_type == "Gradient Boosting":
            return GradientBoostingClassifier(**self.hyperparameters, random_state=42)
        elif self.model_type == "Logistic Regression":
            return LogisticRegression(**self.hyperparameters, random_state=42, max_iter=2000)
        elif self.model_type == "SVM":
            return SVC(**self.hyperparameters, random_state=42, probability=True)
        elif self.model_type == "Decision Tree":
            return DecisionTreeClassifier(**self.hyperparameters, random_state=42)
        elif self.model_type == "K-Nearest Neighbors":
            return KNeighborsClassifier(**self.hyperparameters)
        elif self.model_type == "Naive Bayes":
            return GaussianNB(**self.hyperparameters)
    
    def prepare_data(self, df):
        """Prepare data for training/prediction"""
        df_processed, max_cat_encoder = engineer_features(df)
        self.max_cat_encoder = max_cat_encoder
        
        # Select features for model
        spending_cols = ['Dining', 'Grocery', 'Fuel', 'E-commerce', 'Utilities', 'Travel', 'Movies', 'Other']
        ratio_cols = [f'{col}_ratio' for col in spending_cols]
        high_cols = [f'{col}_high' for col in spending_cols]
        
        feature_cols = spending_cols + ratio_cols + high_cols + [
            'total_spending', 'max_spending_amount', 'min_spending_amount',
            'spending_variance', 'spending_std', 'max_category_encoded',
            'travel_heavy', 'ecommerce_heavy', 'dining_heavy'
        ]
        
        X = df_processed[feature_cols]
        
        if 'recommended_card' in df.columns:
            y = self.label_encoder.fit_transform(df['recommended_card'])
            return X, y, feature_cols
        else:
            return X, None, feature_cols
    
    def train(self, X_train, y_train):
        """Train the model"""
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        self.feature_columns = X_train.columns.tolist()
        
    def predict(self, X):
        """Make predictions"""
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        return predictions, probabilities
    
    def get_feature_importance(self):
        """Get feature importance (for tree-based models)"""
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            return np.abs(self.model.coef_[0])
        else:
            return None

# ──────────────────────────────────────────────────────────────────────────────
#  STREAMLIT UI
# ──────────────────────────────────────────────────────────────────────────────
st.title("🤖 Advanced ML Credit Card Recommender")
st.markdown("**Machine Learning Model with Hyperparameter Tuning for Spending Pattern Analysis**")

# Sidebar for hyperparameters
with st.sidebar:
    st.header("🎛️ Model Configuration")
    
    # Model selection
    model_type = st.selectbox(
        "Choose ML Algorithm",
        ["Random Forest", "Gradient Boosting", "Logistic Regression", "SVM", 
         "Decision Tree", "K-Nearest Neighbors", "Naive Bayes"]
    )
    
    # Scaler selection
    scaler_type = st.selectbox("Feature Scaling", ["standard", "minmax"])
    
    st.subheader("🔧 Hyperparameters")
    
    # Hyperparameter controls based on model type
    hyperparameters = {}
    
    if model_type == "Random Forest":
        hyperparameters['n_estimators'] = st.slider("Number of Trees", 10, 500, 100, 10)
        hyperparameters['max_depth'] = st.slider("Max Depth", 3, 30, 10)
        hyperparameters['min_samples_split'] = st.slider("Min Samples Split", 2, 20, 5)
        hyperparameters['min_samples_leaf'] = st.slider("Min Samples Leaf", 1, 10, 2)
        hyperparameters['max_features'] = st.selectbox("Max Features", ['sqrt', 'log2', 'auto'])
        
    elif model_type == "Gradient Boosting":
        hyperparameters['n_estimators'] = st.slider("Number of Boosting Stages", 50, 500, 100, 10)
        hyperparameters['learning_rate'] = st.slider("Learning Rate", 0.01, 0.3, 0.1, 0.01)
        hyperparameters['max_depth'] = st.slider("Max Depth", 3, 15, 6)
        hyperparameters['subsample'] = st.slider("Subsample", 0.5, 1.0, 0.8, 0.1)
        
    elif model_type == "Logistic Regression":
        hyperparameters['C'] = st.slider("Regularization Strength (C)", 0.01, 100.0, 1.0, 0.01)
        hyperparameters['penalty'] = st.selectbox("Penalty", ['l2', 'l1', 'elasticnet', None])
        hyperparameters['solver'] = st.selectbox("Solver", ['liblinear', 'lbfgs', 'saga'])
        
    elif model_type == "SVM":
        hyperparameters['C'] = st.slider("Regularization Parameter (C)", 0.1, 100.0, 1.0, 0.1)
        hyperparameters['kernel'] = st.selectbox("Kernel", ['rbf', 'linear', 'poly', 'sigmoid'])
        if hyperparameters['kernel'] == 'rbf':
            hyperparameters['gamma'] = st.selectbox("Gamma", ['scale', 'auto'])
            
    elif model_type == "Decision Tree":
        hyperparameters['max_depth'] = st.slider("Max Depth", 3, 30, 10)
        hyperparameters['min_samples_split'] = st.slider("Min Samples Split", 2, 20, 5)
        hyperparameters['min_samples_leaf'] = st.slider("Min Samples Leaf", 1, 10, 2)
        hyperparameters['criterion'] = st.selectbox("Criterion", ['gini', 'entropy'])
        
    elif model_type == "K-Nearest Neighbors":
        hyperparameters['n_neighbors'] = st.slider("Number of Neighbors", 3, 50, 5)
        hyperparameters['weights'] = st.selectbox("Weights", ['uniform', 'distance'])
        hyperparameters['algorithm'] = st.selectbox("Algorithm", ['auto', 'ball_tree', 'kd_tree', 'brute'])
        
    elif model_type == "Naive Bayes":
        hyperparameters['var_smoothing'] = st.slider("Smoothing Parameter", 1e-12, 1e-6, 1e-9, 1e-11)

# Main content area with tabs
tab_data, tab_train, tab_evaluate, tab_predict = st.tabs([
    "📊 Data Upload", "🎯 Model Training", "📈 Model Evaluation", "🔮 Make Predictions"
])

# Data Upload Tab
with tab_data:
    st.header("📊 Upload Your Datasets")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Training Set")
        train_file = st.file_uploader("Upload Training Data", type=['csv', 'xlsx'], key='train')
        if train_file:
            if train_file.name.endswith('.xlsx'):
                train_df = pd.read_excel(train_file)
            else:
                train_df = pd.read_csv(train_file)
            st.success(f"✅ Loaded {len(train_df)} training samples")
            st.dataframe(train_df.head(), use_container_width=True)
            st.session_state.train_df = train_df
    
    with col2:
        st.subheader("Validation Set")
        val_file = st.file_uploader("Upload Validation Data", type=['csv', 'xlsx'], key='val')
        if val_file:
            if val_file.name.endswith('.xlsx'):
                val_df = pd.read_excel(val_file)
            else:
                val_df = pd.read_csv(val_file)
            st.success(f"✅ Loaded {len(val_df)} validation samples")
            st.dataframe(val_df.head(), use_container_width=True)
            st.session_state.val_df = val_df
    
    with col3:
        st.subheader("Test Set")
        test_file = st.file_uploader("Upload Test Data", type=['csv', 'xlsx'], key='test')
        if test_file:
            if test_file.name.endswith('.xlsx'):
                test_df = pd.read_excel(test_file)
            else:
                test_df = pd.read_csv(test_file)
            st.success(f"✅ Loaded {len(test_df)} test samples")
            st.dataframe(test_df.head(), use_container_width=True)
            st.session_state.test_df = test_df

# Model Training Tab
with tab_train:
    st.header("🎯 Model Training & Optimization")
    
    if 'train_df' in st.session_state:
        # Data overview
        train_data = st.session_state.train_df
        st.info(f"Training on {len(train_data)} samples with {model_type} algorithm")
        
        # Display class distribution
        col1, col2 = st.columns(2)
        with col1:
            class_dist = train_data['recommended_card'].value_counts()
            fig = px.bar(x=class_dist.index, y=class_dist.values, 
                        title="Class Distribution in Training Data")
            fig.update_xaxes(title="Credit Card")
            fig.update_yaxes(title="Count")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Spending distribution
            spending_cols = ['Dining', 'Grocery', 'Fuel', 'E-commerce', 'Utilities', 'Travel', 'Movies', 'Other']
            avg_spending = train_data[spending_cols].mean()
            fig = px.bar(x=spending_cols, y=avg_spending.values, 
                        title="Average Spending by Category")
            fig.update_xaxes(title="Category")
            fig.update_yaxes(title="Average Amount")
            st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🚀 Train Model", type="primary"):
            with st.spinner(f"Training {model_type} model..."):
                try:
                    # Initialize model
                    recommender = MLRecommender(model_type, hyperparameters, scaler_type)
                    
                    # Prepare training data
                    X_train, y_train, feature_cols = recommender.prepare_data(train_data)
                    
                    # Train model
                    recommender.train(X_train, y_train)
                    
                    # Calculate training accuracy
                    train_pred, train_prob = recommender.predict(X_train)
                    train_accuracy = accuracy_score(y_train, train_pred)
                    train_f1 = f1_score(y_train, train_pred, average='weighted')
                    
                    # Cross-validation score
                    cv_scores = cross_val_score(recommender.model, 
                                              recommender.scaler.transform(X_train), 
                                              y_train, cv=5, scoring='accuracy')
                    
                    # Store in session state
                    st.session_state.trained_model = recommender
                    st.session_state.training_metrics = {
                        'train_accuracy': train_accuracy,
                        'train_f1': train_f1,
                        'cv_mean': cv_scores.mean(),
                        'cv_std': cv_scores.std(),
                        'feature_importance': recommender.get_feature_importance(),
                        'feature_names': feature_cols,
                        'class_names': recommender.label_encoder.classes_
                    }
                    
                    st.success("✅ Model trained successfully!")
                    
                    # Display training metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Training Accuracy", f"{train_accuracy:.3f}")
                    col2.metric("Training F1-Score", f"{train_f1:.3f}")
                    col3.metric("CV Score", f"{cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
                    col4.metric("Model Type", model_type)
                    
                except Exception as e:
                    st.error(f"Training failed: {str(e)}")
    else:
        st.warning("Please upload training data first!")

# Model Evaluation Tab
with tab_evaluate:
    st.header("📈 Comprehensive Model Evaluation")
    
    if st.session_state.trained_model is not None:
        model = st.session_state.trained_model
        metrics = st.session_state.training_metrics
        
        # Feature Importance Plot
        if metrics['feature_importance'] is not None:
            st.subheader("🎯 Feature Importance Analysis")
            
            importance_df = pd.DataFrame({
                'feature': metrics['feature_names'],
                'importance': metrics['feature_importance']
            }).sort_values('importance', ascending=False)
            
            # Top features
            top_features = importance_df.head(20)
            fig = px.bar(top_features, x='importance', y='feature', 
                        orientation='h',
                        title="Top 20 Most Important Features")
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance on different datasets
        evaluation_options = []
        if 'val_df' in st.session_state:
            evaluation_options.append("Validation Set")
        if 'test_df' in st.session_state:
            evaluation_options.append("Test Set")
        
        if evaluation_options:
            selected_eval = st.selectbox("Choose Dataset for Evaluation", evaluation_options)
            
            if selected_eval == "Validation Set" and 'val_df' in st.session_state:
                eval_df = st.session_state.val_df
                eval_type = "Validation"
            elif selected_eval == "Test Set" and 'test_df' in st.session_state:
                eval_df = st.session_state.test_df
                eval_type = "Test"
            
            if st.button(f"Evaluate on {eval_type} Set"):
                with st.spinner(f"Evaluating on {eval_type.lower()} set..."):
                    X_eval, y_eval, _ = model.prepare_data(eval_df)
                    eval_pred, eval_prob = model.predict(X_eval)
                    
                    eval_accuracy = accuracy_score(y_eval, eval_pred)
                    eval_f1 = f1_score(y_eval, eval_pred, average='weighted')
                    
                    # Store metrics
                    eval_metrics = {
                        'accuracy': eval_accuracy,
                        'f1_score': eval_f1,
                        'predictions': eval_pred,
                        'probabilities': eval_prob,
                        'true_labels': y_eval
                    }
                    
                    if eval_type == "Validation":
                        st.session_state.validation_metrics = eval_metrics
                    else:
                        st.session_state.test_metrics = eval_metrics
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric(f"{eval_type} Accuracy", f"{eval_accuracy:.3f}")
                    col2.metric(f"{eval_type} F1-Score", f"{eval_f1:.3f}")
                    col3.metric("Generalization Gap", f"{metrics['train_accuracy'] - eval_accuracy:.3f}")
                    
                    # Confusion Matrix
                    cm = confusion_matrix(y_eval, eval_pred)
                    fig, ax = plt.subplots(figsize=(12, 8))
                    
                    class_names = model.label_encoder.classes_
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                               xticklabels=class_names, yticklabels=class_names)
                    ax.set_title(f'Confusion Matrix - {eval_type} Set')
                    ax.set_ylabel('Actual')
                    ax.set_xlabel('Predicted')
                    plt.xticks(rotation=45)
                    plt.yticks(rotation=0)
                    st.pyplot(fig)
                    
                    # Classification Report
                    st.subheader("📊 Detailed Classification Report")
                    report = classification_report(y_eval, eval_pred, 
                                                 target_names=class_names, 
                                                 output_dict=True)
                    report_df = pd.DataFrame(report).transpose()
                    st.dataframe(report_df.round(3), use_container_width=True)
                    
                    # Prediction confidence distribution
                    st.subheader("🎲 Prediction Confidence Distribution")
                    max_probs = np.max(eval_prob, axis=1)
                    fig = px.histogram(x=max_probs, nbins=30, 
                                      title="Distribution of Maximum Prediction Probabilities")
                    fig.update_xaxes(title="Maximum Probability")
                    fig.update_yaxes(title="Count")
                    st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning("Please train a model first!")

# Prediction Tab
with tab_predict:
    st.header("🔮 Real-time Spending Pattern Predictions")
    
    if st.session_state.trained_model is not None:
        st.subheader("Single User Prediction")
        
        # Create input form for spending categories
        col1, col2 = st.columns(2)
        
        with col1:
            dining = st.number_input("Dining Spending (₹)", min_value=0, value=3000, step=100)
            grocery = st.number_input("Grocery Spending (₹)", min_value=0, value=5000, step=100)
            fuel = st.number_input("Fuel Spending (₹)", min_value=0, value=2000, step=100)
            ecommerce = st.number_input("E-commerce Spending (₹)", min_value=0, value=8000, step=100)
        
        with col2:
            utilities = st.number_input("Utilities Spending (₹)", min_value=0, value=3000, step=100)
            travel = st.number_input("Travel Spending (₹)", min_value=0, value=15000, step=100)
            movies = st.number_input("Movies Spending (₹)", min_value=0, value=800, step=100)
            other = st.number_input("Other Spending (₹)", min_value=0, value=5000, step=100)
        
        if st.button("🎯 Get Credit Card Recommendation"):
            # Create prediction data
            pred_data = pd.DataFrame({
                'user_id': [999],
                'Dining': [dining],
                'Grocery': [grocery],
                'Fuel': [fuel],
                'E-commerce': [ecommerce],
                'Utilities': [utilities],
                'Travel': [travel],
                'Movies': [movies],
                'Other': [other],
                'recommended_card': ['Unknown']  # Placeholder
            })
            
            # Make prediction
            X_pred, _, _ = st.session_state.trained_model.prepare_data(pred_data)
            pred, prob = st.session_state.trained_model.predict(X_pred)
            
            # Get card name
            recommended_card = st.session_state.trained_model.label_encoder.inverse_transform(pred)[0]
            confidence = np.max(prob[0])
            
            # Display result
            st.success(f"🎯 **Recommended Credit Card**: {recommended_card}")
            st.info(f"🎲 **Confidence**: {confidence:.2%}")
            
            # Show spending pattern analysis
            total_spending = sum([dining, grocery, fuel, ecommerce, utilities, travel, movies, other])
            st.write("### 📊 Your Spending Pattern Analysis")
            
            spending_breakdown = {
                'Category': ['Dining', 'Grocery', 'Fuel', 'E-commerce', 'Utilities', 'Travel', 'Movies', 'Other'],
                'Amount': [dining, grocery, fuel, ecommerce, utilities, travel, movies, other],
                'Percentage': [x/total_spending*100 for x in [dining, grocery, fuel, ecommerce, utilities, travel, movies, other]]
            }
            breakdown_df = pd.DataFrame(spending_breakdown)
            
            fig = px.pie(breakdown_df, values='Amount', names='Category', 
                        title=f"Your Spending Distribution (Total: ₹{total_spending:,})")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top 3 predictions
            top_3_idx = np.argsort(prob[0])[-3:][::-1]
            top_3_cards = st.session_state.trained_model.label_encoder.inverse_transform(top_3_idx)
            top_3_prob = prob[0][top_3_idx]
            
            st.subheader("🏆 Top 3 Credit Card Recommendations")
            for i, (card, conf) in enumerate(zip(top_3_cards, top_3_prob)):
                icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                st.write(f"{icon} **{card}**: {conf:.2%} confidence")
        
        # Batch prediction option
        st.subheader("📋 Batch Predictions")
        batch_file = st.file_uploader("Upload file for batch predictions", type=['csv', 'xlsx'])
        if batch_file:
            if batch_file.name.endswith('.xlsx'):
                batch_df = pd.read_excel(batch_file)
            else:
                batch_df = pd.read_csv(batch_file)
            
            if st.button("Run Batch Predictions"):
                with st.spinner("Processing batch predictions..."):
                    # Add placeholder recommended_card column if not present
                    if 'recommended_card' not in batch_df.columns:
                        batch_df['recommended_card'] = 'Unknown'
                    
                    X_batch, _, _ = st.session_state.trained_model.prepare_data(batch_df)
                    batch_pred, batch_prob = st.session_state.trained_model.predict(X_batch)
                    
                    # Add predictions to dataframe
                    batch_df['predicted_card'] = st.session_state.trained_model.label_encoder.inverse_transform(batch_pred)
                    batch_df['confidence'] = np.max(batch_prob, axis=1)
                    
                    st.success(f"✅ Completed predictions for {len(batch_df)} users")
                    st.dataframe(batch_df[['user_id', 'predicted_card', 'confidence']], use_container_width=True)
                    
                    # Download button for results
                    csv = batch_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Predictions",
                        data=csv,
                        file_name="credit_card_predictions.csv",
                        mime="text/csv"
                    )
    else:
        st.warning("Please train a model first!")

# Performance Summary Sidebar
if st.session_state.trained_model is not None:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Model Performance Summary")
    
    if st.session_state.training_metrics:
        metrics = st.session_state.training_metrics
        st.sidebar.metric("Training Accuracy", f"{metrics['train_accuracy']:.3f}")
        st.sidebar.metric("CV Score", f"{metrics['cv_mean']:.3f}")
    
    if st.session_state.validation_metrics:
        val_metrics = st.session_state.validation_metrics
        st.sidebar.metric("Validation Accuracy", f"{val_metrics['accuracy']:.3f}")
    
    if st.session_state.test_metrics:
        test_metrics = st.session_state.test_metrics
        st.sidebar.metric("Test Accuracy", f"{test_metrics['accuracy']:.3f}")
