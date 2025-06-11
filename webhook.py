from fastapi import FastAPI, Request
from db import set_subscribed
import uvicorn

app = FastAPI()

@app.post("/webhook")
async def crypto_webhook(req: Request):
    data = await req.json()
    try:
        user_id = int(data['invoice']['custom_id'])
        await set_subscribed(user_id)
        print(f"✅ Пользователь {user_id} оплатил подписку.")
    except Exception as e:
        print(f"❌ Ошибка в Webhook: {e}")
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("webhook:app", host="0.0.0.0", port=8000)
