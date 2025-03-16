from locust import HttpUser, between, task

class WebsiteUser(HttpUser):
    wait_time = between(5, 9)
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(5, 15)  # Wait time between requests

    @task
    def index_page(self):
        self.client.get("/")

    @task(3)
    def upload_file(self):
        with open("test_data.csv", "rb") as file:
            self.client.post("/", files={"file": file})

    @task(2)
    def activity_percentage(self):
        self.client.post("/activity_percentage", data={"user": "username", "activity": "typing"})

    @task(4)
    def get_heatmap(self):
        self.client.get("/get_heatmap")
 