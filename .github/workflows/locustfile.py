import random
from locust import HttpUser, task, between

class RAGSystemUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def query_rag_system(self):
        prompt = f"這是一個測試提示 {random.randint(1, 1000)}"
        self.client.post("/query", json={"prompt": prompt})

    @task(2)
    def search_prompts(self):
        query = f"測試 {random.randint(1, 100)}"
        self.client.get(f"/prompts/search?query={query}")

    @task(1)
    def submit_feedback(self):
        response_id = random.randint(1, 100)  
        user_rating = random.randint(1, 5)
        comments = f"這是一個測試評論 {random.randint(1, 1000)}"
        self.client.post("/feedback", json={
            "response_id": response_id,
            "user_rating": user_rating,
            "comments": comments
        })

    @task(1)
    def get_responses(self):
        self.client.get("/responses")

    @task(1)
    def get_feedbacks(self):
        self.client.get("/feedbacks")

    @task(1)
    def analyze_ab_testing(self):
        self.client.get("/analyze")
