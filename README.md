# Energy Anomaly Detection System

An advanced energy consumption anomaly detection system leveraging machine learning to provide intelligent insights into energy usage patterns.

## Features

- Anomaly detection using various machine learning algorithms
- Interactive visualizations with Plotly
- User authentication and data persistence
- Energy efficiency recommendations
- 100% offline functionality

## Operation Modes

The system can be operated in two modes:

### 1. Standalone Mode (100% Offline)

This mode runs only the Streamlit frontend application and provides all functionality without requiring external services or database connectivity.

**To run in standalone mode:**
```bash
./run_app.sh
```

- All data is stored in local files
- Full functionality is available without internet connectivity
- Perfect for quick testing and demonstrations

### 2. Integrated Mode (Flask + Streamlit)

This mode runs both the Flask backend API and the Streamlit frontend, providing enhanced functionality with database persistence when available.

**To run in integrated mode:**
```bash
./run_flask_app.sh
```

- Enhanced data persistence in PostgreSQL database (when available)
- Still works 100% offline with fallback to file-based storage
- Better suited for production deployments

## Technical Details

- **Frontend**: Streamlit with Plotly visualizations
- **Backend**: Flask API
- **Database**: PostgreSQL (with file-based fallback)
- **Machine Learning**: Isolation Forest, Autoencoder, K-Means algorithms
- **Data Analysis**: Pandas, NumPy, SciKit-Learn

## Default User Credentials

For testing purposes, the following default credentials are available:

- Username: `admin`, Password: `admin`
- Username: `demo`, Password: `demo`
