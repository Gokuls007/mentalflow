import sys
import os
import uvicorn

# Manually inject the User Site-Packages path to ensure all clinical dependencies are found
user_site = os.path.expandvars(r'%APPDATA%\Python\Python314\site-packages')
if user_site not in sys.path:
    sys.path.append(user_site)

# Also ensure the local app directory is in the path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

if __name__ == "__main__":
    print(f"Starting MentalFlow Backend with hardened paths...")
    print(f"System Path: {sys.path[:3]}...") # Log first few entries
    
    try:
        import sqlalchemy
        print(f"[SUCCESS] SqlAlchemy {sqlalchemy.__version__} loaded successfully.")
    except ImportError as e:
        print(f"[ERROR] Critical Error: Could not load SqlAlchemy from {user_site}")
        print(e)
        sys.exit(1)

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
