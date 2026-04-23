import sys
import asyncio

# Patch asyncio for Python 3.14 compatibility with Streamlit
_old_get_event_loop = asyncio.get_event_loop
def safe_get_event_loop():
    try:
        return _old_get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
asyncio.get_event_loop = safe_get_event_loop

from streamlit.web.cli import main
sys.argv = ["streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8501"]
main()
