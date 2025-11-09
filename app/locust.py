from locust import HttpUser, task, between
import random

class InventoryUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        # Fetch available product IDs once when each simulated user starts
        resp = self.client.get("/products")
        if resp.status_code == 200 and isinstance(resp.json(), list):
            self.products = [p["id"] for p in resp.json()]
        else:
            self.products = []

    @task(4)
    def get_products(self):
        self.client.get("/products")

    @task(1)
    def create_order(self):
        if not self.products:
            print("⚠️ No products found, skipping order creation")
            return

        product_id = random.choice(self.products)
        payload = {
            "product_id": product_id,
            "quantity": random.randint(1,2),
            "status": "PENDING"
        }

        response = self.client.post("/orders/create", json=payload)
        # if response.status_code != 201:
        #     print(f"❌ Order creation failed: {response.status_code}, {response.text}")
        if response.status_code not in (201, 409):  # 409 is OK for load test
            print(f"❌ Unexpected error: {response.status_code}, {response.text}")
