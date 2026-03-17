from typing import List, Dict, Any


class ConflictDetector:
    """
    Detects contradictions between domain agent summaries.
    Compares key claims across clinical, patent, market, and regulatory domains
    and flags pairs that appear to contradict each other.
    """

    # Pairs of terms that signal potential conflicts
    CONFLICT_SIGNALS = [
        ({"approved", "fda approved", "marketed"}, {"no approval", "not approved", "withdrawn", "banned"}),
        ({"phase 3", "phase iii", "completed"}, {"no trials", "no clinical data", "preclinical only"}),
        ({"patent expired", "generic available", "off-patent"}, {"patent protected", "exclusivity", "composition patent"}),
        ({"safe", "well tolerated", "low toxicity"}, {"black box warning", "serious adverse", "high toxicity"}),
    ]

    def detect(self, summaries: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Compare domain summaries pairwise and return a list of conflict records.

        Each record: {domains, signal, excerpt_a, excerpt_b}
        """
        conflicts = []
        domains = list(summaries.keys())

        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                da, db = domains[i], domains[j]
                text_a = (summaries[da] or "").lower()
                text_b = (summaries[db] or "").lower()

                for pos_terms, neg_terms in self.CONFLICT_SIGNALS:
                    a_pos = any(t in text_a for t in pos_terms)
                    a_neg = any(t in text_a for t in neg_terms)
                    b_pos = any(t in text_b for t in pos_terms)
                    b_neg = any(t in text_b for t in neg_terms)

                    # Conflict: one domain says positive, other says negative
                    if (a_pos and b_neg) or (a_neg and b_pos):
                        signal = list(pos_terms)[0] + " vs " + list(neg_terms)[0]
                        conflicts.append({
                            "domains": [da, db],
                            "signal": signal,
                            "excerpt_a": self._excerpt(summaries[da], pos_terms | neg_terms),
                            "excerpt_b": self._excerpt(summaries[db], pos_terms | neg_terms),
                        })

        return conflicts

    def _excerpt(self, text: str, terms: set, window: int = 80) -> str:
        """Return a short excerpt around the first matching term."""
        lower = text.lower()
        for term in terms:
            idx = lower.find(term)
            if idx != -1:
                start = max(0, idx - window // 2)
                end = min(len(text), idx + len(term) + window // 2)
                return "..." + text[start:end].strip() + "..."
        return text[:window] + "..."


conflict_detector = ConflictDetector()
