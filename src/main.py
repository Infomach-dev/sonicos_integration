import uvicorn

if __name__ == "__main__":
    uvicorn.run("routes.appRoutes:app", host="172.28.106.232", port=5000, reload=True)


