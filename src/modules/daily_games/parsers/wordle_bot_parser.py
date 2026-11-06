
import re

def parse_scores(message: str) -> list[dict]:
    results = []

    for match in re.finditer(r'(X|\d+)/(\d+):([^\n]*)', message, re.I):
        score_text = match.group(1)
        line = match.group(3)

        score = int(score_text) if score_text.isdigit() else 7 # magic number for failed score

        user_ids = re.findall(r'<@!?(\d+)>', line)


        for user_id in user_ids:
            results.append({
                "id": int(user_id),
                "score": score
            })

    return results
