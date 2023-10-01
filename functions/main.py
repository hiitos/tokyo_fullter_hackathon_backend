import firebase_admin
from firebase_admin import firestore
from firebase_functions import https_fn, scheduler_fn

from dotenv import load_dotenv
import time
import datetime
from app_workflow import workflow
from llm import drunk_words_creater

# .env ファイルを読み込む
load_dotenv()

# Firebaseの初期化
app = firebase_admin.initialize_app()
db = firestore.client()

# HTTPリクエストハンドラ
@https_fn.on_request()
def backend_test(req: https_fn.Request) -> https_fn.Response:
    workflow(db)
    return https_fn.Response("Success")

@https_fn.on_request()
def strong_bot(req: https_fn.Request) -> https_fn.Response:
    result = drunk_words_creater()
    return https_fn.Response(result)

# 定期実行ジョブ
@scheduler_fn.on_schedule(schedule='* * * * *')
def cron_job_handler(event: scheduler_fn.ScheduledEvent) -> None:
    dt_now = datetime.datetime.now()
    print(f"exec timestamp : {dt_now}")
    workflow(db)