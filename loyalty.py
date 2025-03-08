import random
from collections import defaultdict

import numpy as np
import pandas as pd


class ChallengeRecommendationSystem:
    def __init__(self, exploration_rate=0.1):
        """
        Initialize the recommendation system.

        Args:
            exploration_rate: Probability of exploring rather than exploiting
        """
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

        self.challenge_q_values = {challenge: 0.0 for challenge in self.challenges}
        self.user_challenge_q_values = {}

        self.challenge_completions = {challenge: 0 for challenge in self.challenges}
        self.challenge_attempts = {challenge: 0 for challenge in self.challenges}

        self.segment_preferences = defaultdict(lambda: defaultdict(float))

    def get_user_segment(self, user):
        """Determine user segment based on user data"""
        if user["lifetime_purchases"] > 3:
            return "high_value"
        elif user["lifetime_purchases"] > 0:
            return "purchaser"
        elif user["reviews_written"] > 0:
            return "engaged"
        else:
            return "new"

    def select_challenge(self, user):
        """
        Select a challenge for a user using epsilon-greedy strategy.

        Args:
            user: User data

        Returns:
            str: Selected challenge name
        """
        user_id = user["user_id"]
        user_segment = self.get_user_segment(user)

        if user_id not in self.user_challenge_q_values:
            self.user_challenge_q_values[user_id] = {
                challenge: 0.0 for challenge in self.challenges
            }

        if np.random.random() < self.exploration_rate:
            return np.random.choice(list(self.challenges.keys()))

        combined_q_values = {}
        for challenge in self.challenges:
            user_specific_weight = 0.6
            segment_weight = 0.3
            global_weight = 0.1

            combined_value = (
                user_specific_weight * self.user_challenge_q_values[user_id][challenge]
                + segment_weight * self.segment_preferences[user_segment][challenge]
                + global_weight * self.challenge_q_values[challenge]
            )

            combined_q_values[challenge] = combined_value

        best_challenge = max(combined_q_values.items(), key=lambda x: x[1])[0]
        return best_challenge

    def simulate_user_interaction(self, user, challenge):
        """
        Simulate user interaction with a challenge.

        Args:
            user: User data
            challenge: Challenge to simulate

        Returns:
            tuple: (progress, completed, purchase, review)
        """
        if challenge is None:
            return 0, False, False, False

        base_progress = 1
        purchase_prob = 0.1
        review_prob = 0.1

        segment = self.get_user_segment(user)
        if segment == "high_value":
            purchase_prob = 0.3
            review_prob = 0.2
        elif segment == "purchaser":
            purchase_prob = 0.2
            review_prob = 0.15
        elif segment == "engaged":
            review_prob = 0.25

        if "Purchase" in challenge:
            purchase_prob *= 2
        elif "Review" in challenge:
            review_prob *= 2

        progress = min(base_progress, self.challenges[challenge]["max_progress"])
        completed = (user["challenge_progress"] + progress) >= self.challenges[
            challenge
        ]["max_progress"]
        purchase_made = np.random.random() < purchase_prob
        review_written = np.random.random() < review_prob

        self.challenge_attempts[challenge] += 1
        if completed:
            self.challenge_completions[challenge] += 1

        return progress, completed, purchase_made, review_written

    def calculate_reward(
        self, user, challenge, completed, purchase_made, review_written, review_length=0
    ):
        """
        Calculate the reward for a user's interaction with a challenge.
        Now includes review length as a factor for review challenges.

        Args:
            user: User data
            challenge: The challenge being evaluated
            completed: Whether the challenge was completed
            purchase_made: Whether a purchase was made
            review_written: Whether a review was written
            review_length: Length of the review (number of characters), default 0

        Returns:
            float: The calculated reward
        """
        base_reward = 0

        if completed:
            base_reward += 1.0

        if purchase_made:
            base_reward += 2.0

        if review_written:
            review_reward = 1.5

            max_review_length = 500

            max_length_bonus = 1.0

            effective_length = min(review_length, max_review_length)
            length_bonus = (effective_length / max_review_length) * max_length_bonus

            base_reward += review_reward + length_bonus

        if challenge is not None and "review" in challenge.lower():
            if review_written:
                base_reward += 1.0

                max_review_challenge_bonus = 1.5
                effective_length = min(review_length, max_review_length)
                challenge_length_bonus = (
                    effective_length / max_review_length
                ) * max_review_challenge_bonus

                base_reward += challenge_length_bonus

        user_segment = self.get_user_segment(user)

        return base_reward

    def update_q_values(self, user, challenge, reward, completed):
        """
        Update Q-values based on the observed reward.

        Args:
            user: User data
            challenge: The challenge being evaluated
            reward: Reward received
            completed: Whether the challenge was completed
        """
        if challenge is None:
            return

        user_id = user["user_id"]
        user_segment = self.get_user_segment(user)

        alpha = 0.1
        gamma = 0.8

        if user_id in self.user_challenge_q_values:
            current_q = self.user_challenge_q_values[user_id][challenge]
            self.user_challenge_q_values[user_id][challenge] = (
                1 - alpha
            ) * current_q + alpha * reward

        current_segment_q = self.segment_preferences[user_segment][challenge]
        self.segment_preferences[user_segment][challenge] = (
            1 - alpha
        ) * current_segment_q + alpha * reward

        current_global_q = self.challenge_q_values[challenge]
        self.challenge_q_values[challenge] = (
            1 - alpha
        ) * current_global_q + alpha * reward

    def get_challenge_insights(self):
        """Get insights about challenge performance"""
        completion_rates = {}
        for challenge in self.challenges:
            attempts = max(1, self.challenge_attempts[challenge])
            completions = self.challenge_completions[challenge]
            completion_rates[challenge] = completions / attempts

        segment_performance = {}
        for segment in self.segment_preferences:
            segment_performance[segment] = dict(self.segment_preferences[segment])

        return {
            "completion_rates": completion_rates,
            "segment_performance": segment_performance,
        }

    def recommend_next_challenges(self, user, num_recommendations=3):
        """
        Recommend the top challenges for a user.

        Args:
            user: User data
            num_recommendations: Number of recommendations to return

        Returns:
            list: Top recommended challenges
        """
        user_id = user["user_id"]
        user_segment = self.get_user_segment(user)

        if user_id not in self.user_challenge_q_values:
            self.user_challenge_q_values[user_id] = {
                challenge: 0.0 for challenge in self.challenges
            }

        combined_scores = {}
        for challenge in self.challenges:
            user_specific_weight = 0.6
            segment_weight = 0.3
            global_weight = 0.1

            combined_score = (
                user_specific_weight * self.user_challenge_q_values[user_id][challenge]
                + segment_weight * self.segment_preferences[user_segment][challenge]
                + global_weight * self.challenge_q_values[challenge]
            )

            combined_scores[challenge] = combined_score

        sorted_challenges = sorted(
            combined_scores.items(), key=lambda x: x[1], reverse=True
        )

        return [challenge for challenge, _ in sorted_challenges[:num_recommendations]]


def create_test_users(num_users=10):
    """Create test users with basic attributes"""
    users = pd.DataFrame(
        {
            "user_id": [f"user_{i}" for i in range(num_users)],
            "lifetime_purchases": np.random.randint(0, 5, num_users),
            "reviews_written": np.random.randint(0, 3, num_users),
            "completed_challenges": np.zeros(num_users),
            "active_challenge": [None] * num_users,
            "challenge_progress": np.zeros(num_users),
        }
    )

    return users


def run_challenge_simulation_with_inactive_users(num_iterations=30):
    """
    Run a simulation that includes users who don't complete challenges.
    Some users will be "inactive" with low engagement probability.
    Now includes review length as a factor in reward calculation.
    """
    recommendation_system = ChallengeRecommendationSystem(exploration_rate=0.2)
    users = create_test_users(15)

    users["engagement_probability"] = np.random.uniform(0.1, 0.9, len(users))

    inactive_user_indices = np.random.choice(
        len(users), size=int(len(users) * 0.2), replace=False
    )

    for idx in inactive_user_indices:
        users.at[idx, "engagement_probability"] = 0.05  # Very low engagement
        print(f"User {users.at[idx, 'user_id']} is set as inactive (low engagement)")

    results = []

    for iteration in range(num_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        for idx, user in users.iterrows():
            if user["active_challenge"] is None or (
                user["active_challenge"] is not None
                and user["challenge_progress"]
                >= recommendation_system.challenges[user["active_challenge"]][
                    "max_progress"
                ]
            ):
                selected_challenge = recommendation_system.select_challenge(user)
                users.at[idx, "active_challenge"] = selected_challenge
                users.at[idx, "challenge_progress"] = 0
                print(
                    f"User {user['user_id']} ({recommendation_system.get_user_segment(user)}) assigned: '{selected_challenge}'"
                )

            if np.random.random() > user["engagement_probability"]:
                print(f"User {user['user_id']} did not engage with their challenge")

                if user["active_challenge"] is not None:
                    reward = 0
                    recommendation_system.update_q_values(
                        user, user["active_challenge"], reward, completed=False
                    )

                    results.append(
                        {
                            "iteration": iteration + 1,
                            "user_id": user["user_id"],
                            "segment": recommendation_system.get_user_segment(user),
                            "challenge": user["active_challenge"],
                            "completed": False,
                            "purchase_made": False,
                            "review_written": False,
                            "review_length": 0,
                            "reward": reward,
                            "engaged": False,
                        }
                    )

                continue

            progress, completed, purchase, review = (
                recommendation_system.simulate_user_interaction(
                    user, user["active_challenge"]
                )
            )

            if user["active_challenge"] is None:
                continue

            users.at[idx, "challenge_progress"] += progress

            review_length = 0
            if review:
                is_review_challenge = (
                    user["active_challenge"] is not None
                    and "review" in user["active_challenge"].lower()
                )
                base_length = 200 if is_review_challenge else 100
                engagement_factor = user["engagement_probability"] * 300

                review_length = int(
                    base_length + engagement_factor + np.random.uniform(-50, 150)
                )
                review_length = max(20, review_length)

                print(
                    f"  → User {user['user_id']} wrote a review of {review_length} characters!"
                )

            if purchase:
                users.at[idx, "lifetime_purchases"] += 1
                print(f"  → User {user['user_id']} made a purchase!")

            if review:
                users.at[idx, "reviews_written"] += 1

            if completed:
                print(
                    f"  → User {user['user_id']} completed challenge '{user['active_challenge']}'!"
                )
                users.at[idx, "completed_challenges"] += 1

                reward = recommendation_system.calculate_reward(
                    user,
                    user["active_challenge"],
                    completed,
                    purchase,
                    review,
                    review_length,
                )

                recommendation_system.update_q_values(
                    user, user["active_challenge"], reward, completed
                )

                users.at[idx, "active_challenge"] = None
            else:
                reward = recommendation_system.calculate_reward(
                    user,
                    user["active_challenge"],
                    completed,
                    purchase,
                    review,
                    review_length,
                )

                recommendation_system.update_q_values(
                    user, user["active_challenge"], reward, completed
                )

            results.append(
                {
                    "iteration": iteration + 1,
                    "user_id": user["user_id"],
                    "segment": recommendation_system.get_user_segment(user),
                    "challenge": user["active_challenge"],
                    "completed": completed,
                    "purchase_made": purchase,
                    "review_written": review,
                    "review_length": review_length,
                    "reward": reward,
                    "engaged": True,
                }
            )

    if results:
        results_df = pd.DataFrame(results)
    else:
        results_df = pd.DataFrame(
            columns=[
                "iteration",
                "user_id",
                "segment",
                "challenge",
                "completed",
                "purchase_made",
                "review_written",
                "review_length",
                "reward",
                "engaged",
            ]
        )

    return recommendation_system, users, results_df


def analyze_results_with_inactivity(recommendation_system, users, results):
    print("\n=== SIMULATION RESULTS WITH INACTIVITY ANALYSIS ===")

    print("\nUser Growth:")
    initial_users = create_test_users(len(users))
    print(
        f"Initial average purchases: {initial_users['lifetime_purchases'].mean():.2f}"
    )
    print(f"Final average purchases: {users['lifetime_purchases'].mean():.2f}")
    print(
        f"Purchase growth: {(users['lifetime_purchases'].mean() - initial_users['lifetime_purchases'].mean()):.2f}"
    )

    print(f"Initial average reviews: {initial_users['reviews_written'].mean():.2f}")
    print(f"Final average reviews: {users['reviews_written'].mean():.2f}")
    print(
        f"Review growth: {(users['reviews_written'].mean() - initial_users['reviews_written'].mean()):.2f}"
    )

    print("\nChallenge Completion Rates:")
    completion_rates = recommendation_system.get_challenge_insights()[
        "completion_rates"
    ]
    for challenge, rate in sorted(
        completion_rates.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  {challenge}: {rate*100:.1f}%")

    if results.empty:
        print("\nNo results recorded in simulation.")
        return {}

    if "engaged" in results.columns:
        engagement_rate = results["engaged"].mean() * 100
        print(f"\nOverall Engagement Rate: {engagement_rate:.1f}%")

        segment_engagement = results.groupby("segment")["engaged"].mean() * 100
        print("\nEngagement Rate by Segment:")
        for segment, rate in segment_engagement.sort_values(ascending=False).items():
            print(f"  {segment}: {rate:.1f}%")

        challenge_engagement = results.groupby("challenge")["engaged"].mean() * 100
        print("\nEngagement Rate by Challenge:")
        for challenge, rate in challenge_engagement.sort_values(
            ascending=False
        ).items():
            if challenge is not None:
                print(f"  {challenge}: {rate:.1f}%")

        inactive_users = users[users["completed_challenges"] == 0]
        print(
            f"\nUsers who never completed a challenge: {len(inactive_users)} ({len(inactive_users)/len(users)*100:.1f}%)"
        )

        if not results[results["engaged"]].empty:
            challenge_abandonment = (
                1 - results[results["engaged"]].groupby("challenge")["completed"].mean()
            )
            print("\nChallenges with Highest Abandonment Rate:")
            for challenge, rate in (
                challenge_abandonment.sort_values(ascending=False).head(3).items()
            ):
                if challenge is not None:
                    print(f"  {challenge}: {rate*100:.1f}% abandonment")

    print("\nPurchase Rate by Challenge:")
    if "purchase_made" in results.columns and results["purchase_made"].any():
        challenge_purchase_rates = results.groupby("challenge")["purchase_made"].mean()
        for challenge, rate in challenge_purchase_rates.sort_values(
            ascending=False
        ).items():
            if challenge is not None:
                print(f"  {challenge}: {rate*100:.1f}%")
    else:
        print("  No purchase data available")

    if "review_length" in results.columns and "review_written" in results.columns:
        reviews = results[results["review_written"] == True]
        if not reviews.empty:
            avg_review_length = reviews["review_length"].mean()
            print(f"\nAverage Review Length: {avg_review_length:.1f} characters")

            challenge_review_lengths = reviews.groupby("challenge")[
                "review_length"
            ].mean()
            print("\nAverage Review Length by Challenge:")
            for challenge, length in challenge_review_lengths.sort_values(
                ascending=False
            ).items():
                if challenge is not None:
                    print(f"  {challenge}: {length:.1f} characters")

            segment_review_lengths = reviews.groupby("segment")["review_length"].mean()
            print("\nAverage Review Length by User Segment:")
            for segment, length in segment_review_lengths.sort_values(
                ascending=False
            ).items():
                print(f"  {segment}: {length:.1f} characters")

            if len(reviews) > 1:
                review_length_reward_corr = reviews["review_length"].corr(
                    reviews["reward"]
                )
                print(
                    f"\nCorrelation between Review Length and Reward: {review_length_reward_corr:.2f}"
                )

    print("\nBest Challenges by User Segment:")
    segment_performance = recommendation_system.get_challenge_insights()[
        "segment_performance"
    ]
    for segment, challenges in segment_performance.items():
        if challenges:
            best_challenge = max(challenges.items(), key=lambda x: x[1])
            print(f"  {segment}: {best_challenge[0]} (avg reward: {best_challenge[1]})")

    print("\nFinal Challenge Q-Values:")
    for challenge, q_value in sorted(
        recommendation_system.challenge_q_values.items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"  {challenge}: {q_value:.2f}")

    metrics = {
        "purchase_growth": users["lifetime_purchases"].mean()
        - initial_users["lifetime_purchases"].mean(),
        "review_growth": users["reviews_written"].mean()
        - initial_users["reviews_written"].mean(),
        "best_challenges": {
            s: max(c.items(), key=lambda x: x[1])[0] if c else None
            for s, c in segment_performance.items()
        },
        "completion_rates": completion_rates,
    }

    if "engaged" in results.columns:
        metrics["overall_engagement"] = engagement_rate
        metrics["segment_engagement"] = segment_engagement.to_dict()
        metrics["challenge_engagement"] = challenge_engagement.to_dict()

    if "purchase_made" in results.columns and not results.empty:
        metrics["purchase_rates"] = (
            challenge_purchase_rates.to_dict()
            if not challenge_purchase_rates.empty
            else {}
        )

    if "review_length" in results.columns and "review_written" in results.columns:
        reviews = results[results["review_written"] == True]
        if not reviews.empty:
            avg_review_length = reviews["review_length"].mean()
            metrics["avg_review_length"] = avg_review_length
            metrics["challenge_review_lengths"] = challenge_review_lengths.to_dict()
            metrics["segment_review_lengths"] = segment_review_lengths.to_dict()
            if len(reviews) > 1:
                metrics["review_length_reward_correlation"] = review_length_reward_corr

    return metrics


if __name__ == "__main__":
    np.random.seed(42)
    random.seed(42)

    print(
        "Running Challenge Recommendation System Simulation with Inactive User Handling..."
    )
    recommendation_system, final_users, results = (
        run_challenge_simulation_with_inactive_users(20)
    )

    metrics = analyze_results_with_inactivity(
        recommendation_system, final_users, results
    )

    print("\n--- Inactive User Analysis ---")
    inactive_users = final_users[final_users["completed_challenges"] == 0]

    if not inactive_users.empty:
        print(f"Number of users who never completed a challenge: {len(inactive_users)}")

        inactive_q_values = {}
        for _, user in inactive_users.iterrows():
            user_id = user["user_id"]
            if user_id in recommendation_system.user_challenge_q_values:
                for challenge, q_value in recommendation_system.user_challenge_q_values[
                    user_id
                ].items():
                    if challenge not in inactive_q_values:
                        inactive_q_values[challenge] = []
                    inactive_q_values[challenge].append(q_value)

        print("\nAverage Q-values for challenges assigned to inactive users:")
        for challenge, values in inactive_q_values.items():
            avg_q = sum(values) / len(values) if values else 0
            print(f"  {challenge}: {avg_q:.2f}")

        current_challenges = inactive_users[
            inactive_users["active_challenge"].notnull()
        ]["active_challenge"].value_counts()

        if not current_challenges.empty:
            print("\nCurrent challenges assigned to inactive users:")
            for challenge, count in current_challenges.items():
                print(f"  {challenge}: {count} users")
        else:
            print("\nNo challenges currently assigned to inactive users.")
    else:
        print("All users completed at least one challenge.")

    if not inactive_users.empty:
        inactive_user_id = inactive_users.iloc[0]["user_id"]
        inactive_user_data = final_users[
            final_users["user_id"] == inactive_user_id
        ].iloc[0]

        print(f"\nRecommended challenges for inactive user {inactive_user_id}:")
        try:
            recommendations = recommendation_system.recommend_next_challenges(
                inactive_user_data
            )
            for challenge in recommendations:
                print(f"  - {challenge}")
        except Exception as e:
            print(f"Error generating recommendations: {e}")

    print("\nSimulation complete.")
