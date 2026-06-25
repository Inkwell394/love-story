import sys, os

# ?? backend ??????
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.dirname(__file__))

# ???? main ??
import main
app = main.app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
