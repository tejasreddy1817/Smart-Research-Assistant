"""
SummarizerAgent: creates Introduction, Key Insights, Future Trends.
If OPENAI_API_KEY present and use_openai=True, uses OpenAI completions.
Else falls back to an extractive/templated summarizer.
"""
import os
from typing import List, Dict
import textwrap

try:
    import openai
except Exception:
    openai = None

class SummarizerAgent:
    def __init__(self, use_openai: bool = False):
        self.use_openai = use_openai and bool(os.getenv("OPENAI_API_KEY")) and openai is not None
        if self.use_openai:
            openai.api_key = os.getenv("OPENAI_API_KEY")

    def run(self, topic: str, docs: List[Dict], analysis: Dict) -> str:
        if self.use_openai:
            return self._openai_summarize(topic, docs, analysis)
        return self._simple_summarize(topic, docs, analysis)

    def _simple_summarize(self, topic, docs, analysis):
        intro = f"**Introduction**\n\nThis short report summarizes findings related to **{topic}** based on {analysis['num_docs']} sources."
        insights = "\n\n**Key Insights**\n\n"
        insights += "\n".join(f"- {k}" for k in analysis["themes"])
        insights += f"\n\nAverage words per doc: {analysis['avg_word_count']:.0f}"
        sentiment = "neutral"
        if analysis["sentiment_score"] > 0.3:
            sentiment = "positive"
        elif analysis["sentiment_score"] < -0.3:
            sentiment = "negative"
        insights += f"\n\nOverall sentiment: **{sentiment}**"

        future = "\n\n**Future Trends & Recommendations**\n\n"
        future += "- Investigate multimodal and retrieval-augmented techniques.\n"
        future += "- Focus on evaluation metrics and ethical implications.\n"

        full = "\n\n".join([intro, insights, future])
        return full

    def _openai_summarize(self, topic, docs, analysis):
        prompt = self._build_prompt(topic, docs, analysis)
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini" if "gpt-4o-mini" in openai.Model.list().data else "gpt-4o",
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
            max_tokens=600,
        )
        text = resp.choices[0].message.content.strip()
        return text

    def _build_prompt(self, topic, docs, analysis):
        snippet = "\n\n".join(f"{i+1}. {d['title']}: {d['content'][:400]}" for i,d in enumerate(docs))
        prompt = f"""
You are a concise research summarizer. Create a report with sections: Introduction, Key Insights (bulleted), Future Trends & Recommendations.
Topic: {topic}

Analysis summary: {analysis}

Source snippets:
{snippet}

Write clearly and short.
"""
        return prompt
