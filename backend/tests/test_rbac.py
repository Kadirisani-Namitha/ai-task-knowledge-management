import os
import unittest
from fastapi.testclient import TestClient

# Set environment variables before app imports
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DB_PORT"] = "3306"
os.environ["DB_NAME"] = "task_knowledge_db"
os.environ["DB_USER"] = "task_app"
os.environ["DB_PASSWORD"] = "TaskApp@2026Secure!"

from main import app
from app.db.session import SessionLocal
from app.models.models import User, Role, RoleName, Task, Document, ActivityLog
from app.core.security import hash_password, create_access_token


def _clean_rbac_test_data(db):
    test_users = db.query(User).filter(User.username.in_(["rbac_admin_test", "rbac_user1_test", "rbac_user2_test"])).all()
    if test_users:
        user_ids = [u.id for u in test_users]
        db.query(ActivityLog).filter(ActivityLog.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(Document).filter(Document.uploaded_by.in_(user_ids)).delete(synchronize_session=False)
        db.query(Task).filter((Task.created_by.in_(user_ids)) | (Task.assigned_to.in_(user_ids))).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
        db.commit()


class TestRBAC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        # Clean pre-existing test data safely handling foreign key constraints
        _clean_rbac_test_data(cls.db)

        # Find or create roles
        cls.admin_role = cls.db.query(Role).filter_by(name=RoleName.ADMIN.value).first()
        if not cls.admin_role:
            cls.admin_role = Role(name=RoleName.ADMIN.value)
            cls.db.add(cls.admin_role)
            cls.db.commit()
            cls.db.refresh(cls.admin_role)

        cls.user_role = cls.db.query(Role).filter_by(name=RoleName.USER.value).first()
        if not cls.user_role:
            cls.user_role = Role(name=RoleName.USER.value)
            cls.db.add(cls.user_role)
            cls.db.commit()
            cls.db.refresh(cls.user_role)

        # Create Admin User
        cls.admin = User(
            username="rbac_admin_test",
            email="admin_rbac_test@example.com",
            password_hash=hash_password("AdminPass123!"),
            role_id=cls.admin_role.id,
            is_active=True,
        )

        # Create Regular User 1
        cls.user1 = User(
            username="rbac_user1_test",
            email="user1_rbac_test@example.com",
            password_hash=hash_password("UserPass123!"),
            role_id=cls.user_role.id,
            is_active=True,
        )

        # Create Regular User 2
        cls.user2 = User(
            username="rbac_user2_test",
            email="user2_rbac_test@example.com",
            password_hash=hash_password("UserPass123!"),
            role_id=cls.user_role.id,
            is_active=True,
        )

        cls.db.add(cls.admin)
        cls.db.add(cls.user1)
        cls.db.add(cls.user2)
        cls.db.commit()

        cls.db.refresh(cls.admin)
        cls.db.refresh(cls.user1)
        cls.db.refresh(cls.user2)

        # Create Auth Headers
        admin_token = create_access_token(cls.admin.id)
        user1_token = create_access_token(cls.user1.id)
        user2_token = create_access_token(cls.user2.id)

        cls.admin_headers = {"Authorization": f"Bearer {admin_token}"}
        cls.user1_headers = {"Authorization": f"Bearer {user1_token}"}
        cls.user2_headers = {"Authorization": f"Bearer {user2_token}"}

    @classmethod
    def tearDownClass(cls):
        try:
            _clean_rbac_test_data(cls.db)
        except Exception:
            cls.db.rollback()
        finally:
            cls.db.close()

    def test_1_admin_create_task_succeeds(self):
        res = self.client.post(
            "/api/v1/tasks",
            json={"title": "RBAC Admin Task", "assigned_to": self.user1.id},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["title"], "RBAC Admin Task")

    def test_2_user_create_task_returns_403(self):
        res = self.client.post(
            "/api/v1/tasks",
            json={"title": "RBAC User Task"},
            headers=self.user1_headers,
        )
        self.assertEqual(res.status_code, 403)

    def test_3_admin_upload_document_succeeds(self):
        file_content = b"Sample text for RBAC test document upload."
        res = self.client.post(
            "/api/v1/documents/upload",
            files={"file": ("test_rbac.txt", file_content, "text/plain")},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 201)

    def test_4_user_upload_document_returns_403(self):
        file_content = b"Unauthorized upload test."
        res = self.client.post(
            "/api/v1/documents/upload",
            files={"file": ("test_rbac.txt", file_content, "text/plain")},
            headers=self.user1_headers,
        )
        self.assertEqual(res.status_code, 403)

    def test_5_admin_assign_task_succeeds(self):
        res = self.client.post(
            "/api/v1/tasks",
            json={"title": "RBAC Assigned Task", "assigned_to": self.user1.id},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["assigned_to"], self.user1.id)

    def test_6_user_assign_task_returns_403(self):
        res = self.client.post(
            "/api/v1/tasks",
            json={"title": "RBAC Attempted Assign", "assigned_to": self.user2.id},
            headers=self.user1_headers,
        )
        self.assertEqual(res.status_code, 403)

    def test_7_user_view_own_assigned_tasks_succeeds(self):
        # Admin creates task assigned to user1
        self.client.post(
            "/api/v1/tasks",
            json={"title": "RBAC User 1 Task", "assigned_to": self.user1.id},
            headers=self.admin_headers,
        )
        # Admin creates task assigned to user2
        self.client.post(
            "/api/v1/tasks",
            json={"title": "RBAC User 2 Task", "assigned_to": self.user2.id},
            headers=self.admin_headers,
        )

        res = self.client.get("/api/v1/tasks", headers=self.user1_headers)
        self.assertEqual(res.status_code, 200)
        tasks = res.json()
        self.assertTrue(all(t["assigned_to"] == self.user1.id for t in tasks))

    def test_8_user_complete_own_assigned_task_succeeds(self):
        create_res = self.client.post(
            "/api/v1/tasks",
            json={"title": "RBAC User Task to Complete", "assigned_to": self.user1.id},
            headers=self.admin_headers,
        )
        task_id = create_res.json()["id"]

        update_res = self.client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"status": "completed"},
            headers=self.user1_headers,
        )
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["status"].upper(), "COMPLETED")

    def test_9_user_modify_other_user_task_returns_403(self):
        create_res = self.client.post(
            "/api/v1/tasks",
            json={"title": "RBAC User 2 Task Modify Test", "assigned_to": self.user2.id},
            headers=self.admin_headers,
        )
        task_id = create_res.json()["id"]

        # User 1 attempts to complete User 2's task
        update_res = self.client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"status": "completed"},
            headers=self.user1_headers,
        )
        self.assertEqual(update_res.status_code, 403)

    def test_10_missing_or_invalid_jwt_returns_401(self):
        res = self.client.get("/api/v1/tasks")
        self.assertEqual(res.status_code, 401)

        invalid_headers = {"Authorization": "Bearer invalid.jwt.token"}
        res2 = self.client.get("/api/v1/tasks", headers=invalid_headers)
        self.assertEqual(res2.status_code, 401)


if __name__ == "__main__":
    unittest.main()
