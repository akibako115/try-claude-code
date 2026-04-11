from __future__ import annotations

import logging

from openai import OpenAI

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """あなたは機械学習・AI分野の論文を日本語で解説するアシスタントです。
論文のタイトル・著者・URLをもとに、以下の構成で論文を解説してください。
URLが論文ページ（arXivなど）であればその内容も参照してください。
各セクションは3〜5文程度で簡潔にまとめ、不明な場合は「情報なし」と記載してください。

# 研究の背景・先行研究の流れ
（この研究が取り組む問題と、先行研究の限界・課題を説明する）

# 提案手法の優位性・新規性・貢献
（先行研究と比べて何が新しく、どのような貢献をもたらすかを説明する）

# 提案手法のロジックの全体像
（アーキテクチャの構成、処理の流れ、損失関数の設計を説明する）

# 提案手法の理論・数式ベースでの解説
（核となる理論・数式・アルゴリズムをできるだけ具体的に説明する）

# 実験結果
（使用データセット、評価指標、ベースラインとの比較結果を説明する）

# 限界・今後の展開
（手法の制約・失敗ケース・著者が言及する今後の課題を説明する）"""


def generate_memo(title: str, authors: str, url: str, api_key: str) -> str:
    """ChatGPT API を使って論文のメモを自動生成する。

    api_key が未設定またはダミーの場合は空文字を返す。
    """
    if not api_key or api_key.startswith("sk-dummy"):
        return ""

    client = OpenAI(api_key=api_key)

    user_message = f"タイトル: {title}"
    if authors:
        user_message += f"\n著者: {authors}"
    if url:
        user_message += f"\nURL: {url}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=2000,
            temperature=0.3,
            timeout=30,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.warning("OpenAI API 呼び出しに失敗しました: %s", e)
        return ""
