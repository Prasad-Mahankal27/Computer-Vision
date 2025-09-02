# Complete Setup Commands - Privacy-Aware Gym Assistant

## Prerequisites Check
Open Command Prompt and check Python version:

python --version

Should show Python 3.8 or higher.

## Step 1: Create Project Directory

mkdir gym-assistant
cd gym-assistant


## Step 2: Create Virtual Environment

python -m venv venv


## Step 3: Activate Virtual Environment

venv\Scripts\activate


## Step 4: Upgrade pip

python.exe -m pip install --upgrade pip


## Step 5: Install Packages

pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-multipart==0.0.6 opencv-python==4.8.1.78 mediapipe>=0.10.13 numpy>=1.24.3 websockets==12.0


## Step 6: Create main.py File
Create a new file called `main.py` in the gym-assistant folder and paste the complete main.py code from the artifacts above.

## Step 7: Run the Application

python main.py


## Step 8: Open Browser
Look for the output line that shows:

Server: http://localhost:XXXX

Copy that URL and paste it into your web browser.

## Daily Usage Commands
To run the app again later:

cd gym-assistant
venv\Scripts\activate
python main.py


## Stop the Server
Press `Ctrl+C` in the command prompt.


## File Structure Should Look Like:

gym-assistant/
├── venv/           (virtual environment - don't modify)
├── main.py         (your application code)
└── __pycache__/    (auto-generated - ignore)


## Troubleshooting
If Step 5 fails, try:

pip install opencv-python-headless==4.8.1.78

Instead of regular opencv-python.
