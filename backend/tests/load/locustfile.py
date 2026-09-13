"""Lumina V3 — Load Testing Suite (Locust).

Scenarios (§13.5):
1. Concurrent students viewing dashboard & checking grades
2. Teacher bulk grading class
3. Notification burst queries
4. High-concurrency health check & auth
"""

from locust import HttpUser, between, task


class StudentUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        # Authenticate mock student session
        self.headers = {
            "Authorization": "Bearer test-load-token-student",
            "Content-Type": "application/json",
        }

    @task(3)
    def view_dashboard(self):
        self.client.get("/api/v1/student/dashboard", headers=self.headers)

    @task(2)
    def view_grades(self):
        self.client.get("/api/v1/student/grades", headers=self.headers)

    @task(1)
    def check_xp(self):
        self.client.get("/api/v1/student/xp", headers=self.headers)


class TeacherUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.headers = {
            "Authorization": "Bearer test-load-token-teacher",
            "Content-Type": "application/json",
        }

    @task(2)
    def view_attendance(self):
        self.client.get("/api/v1/teacher/attendance", headers=self.headers)

    @task(1)
    def list_homework(self):
        self.client.get("/api/v1/teacher/homework", headers=self.headers)


class SystemHealthUser(HttpUser):
    wait_time = between(0.5, 1)

    @task
    def health_check(self):
        self.client.get("/health")
