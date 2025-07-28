################################################################################
#           ML Credit Card Recommender - Complete Fixed Version 5.3           #
#                          (All Issues Resolved)                              #
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
from sklearn.model_selection import cross_val_score
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG & SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ML Credit Card Recommender", 
    page_icon="🤖",
    layout="wide"
)

# Initialize all session state variables
session_vars = ['trained_model', 'training_metrics', 'validation_metrics', 'test_metrics']
for var in session_vars:
    if var not in st.session_state:
        st.session_state[var] = None

# ──────────────────────────────────────────────────────────────────────────────
#  FEATURE ENGINEERING & ML MODEL
# ──────────────────────────────────────────────────────────────────────────────
def engineer_features(df):
    """Create advanced features for better model performance"""
    df_processed = df.copy()
    spending_cols = ['Dining', 'Grocery', 'Fuel', 'E-commerce', 'Utilities', 'Travel', 'Movies', 'Other']
    
    # Core features
    df_processed['total_spending'] = df_processed[spending_cols].sum(axis=1)
    
    # Ratio features
    for col in spending_cols:
        df_processed[f'{col}_ratio'] = df_processed[col] / (df_processed['total_spending'] + 1)
        df_processed[f'{col}_high'] = (df_processed[col] > 5000).astype(int)
    
    # Statistical features
    df_processed['max_spending_amount'] = df_processed[spending_cols].max(axis=1)
    df_processed['spending_variance'] = df_processed[spending_cols].var(axis=1)
    df_processed['spending_std'] = df_processed[spending_cols].std(axis=1)
    
    # Pattern features
    df_processed['travel_heavy'] = (df_processed['Travel'] > 15000).astype(int)
    df_processed['ecommerce_heavy'] = (df_processed['E-commerce'] > 15000).astype(int)
    df_processed['dining_heavy'] = (df_processed['Dining'] > 5000).astype(int)
    
    # Category encoding
    max_cat_encoder = LabelEncoder()
    df_processed['max_spending_category'] = df_processed[spending_cols].idxmax(axis=1)
    df_processed['max_category_encoded'] = max_cat_encoder.fit_transform(df_processed['max_spending_category'])
    
    return df_processed, max_cat_encoder

class MLRecommender:
    def __init__(self, model_type, hyperparameters, scaler_type='standard'):
        self.model_type = model_type
        self.model = self._create_model(model_type, hyperparameters)
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler() if scaler_type == 'standard' else MinMaxScaler()
        self.feature_columns = None
        
    def _create_model(self, model_type, hyperparameters):
        """Create model with parameter validation"""
        try:
            models = {
                "Random Forest": RandomForestClassifier(**hyperparameters, random_state=42),
                "Gradient Boosting": GradientBoostingClassifier(**hyperparameters, random_state=42),
                "Logistic Regression": LogisticRegression(**hyperparameters, random_state=42),
                "SVM": SVC(**hyperparameters, random_state=42),
                "Decision Tree": DecisionTreeClassifier(**hyperparameters, random_state=42),
                "K-Nearest Neighbors": KNeighborsClassifier(**hyperparameters),
                "Naive Bayes": GaussianNB(**hyperparameters)
            }
            return models[model_type]
        except TypeError as e:
            st.error(f"❌ Parameter error for {model_type}: {str(e)}")
            st.write(f"Received parameters: {hyperparameters}")
            # Return default model as fallback
            if model_type == "Logistic Regression":
                return LogisticRegression(random_state=42, max_iter=2000)
            else:
                raise e
    
    def prepare_data(self, df):
        """Prepare data for training/prediction"""
        df_processed, _ = engineer_features(df)
        
        spending_cols = ['Dining', 'Grocery', 'Fuel', 'E-commerce', 'Utilities', 'Travel', 'Movies', 'Other']
        feature_cols = (spending_cols + 
                       [f'{col}_ratio' for col in spending_cols] + 
                       [f'{col}_high' for col in spending_cols] + 
                       ['total_spending', 'max_spending_amount', 'spending_variance', 
                        'spending_std', 'max_category_encoded', 'travel_heavy', 
                        'ecommerce_heavy', 'dining_heavy'])
        
        X = df_processed[feature_cols]
        y = self.label_encoder.fit_transform(df['recommended_card']) if 'recommended_card' in df.columns else None
        return X, y, feature_cols
    
    def train(self, X_train, y_train):
        """Train the model with bounds checking"""
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        self.feature_columns = X_train.columns.tolist()
        
    def predict(self, X):
        """Make predictions with safety checks"""
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        # Safety check: ensure predictions are within valid range
        n_classes = len(self.label_encoder.classes_)
        predictions = np.clip(predictions, 0, n_classes - 1).astype(int)
        
        return predictions, probabilities
    
    def get_feature_importance(self):
        """Get feature importance for interpretability"""
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            return np.abs(self.model.coef_[0])
        return None

# ──────────────────────────────────────────────────────────────────────────────
#  STREAMLIT UI
# ──────────────────────────────────────────────────────────────────────────────
st.title("🤖 ML Credit Card Recommender")
st.markdown("**Advanced Machine Learning with Hyperparameter Tuning**")

# Sidebar Configuration
with st.sidebar:
    st.header("🎛️ Model Configuration")
    
    # Clear button to reset everything
    if st.button("🔄 Reset Configuration"):
        for key in list(st.session_state.keys()):
            if key.startswith(('trained_', 'hyperparams_')):
                del st.session_state[key]
        st.rerun()
    
    model_type = st.selectbox("ML Algorithm", 
        ["Random Forest", "Gradient Boosting", "Logistic Regression", "SVM", 
         "Decision Tree", "K-Nearest Neighbors", "Naive Bayes"])
    scaler_type = st.selectbox("Feature Scaling", ["standard", "minmax"])
    
    st.subheader("🔧 Hyperparameters")
    
    # FIXED: Clear hyperparameters for each model type to prevent mixing
    hyperparameters = {}
    
    if model_type == "Random Forest":
        hyperparameters = {
            'n_estimators': st.slider("Trees", 10, 500, 100, 10),
            'max_depth': st.slider("Max Depth", 3, 30, 10),
            'min_samples_split': st.slider("Min Split", 2, 20, 5),
            'min_samples_leaf': st.slider("Min Leaf", 1, 10, 2),
            'max_features': st.selectbox("Max Features", ['sqrt', 'log2', 'auto'])
        }
        
    elif model_type == "Gradient Boosting":
        hyperparameters = {
            'n_estimators': st.slider("Boosting Stages", 50, 500, 100, 10),
            'learning_rate': st.slider("Learning Rate", 0.01, 0.3, 0.1, 0.01),
            'max_depth': st.slider("Max Depth", 3, 15, 6),
            'subsample': st.slider("Subsample", 0.5, 1.0, 0.8, 0.1)
        }
        
    elif model_type == "Logistic Regression":
        hyperparameters = {
            'C': st.slider("Regularization (C)", 0.01, 100.0, 1.0, 0.01),
            'penalty': st.selectbox("Penalty", ['l2', 'l1', 'elasticnet', None]),
            'solver': st.selectbox("Solver", ['liblinear', 'lbfgs', 'saga']),
            'max_iter': 2000  # Fixed: Add this to prevent convergence issues
        }
        
    elif model_type == "SVM":
        kernel = st.selectbox("Kernel", ['rbf', 'linear', 'poly', 'sigmoid'])
        hyperparameters = {
            'C': st.slider("C Parameter", 0.1, 100.0, 1.0, 0.1),
            'kernel': kernel,
            'probability': True  # Required for predict_proba
        }
        if kernel == 'rbf':
            hyperparameters['gamma'] = st.selectbox("Gamma", ['scale', 'auto'])
            
    elif model_type == "Decision Tree":
        hyperparameters = {
            'max_depth': st.slider("Max Depth", 3, 30, 10),
            'min_samples_split': st.slider("Min Split", 2, 20, 5),
            'min_samples_leaf': st.slider("Min Leaf", 1, 10, 2),
            'criterion': st.selectbox("Criterion", ['gini', 'entropy'])
        }
        
    elif model_type == "K-Nearest Neighbors":
        hyperparameters = {
            'n_neighbors': st.slider("Neighbors", 3, 50, 5),
            'weights': st.selectbox("Weights", ['uniform', 'distance']),
            'algorithm': st.selectbox("Algorithm", ['auto', 'ball_tree', 'kd_tree', 'brute'])
        }
        
    elif model_type == "Naive Bayes":
        hyperparameters = {
            'var_smoothing': st.slider("Smoothing", 1e-12, 1e-6, 1e-9, 1e-11)
        }

# Main Tabs
tab_data, tab_train, tab_evaluate, tab_predict = st.tabs([
    "📊 Data Upload", "🎯 Training", "📈 Evaluation", "🔮 Predictions"
])

# Data Upload Tab
with tab_data:
    st.header("📊 Upload Datasets")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Training Set")
        train_file = st.file_uploader("Upload Training Data", type=['csv', 'xlsx'], key='train')
        if train_file:
            df = pd.read_excel(train_file) if train_file.name.endswith('.xlsx') else pd.read_csv(train_file)
            st.success(f"✅ Loaded {len(df)} samples")
            st.dataframe(df.head(3), use_container_width=True)
            st.session_state.train_df = df
    
    with col2:
        st.subheader("Validation Set")
        val_file = st.file_uploader("Upload Validation Data", type=['csv', 'xlsx'], key='val')
        if val_file:
            df = pd.read_excel(val_file) if val_file.name.endswith('.xlsx') else pd.read_csv(val_file)
            st.success(f"✅ Loaded {len(df)} samples")
            st.dataframe(df.head(3), use_container_width=True)
            st.session_state.val_df = df
    
    with col3:
        st.subheader("Test Set")
        test_file = st.file_uploader("Upload Test Data", type=['csv', 'xlsx'], key='test')
        if test_file:
            df = pd.read_excel(test_file) if test_file.name.endswith('.xlsx') else pd.read_csv(test_file)
            st.success(f"✅ Loaded {len(df)} samples")
            st.dataframe(df.head(3), use_container_width=True)
            st.session_state.test_df = df

# Training Tab
with tab_train:
    st.header("🎯 Model Training")
    
    if 'train_df' in st.session_state:
        train_data = st.session_state.train_df
        
        # Quick data overview
        col1, col2 = st.columns(2)
        with col1:
            class_dist = train_data['recommended_card'].value_counts()
            fig = px.bar(x=class_dist.index, y=class_dist.values, title="Class Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            spending_cols = ['Dining', 'Grocery', 'Fuel', 'E-commerce', 'Utilities', 'Travel', 'Movies', 'Other']
            avg_spending = train_data[spending_cols].mean()
            fig = px.bar(x=spending_cols, y=avg_spending.values, title="Average Spending")
            st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🚀 Train Model", type="primary"):
            # Data consistency check
            datasets = [train_data]
            if 'val_df' in st.session_state:
                datasets.append(st.session_state.val_df)
            if 'test_df' in st.session_state:
                datasets.append(st.session_state.test_df)
            
            all_labels = set()
            for df in datasets:
                all_labels.update(df['recommended_card'].unique())
            
            train_labels = set(train_data['recommended_card'].unique())
            missing_labels = all_labels - train_labels
            
            if missing_labels:
                st.error(f"❌ Missing labels in training: {missing_labels}")
                st.stop()
            
            with st.spinner(f"Training {model_type}..."):
                try:
                    # Initialize and train
                    recommender = MLRecommender(model_type, hyperparameters, scaler_type)
                    X_train, y_train, feature_cols = recommender.prepare_data(train_data)
                    recommender.train(X_train, y_train)
                    
                    # Evaluate
                    train_pred, train_prob = recommender.predict(X_train)
                    train_accuracy = accuracy_score(y_train, train_pred)
                    train_f1 = f1_score(y_train, train_pred, average='weighted')
                    cv_scores = cross_val_score(recommender.model, recommender.scaler.transform(X_train), y_train, cv=5)
                    
                    # Store results
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
                    
                    st.success("✅ Training completed!")
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Training Accuracy", f"{train_accuracy:.3f}")
                    col2.metric("F1-Score", f"{train_f1:.3f}")
                    col3.metric("CV Score", f"{cv_scores.mean():.3f}")
                    col4.metric("Model", model_type)
                    
                except Exception as e:
                    st.error(f"Training failed: {str(e)}")
    else:
        st.warning("Upload training data first!")

# Evaluation Tab
with tab_evaluate:
    st.header("📈 Model Evaluation")
    
    if st.session_state.trained_model:
        model = st.session_state.trained_model
        metrics = st.session_state.training_metrics
        
        # Feature importance
        if metrics['feature_importance'] is not None:
            importance_df = pd.DataFrame({
                'feature': metrics['feature_names'],
                'importance': metrics['feature_importance']
            }).sort_values('importance', ascending=False).head(15)
            
            fig = px.bar(importance_df, x='importance', y='feature', orientation='h',
                        title="Top 15 Feature Importance")
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Dataset evaluation
        eval_options = []
        if 'val_df' in st.session_state:
            eval_options.append("Validation")
        if 'test_df' in st.session_state:
            eval_options.append("Test")
        
        if eval_options:
            selected = st.selectbox("Choose Dataset", eval_options)
            eval_df = st.session_state[f'{selected.lower()}_df']
            
            if st.button(f"Evaluate on {selected} Set"):
                with st.spinner(f"Evaluating..."):
                    try:
                        X_eval, y_eval, _ = model.prepare_data(eval_df)
                        eval_pred, eval_prob = model.predict(X_eval)
                        
                        accuracy = accuracy_score(y_eval, eval_pred)
                        f1 = f1_score(y_eval, eval_pred, average='weighted')
                        
                        # Store and display results
                        eval_key = f'{selected.lower()}_metrics'
                        st.session_state[eval_key] = {
                            'accuracy': accuracy, 'f1_score': f1,
                            'predictions': eval_pred, 'true_labels': y_eval
                        }
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric(f"{selected} Accuracy", f"{accuracy:.3f}")
                        col2.metric("F1-Score", f"{f1:.3f}")
                        col3.metric("Gap", f"{metrics['train_accuracy'] - accuracy:.3f}")
                        
                        # Confusion matrix
                        cm = confusion_matrix(y_eval, eval_pred)
                        fig, ax = plt.subplots(figsize=(10, 8))
                        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                                   xticklabels=model.label_encoder.classes_,
                                   yticklabels=model.label_encoder.classes_)
                        ax.set_title(f'Confusion Matrix - {selected} Set')
                        plt.xticks(rotation=45)
                        st.pyplot(fig)
                        
                        # Classification report
                        report = classification_report(y_eval, eval_pred, 
                                                     target_names=model.label_encoder.classes_, 
                                                     output_dict=True)
                        st.dataframe(pd.DataFrame(report).transpose().round(3))
                        
                        # FIXED: Prediction confidence distribution
                        try:
                            max_probs = np.max(eval_prob, axis=1)
                            if len(max_probs) > 0:
                                fig = px.histogram(x=max_probs, nbins=30,  # Fixed: Use nbins instead of bins
                                                  title="Distribution of Maximum Prediction Probabilities")
                                fig.update_xaxes(title="Maximum Probability")
                                fig.update_yaxes(title="Count")
                                st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not create probability histogram: {str(e)}")
                        
                    except Exception as e:
                        st.error(f"Evaluation failed: {str(e)}")
    else:
        st.warning("Train a model first!")

# Prediction Tab
with tab_predict:
    st.header("🔮 Make Predictions")
    
    if st.session_state.trained_model:
        st.subheader("Single Prediction")
        
        # Input form
        col1, col2 = st.columns(2)
        with col1:
            dining = st.number_input("Dining (₹)", 0, 50000, 3000, 100)
            grocery = st.number_input("Grocery (₹)", 0, 50000, 5000, 100)
            fuel = st.number_input("Fuel (₹)", 0, 20000, 2000, 100)
            ecommerce = st.number_input("E-commerce (₹)", 0, 50000, 8000, 100)
        with col2:
            utilities = st.number_input("Utilities (₹)", 0, 20000, 3000, 100)
            travel = st.number_input("Travel (₹)", 0, 100000, 15000, 1000)
            movies = st.number_input("Movies (₹)", 0, 10000, 800, 100)
            other = st.number_input("Other (₹)", 0, 50000, 5000, 100)
        
        if st.button("🎯 Get Recommendation"):
            pred_data = pd.DataFrame({
                'user_id': [999], 'Dining': [dining], 'Grocery': [grocery], 'Fuel': [fuel],
                'E-commerce': [ecommerce], 'Utilities': [utilities], 'Travel': [travel],
                'Movies': [movies], 'Other': [other], 'recommended_card': ['PLACEHOLDER']
            })
            
            try:
                X_pred, _, _ = st.session_state.trained_model.prepare_data(pred_data)
                pred, prob = st.session_state.trained_model.predict(X_pred)
                
                # FIXED: Safe recommendation with bounds checking
                n_classes = len(st.session_state.trained_model.label_encoder.classes_)
                if pred[0] < 0 or pred[0] >= n_classes:
                    st.error(f"🚨 Model prediction {pred[0]} is out of valid range [0, {n_classes-1}]")
                    st.write("This indicates a training data issue. Please retrain the model.")
                else:
                    recommended_card = st.session_state.trained_model.label_encoder.inverse_transform(pred)[0]
                    confidence = np.max(prob[0])
                    
                    st.success(f"🎯 **Recommended**: {recommended_card}")
                    st.info(f"🎲 **Confidence**: {confidence:.2%}")
                    
                    # Spending breakdown
                    total = sum([dining, grocery, fuel, ecommerce, utilities, travel, movies, other])
                    categories = ['Dining', 'Grocery', 'Fuel', 'E-commerce', 'Utilities', 'Travel', 'Movies', 'Other']
                    amounts = [dining, grocery, fuel, ecommerce, utilities, travel, movies, other]
                    
                    fig = px.pie(values=amounts, names=categories, title=f"Spending Pattern (₹{total:,})")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Top 3 recommendations
                    top_3_idx = np.argsort(prob[0])[-3:][::-1]
                    # FIXED: Ensure all indices are valid
                    top_3_idx = [idx for idx in top_3_idx if 0 <= idx < n_classes]
                    
                    if len(top_3_idx) > 0:
                        top_3_cards = st.session_state.trained_model.label_encoder.inverse_transform(top_3_idx)
                        
                        st.subheader("🏆 Top 3 Recommendations")
                        for i, (card, conf) in enumerate(zip(top_3_cards, prob[0][top_3_idx])):
                            icon = ["🥇", "🥈", "🥉"][i]
                            st.write(f"{icon} **{card}**: {conf:.2%}")
                    
            except Exception as e:
                st.error(f"❌ Prediction failed: {str(e)}")
                
                # Enhanced debugging
                st.write("**🔍 Debugging Information:**")
                if 'pred' in locals():
                    st.write(f"- Raw prediction: {pred}")
                    st.write(f"- Prediction type: {type(pred[0])}")
                
                if st.session_state.trained_model:
                    classes = st.session_state.trained_model.label_encoder.classes_
                    st.write(f"- Available classes: {list(classes)}")
                    st.write(f"- Valid class indices: 0 to {len(classes)-1}")
                
                st.write("**💡 Suggested Fix:** Retrain the model with consistent data")
                
        # Batch predictions
        st.subheader("📋 Batch Predictions")
        batch_file = st.file_uploader("Upload batch file", type=['csv', 'xlsx'])
        if batch_file and st.button("Process Batch"):
            batch_df = pd.read_excel(batch_file) if batch_file.name.endswith('.xlsx') else pd.read_csv(batch_file)
            
            if 'recommended_card' not in batch_df.columns:
                batch_df['recommended_card'] = 'PLACEHOLDER'
            
            try:
                X_batch, _, _ = st.session_state.trained_model.prepare_data(batch_df)
                batch_pred, batch_prob = st.session_state.trained_model.predict(X_batch)
                
                batch_df['predicted_card'] = st.session_state.trained_model.label_encoder.inverse_transform(batch_pred)
                batch_df['confidence'] = np.max(batch_prob, axis=1)
                
                st.success(f"✅ Processed {len(batch_df)} predictions")
                st.dataframe(batch_df[['user_id', 'predicted_card', 'confidence']])
                
                # Download results
                csv = batch_df.to_csv(index=False)
                st.download_button("📥 Download Results", csv, "predictions.csv", "text/csv")
            except Exception as e:
                st.error(f"Batch processing failed: {str(e)}")
    else:
        st.warning("Train a model first!")

# Performance Summary in Sidebar
if st.session_state.trained_model:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Performance")
    
    if st.session_state.training_metrics:
        metrics = st.session_state.training_metrics
        st.sidebar.metric("Training", f"{metrics['train_accuracy']:.3f}")
    
    if st.session_state.validation_metrics:
        st.sidebar.metric("Validation", f"{st.session_state.validation_metrics['accuracy']:.3f}")
    
    if st.session_state.test_metrics:
        st.sidebar.metric("Test", f"{st.session_state.test_metrics['accuracy']:.3f}")
