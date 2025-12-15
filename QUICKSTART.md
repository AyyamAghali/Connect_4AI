# Quick Start Guide

## Setup

1. **Create and activate virtual environment** (if not already done):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or use the setup script:
   ```bash
   bash setup_env.sh
   ```

## Running the Application

### Option 1: Using the run script (recommended)
```bash
source venv/bin/activate  # Activate virtual environment first
python run.py
```

### Option 2: Direct Flask run
```bash
source venv/bin/activate
python app.py
```

### Option 3: Using the shell script
```bash
bash run.sh
```

The server will start on `http://localhost:5001`

## Running Data Collection

To collect game data:
```bash
source venv/bin/activate
python data/data_collection.py
```

## Notes

- Always activate the virtual environment before running scripts
- The server runs on port 5001 by default
- Open `http://localhost:5001` in your browser to play

