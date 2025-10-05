import os
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "dev-secret"))

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")  # must match your Google redirect URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    request.session["id_token"] = token["id_token"]
    return RedirectResponse(url="/id_token")

@app.get("/id_token")
async def id_token(request: Request):
    t = request.session.get("id_token")
    if not t:
        return JSONResponse({"error": "not logged in"}, status_code=401)
    return {"id_token": t}
