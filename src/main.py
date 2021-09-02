import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run("routes.appRoutes:app", host="0.0.0.0", port=os.environ.get('PORT'), reload=True)


