from locust import HttpUser, task

class SmokeUser(HttpUser):
    host = "http://localhost:8000"

    @task
    def health(self):
        self.client.get("/health")
