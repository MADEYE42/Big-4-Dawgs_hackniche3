import numpy as np
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)


class ChallengeRecommendationSystem:
    def __init__(self, exploration_rate=0.2):
        self.exploration_rate = exploration_rate
        self.challenges = {
            "First Purchase": {
                "description": "Make your first purchase",
                "max_progress": 1,
            },
            "Write a Review": {
                "description": "Write a review for a product",
                "max_progress": 1,
            },
            "Complete Your Profile": {
                "description": "Fill out all profile information",
                "max_progress": 5,
            },
            "Browse Five Products": {
                "description": "View details of five different products",
                "max_progress": 5,
            },
            "Add to Wishlist": {
                "description": "Add three products to your wishlist",
                "max_progress": 3,
            },
            "Share on Social Media": {
                "description": "Share a product on social media",
                "max_progress": 1,
            },
            "Refer a Friend": {
                "description": "Refer a friend to our platform",
                "max_progress": 1,
            },
            "Complete a Survey": {
                "description": "Fill out our customer satisfaction survey",
                "max_progress": 1,
            },
            "Download Our App": {
                "description": "Download and log in to our mobile app",
                "max_progress": 2,
            },
            "Make a Repeat Purchase": {
                "description": "Make another purchase within 30 days",
                "max_progress": 1,
            },
            "Write an In-depth Review": {
                "description": "Write a detailed review with pros and cons",
                "max_progress": 1,
            },
            "Watch Product Video": {
                "description": "Watch our product demonstration videos",
                "max_progress": 3,
            },
        }

        self.user_challenge_q_values = {}
        self.segment_preferences = {
            "high_value": {c: 0.5 for c in self.challenges},
            "purchaser": {c: 0.3 for c in self.challenges},
            "engaged": {c: 0.2 for c in self.challenges},
            "new": {c: 0.1 for c in self.challenges},
        }
        self.challenge_q_values = {c: 0.2 for c in self.challenges}
        self.challenge_attempts = {c: 0 for c in self.challenges}
        self.challenge_completions = {c: 0 for c in self.challenges}

    def get_user_segment(self, user):
        """Determine user segment based on user data"""
        if user["lifetime_purchases"] > 3:
            return "high_value"
        elif user["lifetime_purchases"] > 0:
            return "purchaser"
        elif user["reviews_written"] > 0:
            return "engaged"
        return "new"

    def select_challenge(self, user):
        """Select a challenge for the user"""
        user_id = user["user_id"]
        user_segment = self.get_user_segment(user)

        if user_id not in self.user_challenge_q_values:
            self.user_challenge_q_values[user_id] = {c: 0.0 for c in self.challenges}

        if np.random.random() < self.exploration_rate:
            return np.random.choice(list(self.challenges.keys()))

        combined_q_values = {
            c: (
                0.6 * self.user_challenge_q_values[user_id][c]
                + 0.3 * self.segment_preferences[user_segment][c]
                + 0.1 * self.challenge_q_values[c]
            )
            for c in self.challenges
        }

        return max(combined_q_values, key=combined_q_values.get)

    def simulate_user_interaction(self, user, challenge):
        """Simulate user interaction with a challenge"""
        if not challenge:
            return 0, False, False, False

        base_progress = 1
        purchase_prob = 0.1
        review_prob = 0.1
        segment = self.get_user_segment(user)

        if segment == "high_value":
            purchase_prob, review_prob = 0.3, 0.2
        elif segment == "purchaser":
            purchase_prob, review_prob = 0.2, 0.15
        elif segment == "engaged":
            review_prob = 0.25

        if "Purchase" in challenge:
            purchase_prob *= 2
        elif "Review" in challenge:
            review_prob *= 2

        progress = min(base_progress, self.challenges[challenge]["max_progress"])
        completed = (
            user["challenge_progress"] + progress
            >= self.challenges[challenge]["max_progress"]
        )
        purchase_made = np.random.random() < purchase_prob
        review_written = np.random.random() < review_prob

        return progress, completed, purchase_made, review_written

    def calculate_reward(
        self, completed, purchase_made, review_written, review_length=0
    ):
        """Calculate user reward based on challenge interaction"""
        reward = 1.0 if completed else 0
        reward += 2.0 if purchase_made else 0

        if review_written:
            reward += 1.5 + min(review_length / 500 * 1.0, 1.0)

        return reward

    def update_q_values(self, user, challenge, reward):
        """Update Q-values based on the observed reward"""
        if challenge is None:
            return

        user_id = user["user_id"]
        user_segment = self.get_user_segment(user)

        alpha = 0.1
        self.user_challenge_q_values[user_id][challenge] = (
            1 - alpha
        ) * self.user_challenge_q_values[user_id][challenge] + alpha * reward
        self.segment_preferences[user_segment][challenge] = (
            1 - alpha
        ) * self.segment_preferences[user_segment][challenge] + alpha * reward
        self.challenge_q_values[challenge] = (1 - alpha) * self.challenge_q_values[
            challenge
        ] + alpha * reward

    def get_challenge_insights(self):
        """Retrieve challenge performance insights"""
        return {
            "completion_rates": {
                c: self.challenge_completions[c] / max(1, self.challenge_attempts[c])
                for c in self.challenges
            }
        }


recommendation_system = ChallengeRecommendationSystem()


@app.route("/segment_user", methods=["POST"])
def segment_user():
    """Determine user segment"""
    user = request.json
    segment = recommendation_system.get_user_segment(user)
    return jsonify({"user_segment": segment})


@app.route("/select_challenge", methods=["POST"])
def select_challenge():
    """Select a challenge for the user"""
    user = request.json
    challenge = recommendation_system.select_challenge(user)
    return jsonify({"selected_challenge": challenge})


@app.route("/simulate_interaction", methods=["POST"])
def simulate_interaction():
    """Simulate user interaction with a challenge"""
    data = request.json
    user, challenge = data["user"], data["challenge"]
    progress, completed, purchase, review = (
        recommendation_system.simulate_user_interaction(user, challenge)
    )

    return jsonify(
        {
            "progress": progress,
            "completed": completed,
            "purchase_made": purchase,
            "review_written": review,
        }
    )


@app.route("/calculate_reward", methods=["POST"])
def calculate_reward():
    """Calculate the reward for a user's interaction"""
    data = request.json
    reward = recommendation_system.calculate_reward(
        data["completed"],
        data["purchase_made"],
        data["review_written"],
        data.get("review_length", 0),
    )
    return jsonify({"reward": reward})


@app.route("/update_q_values", methods=["POST"])
def update_q_values():
    """Update Q-values for a challenge"""
    data = request.json
    recommendation_system.update_q_values(
        data["user"], data["challenge"], data["reward"]
    )
    return jsonify({"message": "Q-values updated"})


@app.route("/get_insights", methods=["GET"])
def get_insights():
    """Get challenge performance insights"""
    insights = recommendation_system.get_challenge_insights()
    return jsonify(insights)


@app.route("/recommend_challenges", methods=["POST"])
def recommend_challenges():
    """Recommend challenges for a user"""
    data = request.json
    user = data["user"]
    num_recommendations = data.get("num_recommendations", 3)

    recommended_challenges = sorted(
        recommendation_system.challenges.keys(),
        key=lambda c: recommendation_system.challenge_q_values[c],
        reverse=True,
    )[:num_recommendations]

    return jsonify({"recommended_challenges": recommended_challenges})


if __name__ == "__main__":
    app.run(debug=True)
