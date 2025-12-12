# Quick Start Guide

Get the Connect 4 AI game running in 3 simple steps!

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

(On some systems, use `pip3` instead of `pip`)

## Step 2: Start the Server

```bash
python run.py
```

(On some systems, use `python3` instead of `python`)

## Step 3: Play!

Open your browser and go to: **http://localhost:5001**

That's it! Enjoy playing Connect 4 against the AI!

---

### Troubleshooting

**"Python not found"**
- Install Python from https://www.python.org/downloads/
- Make sure Python is added to your system PATH

**"pip not found"**
- Try `pip3` instead of `pip`
- On Windows, try `python -m pip install -r requirements.txt`

**"Port 5001 already in use"**
- Close other programs using port 5001
- Or edit `app.py` line 210 to use a different port

**"Import errors"**
- Make sure you're in the project directory
- Run `pip install -r requirements.txt` again

For more details, see [README.md](README.md)
