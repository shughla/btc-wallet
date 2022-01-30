import uvicorn

from app.runner.asgi import app

uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
