from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_SYSTEM_PROMPT = """あなたは論文のメモを作成するアシスタントです。
論文のタイトル・著者・URLをもとに、その論文の概要・手法・貢献を
3〜5文の日本語で簡潔にまとめてください。
URLが論文ページであればその情報も考慮してください。"""


def generate_memo(title: str, authors: str, url: str) -> str:
    """ChatGPT API を使って論文のメモを自動生成する。

    API キーが未設定またはダミーの場合は空文字を返す。
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-dummy"):
        return ""

    client = OpenAI(api_key=api_key)

    user_message = f"タイトル: {title}"
    if authors:
        user_message += f"\n著者: {authors}"
    if url:
        user_message += f"\nURL: {url}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content or ""
