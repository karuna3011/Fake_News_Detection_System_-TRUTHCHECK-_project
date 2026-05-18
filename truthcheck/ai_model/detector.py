"""
TruthCheck AI Engine
Fake News Detection using TF-IDF + Logistic Regression / PassiveAggressiveClassifier
"""

import os
import re
import json
import logging
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fake_news_model.pkl')

# ── Linguistic patterns for rule-based signals ──────────────────────────────

FAKE_PATTERNS = [
    r'\b(BREAKING|EXCLUSIVE|SHOCKING|BOMBSHELL|EXPOSED|SCANDAL)\b',
    r'\b(you won\'t believe|mind-blowing|secret they don\'t want|wake up|sheeple)\b',
    r'\b(government conspiracy|deep state|mainstream media lies|fake news media)\b',
    r'(!{2,}|\?{2,})',   # multiple exclamation/question marks
    r'\b(100%|absolutely proven|definitive proof|scientists confirm|doctors hate)\b',
    r'\b(illuminati|new world order|cabal|reptilian|chemtrails)\b',
]

REAL_PATTERNS = [
    r'\b(according to|researchers found|study shows|officials said|reported by)\b',
    r'\b(percent|per cent|statistics|data|evidence|analysis|survey)\b',
    r'\b(published|peer-reviewed|journal|university|institution)\b',
]

# ── Synthetic training data (fallback when no CSV is provided) ───────────────

SYNTHETIC_FAKE = [
    "SHOCKING: Government hiding alien technology in Area 51 documents LEAKED!!!",
    "You won't BELIEVE what they found in the water supply – mass poisoning confirmed",
    "BREAKING: Deep state operatives arrested in massive pedophile ring cover-up",
    "Scientists REFUSE to talk about this miracle cure Big Pharma doesn't want you to know",
    "EXPOSED: The moon landing was staged in a Hollywood studio, insider reveals all",
    "Chemtrails confirmed: pilots admit to spraying mind-control chemicals daily",
    "New World Order plans to microchip every human by 2025 – documents surface",
    "BOMBSHELL: 5G towers are spreading COVID-19, whistleblower comes forward",
    "Soros funds secret army of protestors to destroy America from within EXCLUSIVE",
    "Vaccines contain nanobots that track your location in real-time – LEAKED documents",
    "FBI files PROVE Obama is a Kenyan spy working for the Muslim Brotherhood",
    "Hollywood elites drink children's blood in satanic rituals – survivor speaks out",
    "Climate change is a HOAX invented by globalists to control the world economy",
    "Doctors BANNED from telling you this one trick that cures cancer overnight",
    "ALERT: Drinking bleach cures coronavirus, suppressed by mainstream media",
    "President secretly replaced by body double, insiders confirm the switch",
    "Ancient prophecy FULFILLED – end of the world begins this September!!!",
    "George Soros literally owns all mainstream media and controls every election",
    "Water fluoridation is a communist plot to make Americans docile and obedient",
    "PROOF: The earth is flat and NASA has been lying for 60 years – pilot testimony",
    "Reptilian shapeshifters control the banking system and royal family",
    "QAnon drops BOMBSHELL: Storm is coming, arrests imminent for deep state cabal",
    "Leaked Pentagon memo confirms UFO crash retrieval program since 1947",
    "MIRACLE CURE: This common herb DESTROYS cancer cells doctors don't want you to know",
    "Mainstream media blackout: Thousands dying from vaccine injuries every day",
    "False flag operation exposed: Sandy Hook was staged with crisis actors",
    "Antifa paid $25 per hour by Soros foundation to riot in American cities",
    "Bill Gates planning to reduce world population through vaccine sterilization",
    "COVID-19 pandemic planned 10 years ago by globalist elite – proof inside",
    "The sun is actually a cold body and NASA uses CGI to hide the truth",
]

SYNTHETIC_REAL = [
    "Federal Reserve raises interest rates by 25 basis points amid inflation concerns",
    "Researchers at MIT publish study on renewable energy efficiency improvements",
    "City council approves budget for infrastructure repair projects next fiscal year",
    "WHO reports decline in malaria cases following widespread prevention campaigns",
    "Stock markets closed mixed on Friday following jobs report data release",
    "Scientists discover new species of deep-sea fish in Pacific Ocean expedition",
    "Local school district announces new STEM curriculum starting next semester",
    "Hospital system reports improved patient outcomes after new treatment protocols",
    "University study finds correlation between exercise and improved mental health",
    "Transportation department announces highway expansion project timeline",
    "Central bank governor speaks on monetary policy at annual economic forum",
    "Researchers develop more efficient solar panel technology at lower cost",
    "City announces new public transit routes to underserved neighborhoods",
    "Agricultural department reports crop yields up 3 percent from previous year",
    "Tech company announces 500 new jobs in regional expansion announcement",
    "Health officials recommend updated vaccination schedule for flu season",
    "Supreme Court hears arguments in landmark environmental protection case",
    "International trade negotiations conclude with new agreement on tariffs",
    "Seismologists record 4.2 magnitude earthquake off coast, no damage reported",
    "Local government releases annual transparency report on budget spending",
    "Scientists confirm that regular hand washing reduces cold transmission by 40%",
    "New public library branch to open next month in downtown district area",
    "Study from Johns Hopkins finds Mediterranean diet linked to heart health",
    "State legislature passes bipartisan bill on water conservation measures",
    "NASA confirms successful launch of weather monitoring satellite into orbit",
    "Independent auditors verify election results in three contested counties",
    "According to CDC data, childhood vaccination rates increased by 5% last year",
    "Police department releases annual crime statistics showing 8% reduction",
    "Economists forecast moderate GDP growth of 2.3% in the coming fiscal year",
    "University researchers publish peer-reviewed findings on sleep and cognition",
]


class FakeNewsDetector:
    """Core AI model for fake news detection."""

    def __init__(self):
        self.model = None
        self.is_trained = False
        self._load_or_train()

    # ── Public API ────────────────────────────────────────────────────────────

    def predict(self, text: str) -> dict:
        """Return prediction dict for the given text."""
        cleaned = self._preprocess(text)

        if self.is_trained:
            proba = self.model.predict_proba([cleaned])[0]
            classes = self.model.classes_
            fake_idx = list(classes).index('FAKE') if 'FAKE' in classes else 0
            real_idx = list(classes).index('REAL') if 'REAL' in classes else 1

            fake_prob = float(proba[fake_idx])
            real_prob = float(proba[real_idx])
            result = 'FAKE' if fake_prob > real_prob else 'REAL'
            confidence = float(max(fake_prob, real_prob))
        else:
            # Rule-based fallback
            fake_prob, real_prob = self._rule_based_score(cleaned)
            result = 'FAKE' if fake_prob > 0.5 else 'REAL'
            confidence = max(fake_prob, real_prob)

        # Apply linguistic adjustments
        adj_fake, adj_real = self._linguistic_adjustment(text, fake_prob, real_prob)

        explanation = self._generate_explanation(text, result, adj_fake)
        features = self._extract_top_features(cleaned)

        return {
            'result': result,
            'confidence': round(confidence * 100, 1),
            'fake_probability': round(adj_fake * 100, 1),
            'real_probability': round(adj_real * 100, 1),
            'explanation': explanation,
            'top_features': features,
            'word_count': len(text.split()),
            'credibility_score': round((1 - adj_fake) * 100, 1),
        }

    # ── Training ──────────────────────────────────────────────────────────────

    def _load_or_train(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.is_trained = True
                logger.info("✅ Model loaded from disk.")
                return
            except Exception as e:
                logger.warning(f"Could not load model: {e}. Retraining…")

        self._train_on_synthetic()

    def _train_on_synthetic(self):
        logger.info("🔧 Training on synthetic dataset…")
        texts = SYNTHETIC_FAKE + SYNTHETIC_REAL
        labels = ['FAKE'] * len(SYNTHETIC_FAKE) + ['REAL'] * len(SYNTHETIC_REAL)

        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 3),
                stop_words='english',
                sublinear_tf=True,
                min_df=1,
            )),
            ('clf', LogisticRegression(
                max_iter=1000,
                C=1.0,
                class_weight='balanced',
                random_state=42,
            )),
        ])

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        logger.info(f"✅ Model trained — accuracy: {acc:.2%}")
        logger.info("\n" + classification_report(y_test, y_pred))

        self.model = pipeline
        self.is_trained = True

        try:
            joblib.dump(pipeline, MODEL_PATH)
            logger.info(f"💾 Model saved to {MODEL_PATH}")
        except Exception as e:
            logger.warning(f"Could not save model: {e}")

    def train_on_dataframe(self, df):
        """Train/retrain on a pandas DataFrame with 'text' and 'label' columns."""
        texts = df['text'].tolist()
        labels = df['label'].tolist()

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=50000,
                ngram_range=(1, 3),
                stop_words='english',
                sublinear_tf=True,
            )),
            ('clf', PassiveAggressiveClassifier(
                max_iter=1000,
                random_state=42,
                class_weight='balanced',
            )),
        ])

        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        self.model = pipeline
        self.is_trained = True
        joblib.dump(pipeline, MODEL_PATH)

        return {
            'accuracy': round(acc * 100, 2),
            'report': classification_report(y_test, y_pred, output_dict=True),
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _preprocess(text: str) -> str:
        text = text.lower()
        text = re.sub(r'http\S+|www\S+', ' URL ', text)
        text = re.sub(r'\S+@\S+', ' EMAIL ', text)
        text = re.sub(r'[^a-z0-9\s!?]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def _rule_based_score(text: str):
        fake_hits = sum(1 for p in FAKE_PATTERNS if re.search(p, text, re.IGNORECASE))
        real_hits = sum(1 for p in REAL_PATTERNS if re.search(p, text, re.IGNORECASE))
        total = fake_hits + real_hits + 1e-9
        fake_prob = min(0.9, 0.4 + (fake_hits / total) * 0.5)
        real_prob = 1 - fake_prob
        return fake_prob, real_prob

    def _linguistic_adjustment(self, text: str, fake_prob: float, real_prob: float):
        fake_hits = sum(1 for p in FAKE_PATTERNS if re.search(p, text, re.IGNORECASE))
        real_hits = sum(1 for p in REAL_PATTERNS if re.search(p, text, re.IGNORECASE))

        adj = fake_prob + (fake_hits * 0.02) - (real_hits * 0.02)
        adj = max(0.05, min(0.95, adj))
        return adj, 1 - adj

    @staticmethod
    def _generate_explanation(text: str, result: str, fake_prob: float) -> str:
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        word_count = len(text.split())

        signals = []
        if exclamation_count > 2:
            signals.append(f"excessive punctuation ({exclamation_count} exclamation marks)")
        if caps_ratio > 0.15:
            signals.append("high proportion of capital letters (sensationalist style)")
        if re.search(r'\b(BREAKING|EXCLUSIVE|SHOCKING)\b', text, re.I):
            signals.append("sensational headline keywords")
        if re.search(r'\b(according to|researchers|study|officials)\b', text, re.I):
            signals.append("references to credible sources")
        if word_count < 30:
            signals.append("very short text (limited context for analysis)")

        if result == 'FAKE':
            base = (
                f"The AI model classified this article as likely FAKE with "
                f"{fake_prob*100:.1f}% confidence. "
            )
            if signals:
                base += f"Key indicators: {', '.join(signals)}. "
            base += (
                "Fake news often uses emotional language, unverified claims, "
                "and lacks citations from credible sources. Always cross-reference "
                "with established news outlets."
            )
        else:
            base = (
                f"The AI model classified this article as likely REAL with "
                f"{(1-fake_prob)*100:.1f}% confidence. "
            )
            if signals:
                base += f"Positive indicators: {', '.join(signals)}. "
            base += (
                "The text appears to follow journalistic conventions with measured "
                "language and factual framing. However, always verify from multiple "
                "independent sources."
            )

        return base

    def _extract_top_features(self, text: str, n: int = 8) -> list:
        """Return the top TF-IDF feature words for this text."""
        if not self.is_trained:
            return []
        try:
            vectorizer = self.model.named_steps['tfidf']
            vec = vectorizer.transform([text])
            feature_names = vectorizer.get_feature_names_out()
            indices = vec.toarray()[0].argsort()[::-1][:n]
            return [
                {'word': feature_names[i], 'score': round(float(vec.toarray()[0][i]), 4)}
                for i in indices if vec.toarray()[0][i] > 0
            ]
        except Exception:
            return []


# Singleton instance
_detector = None

def get_detector() -> FakeNewsDetector:
    global _detector
    if _detector is None:
        _detector = FakeNewsDetector()
    return _detector
