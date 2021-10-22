import os
import uvicorn

port = int(os.environ.get('PORT'))

if __name__ == "__main__":
    uvicorn.run("routes.appRoutes:app", host="0.0.0.0", port=os.PORT, reload=True)


