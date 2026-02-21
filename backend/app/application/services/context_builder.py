from app.domain.entities.matches import Match


class ContextBuilder:
    async def build(self, match: Match) -> dict:
        context = {
            "match_id": str(match.id.value),
            "team_a": match.team_a_name.value,
            "team_b": match.team_b_name.value,
            "score_a": match.score.a.value,
            "score_b": match.score.b.value,
            "current_set": match.current_set.value,
            "rotation_a": match.rotation.team_a.value,
            "rotation_b": match.rotation.team_b.value,
        }

        context["set_scores"] = [(s.a.value, s.b.value) for s in match.set_scores]
        context["situation"] = self._detect_situation(context)
        return context

    def _detect_situation(self, ctx: dict) -> str:
        a, b = ctx["score_a"], ctx["score_b"]
        set_num = ctx["current_set"]
        if set_num == 5 and a >= 14 and b >= 14:
            return "match_point"
        
        if a >= 24 and b >= 24:
            return "deuce"
        
        if (a >= 24 and a - b >= 2) or (b >= 24 and b - a >= 2):
            return "set_point"

        if abs(a - b) >= 5:
            return "big_lead"
        
        if abs(a - b) <= 2:
            return "close_game"

        return "normal"
