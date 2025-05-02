import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

class IsolationForestModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    def detect(self, data, threshold=0.5):
        """
        Detect anomalies using Isolation Forest
        
        Parameters:
        data (pd.DataFrame): Input data
        threshold (float): Threshold for anomaly detection (0.0-1.0)
        
        Returns:
        tuple: (results DataFrame, metrics dictionary)
        """
        # Select numerical columns for anomaly detection
        numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
        X = data[numeric_cols]
        
        # Scale the data
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit the model
        self.model = IsolationForest(
            contamination=threshold,
            random_state=42
        )
        
        # Predict anomalies
        # Isolation Forest returns -1 for outliers and 1 for inliers
        y_pred = self.model.fit_predict(X_scaled)
        anomaly_scores = self.model.decision_function(X_scaled)
        
        # Convert to 0 for normal, 1 for anomaly
        anomalies = np.where(y_pred == -1, 1, 0)
        
        # Add results to dataframe
        results = data.copy()
        results['anomaly'] = anomalies
        results['anomaly_score'] = 1 - (anomaly_scores + 0.5)  # Transform to 0-1 scale
        
        # Calculate some mock metrics (since we don't have true labels)
        # In a real scenario, you would use labeled data for evaluation
        anomaly_count = np.sum(anomalies)
        anomaly_percent = (anomaly_count / len(data)) * 100
        
        # Generate evaluation metrics based on synthetic ground truth for demonstration
        # In a real-world scenario, you would use actual labeled data
        # This is a simplified approach for educational purposes
        
        # Create synthetic ground truth based on extreme values
        # (assuming outliers are 10% of highest/lowest values in key features)
        if len(numeric_cols) > 0:
            ground_truth = np.zeros(len(data))
            
            # For each numerical column, mark extreme values as anomalies
            for col in numeric_cols[:3]:  # Use at most 3 columns
                values = data[col].values
                sorted_values = np.sort(values)
                
                # Mark highest and lowest 5% as potential anomalies
                low_threshold = sorted_values[int(len(sorted_values) * 0.05)]
                high_threshold = sorted_values[int(len(sorted_values) * 0.95)]
                
                # Mark values outside these thresholds
                col_anomalies = ((values <= low_threshold) | (values >= high_threshold)).astype(int)
                ground_truth = np.logical_or(ground_truth, col_anomalies).astype(int)
        else:
            # If no numerical columns, create random ground truth
            ground_truth = np.random.choice([0, 1], size=len(data), p=[0.9, 0.1])
        
        # Calculate performance metrics
        tn, fp, fn, tp = confusion_matrix(ground_truth, anomalies, labels=[0, 1]).ravel()
        
        # Calculate metrics (handle division by zero)
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics = {
            'model_name': 'Isolation Forest',
            'anomaly_count': int(anomaly_count),
            'total_records': len(data),
            'anomaly_percent': float(anomaly_percent),
            'threshold_used': float(threshold),
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'true_positives': int(tp),
            'false_positives': int(fp),
            'true_negatives': int(tn),
            'false_negatives': int(fn)
        }
        
        return results, metrics

class AutoEncoderModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.history = None
    
    def _build_model(self, input_dim):
        """Build autoencoder model architecture"""
        # Encoder
        input_layer = Input(shape=(input_dim,))
        encoder = Dense(int(input_dim * 0.75), activation="relu")(input_layer)
        encoder = Dense(int(input_dim * 0.5), activation="relu")(encoder)
        encoder = Dense(int(input_dim * 0.33), activation="relu")(encoder)
        
        # Decoder
        decoder = Dense(int(input_dim * 0.5), activation="relu")(encoder)
        decoder = Dense(int(input_dim * 0.75), activation="relu")(decoder)
        decoder = Dense(input_dim, activation="linear")(decoder)
        
        # Autoencoder model
        autoencoder = Model(inputs=input_layer, outputs=decoder)
        autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss="mse")
        
        return autoencoder
    
    def detect(self, data, threshold=0.5):
        """
        Detect anomalies using Autoencoder
        
        Parameters:
        data (pd.DataFrame): Input data
        threshold (float): Threshold for anomaly detection (0.0-1.0)
        
        Returns:
        tuple: (results DataFrame, metrics dictionary)
        """
        # Select numerical columns for anomaly detection
        numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
        X = data[numeric_cols]
        
        # Scale the data
        X_scaled = self.scaler.fit_transform(X)
        
        # Build and train the autoencoder
        self.model = self._build_model(X_scaled.shape[1])
        
        # Train the model
        self.history = self.model.fit(
            X_scaled, X_scaled,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        # Get reconstruction error
        predictions = self.model.predict(X_scaled, verbose=0)
        mse = np.mean(np.power(X_scaled - predictions, 2), axis=1)
        
        # Determine threshold for anomaly detection
        # We use the percentile method based on the user's threshold
        mse_threshold = np.percentile(mse, 100 * (1 - threshold))
        
        # Detect anomalies
        anomalies = (mse > mse_threshold).astype(int)
        
        # Normalize scores to 0-1 range
        max_score = np.max(mse)
        min_score = np.min(mse)
        normalized_scores = (mse - min_score) / (max_score - min_score)
        
        # Add results to dataframe
        results = data.copy()
        results['anomaly'] = anomalies
        results['anomaly_score'] = normalized_scores
        
        # Calculate metrics
        anomaly_count = np.sum(anomalies)
        anomaly_percent = (anomaly_count / len(data)) * 100
        
        # Generate evaluation metrics based on synthetic ground truth for demonstration
        # In a real-world scenario, you would use actual labeled data
        if len(numeric_cols) > 0:
            ground_truth = np.zeros(len(data))
            
            # For each numerical column, mark extreme values as anomalies
            for col in numeric_cols[:3]:  # Use at most 3 columns
                values = data[col].values
                sorted_values = np.sort(values)
                
                # Mark highest and lowest 5% as potential anomalies
                low_threshold = sorted_values[int(len(sorted_values) * 0.05)]
                high_threshold = sorted_values[int(len(sorted_values) * 0.95)]
                
                # Mark values outside these thresholds
                col_anomalies = ((values <= low_threshold) | (values >= high_threshold)).astype(int)
                ground_truth = np.logical_or(ground_truth, col_anomalies).astype(int)
        else:
            # If no numerical columns, create random ground truth
            ground_truth = np.random.choice([0, 1], size=len(data), p=[0.9, 0.1])
        
        # Calculate performance metrics
        tn, fp, fn, tp = confusion_matrix(ground_truth, anomalies, labels=[0, 1]).ravel()
        
        # Calculate metrics (handle division by zero)
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics = {
            'model_name': 'Autoencoder',
            'anomaly_count': int(anomaly_count),
            'total_records': len(data),
            'anomaly_percent': float(anomaly_percent),
            'threshold_used': float(threshold),
            'training_loss': float(self.history.history['loss'][-1]),
            'validation_loss': float(self.history.history['val_loss'][-1]) if 'val_loss' in self.history.history else None,
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'true_positives': int(tp),
            'false_positives': int(fp),
            'true_negatives': int(tn),
            'false_negatives': int(fn)
        }
        
        return results, metrics

class KMeansModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    def detect(self, data, threshold=0.5):
        """
        Detect anomalies using K-Means Clustering
        
        Parameters:
        data (pd.DataFrame): Input data
        threshold (float): Threshold for anomaly detection (0.0-1.0)
        
        Returns:
        tuple: (results DataFrame, metrics dictionary)
        """
        # Select numerical columns for anomaly detection
        numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
        X = data[numeric_cols]
        
        # Scale the data
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit K-Means model (we'll use 3 clusters as a starting point)
        n_clusters = 3
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = self.model.fit_predict(X_scaled)
        
        # Calculate distance to cluster centers
        distances = np.zeros(X_scaled.shape[0])
        for i in range(X_scaled.shape[0]):
            cluster_center = self.model.cluster_centers_[clusters[i]]
            distances[i] = np.linalg.norm(X_scaled[i] - cluster_center)
        
        # Normalize distances to 0-1 range
        max_dist = np.max(distances)
        min_dist = np.min(distances)
        normalized_distances = (distances - min_dist) / (max_dist - min_dist)
        
        # Determine threshold for anomaly detection
        distance_threshold = np.percentile(normalized_distances, 100 * (1 - threshold))
        
        # Detect anomalies
        anomalies = (normalized_distances > distance_threshold).astype(int)
        
        # Add results to dataframe
        results = data.copy()
        results['anomaly'] = anomalies
        results['anomaly_score'] = normalized_distances
        results['cluster'] = clusters
        
        # Calculate metrics
        anomaly_count = np.sum(anomalies)
        anomaly_percent = (anomaly_count / len(data)) * 100
        
        # Calculate cluster distributions
        cluster_counts = np.bincount(clusters, minlength=n_clusters)
        cluster_percents = (cluster_counts / len(data)) * 100
        
        # Generate evaluation metrics based on synthetic ground truth for demonstration
        # In a real-world scenario, you would use actual labeled data
        if len(numeric_cols) > 0:
            ground_truth = np.zeros(len(data))
            
            # For each numerical column, mark extreme values as anomalies
            for col in numeric_cols[:3]:  # Use at most 3 columns
                values = data[col].values
                sorted_values = np.sort(values)
                
                # Mark highest and lowest 5% as potential anomalies
                low_threshold = sorted_values[int(len(sorted_values) * 0.05)]
                high_threshold = sorted_values[int(len(sorted_values) * 0.95)]
                
                # Mark values outside these thresholds
                col_anomalies = ((values <= low_threshold) | (values >= high_threshold)).astype(int)
                ground_truth = np.logical_or(ground_truth, col_anomalies).astype(int)
        else:
            # If no numerical columns, create random ground truth
            ground_truth = np.random.choice([0, 1], size=len(data), p=[0.9, 0.1])
        
        # Calculate performance metrics
        tn, fp, fn, tp = confusion_matrix(ground_truth, anomalies, labels=[0, 1]).ravel()
        
        # Calculate metrics (handle division by zero)
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics = {
            'model_name': 'K-Means Clustering',
            'anomaly_count': int(anomaly_count),
            'total_records': len(data),
            'anomaly_percent': float(anomaly_percent),
            'threshold_used': float(threshold),
            'n_clusters': n_clusters,
            'cluster_distribution': {
                f'cluster_{i}': {
                    'count': int(cluster_counts[i]),
                    'percent': float(cluster_percents[i])
                } for i in range(n_clusters)
            },
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'true_positives': int(tp),
            'false_positives': int(fp),
            'true_negatives': int(tn),
            'false_negatives': int(fn)
        }
        
        return results, metrics
