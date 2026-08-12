import os
import unittest
from unittest.mock import patch
import numpy as np

# Set environment variables for testing before importing anything
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DB_PORT"] = "3306"
os.environ["DB_NAME"] = "task_knowledge_db"
os.environ["DB_USER"] = "task_app"
os.environ["DB_PASSWORD"] = "TaskApp@2026Secure!"
os.environ["JWT_SECRET"] = "testsecret_testsecret_testsecret_testsecret"
os.environ["UPLOAD_DIR"] = "./test_uploads"
os.environ["VECTOR_STORE_PATH"] = "./test_vector_store"

from app.db.session import SessionLocal, engine
from app.models.models import Base, User, Role, RoleName, Task, TaskStatus, ActivityLog, Document
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.ai.document_processor import chunk_text, extract_text
from app.ai.embeddings import embed_texts, embed_query
from app.ai.vector_store import VectorStore, ChunkMetadata
from app.services.activity_service import ActivityLogService
from app.services.task_service import TaskService
from app.services.search_service import SearchService
from app.services.analytics_service import AnalyticsService
from app.services.document_service import DocumentService


class TestBackendAI(unittest.TestCase):
    def test_chunking(self):
        text = "This is a simple text that we want to split into smaller chunks for our tests."
        # Split with chunk size of 15 characters and overlap of 5 characters
        chunks = chunk_text(text, chunk_size=15, overlap=5)
        self.assertTrue(len(chunks) > 0)
        # Ensure it splits on space boundaries
        for chunk in chunks:
            self.assertFalse(chunk.startswith(" "))
            self.assertFalse(chunk.endswith(" "))

    def test_empty_chunking(self):
        self.assertEqual(chunk_text(""), [])
        self.assertEqual(chunk_text("   "), [])

    def test_embeddings_and_vector_store(self):
        # Clean test vector store files if any
        import shutil
        if os.path.exists("./test_vector_store"):
            shutil.rmtree("./test_vector_store")

        # Test empty index first
        store = VectorStore("./test_vector_store")
        self.assertEqual(store.total_vectors, 0)
        self.assertEqual(store.search(np.random.rand(384)), [])

        # Test embedding generation (real MiniLM model)
        texts = ["How can a user complete an assigned task?", "Python web applications with FastAPI."]
        embeddings = embed_texts(texts)
        self.assertEqual(embeddings.shape, (2, 384)) # MiniLM dimension is 384
        
        # Test vector indexing
        meta1 = ChunkMetadata(document_id=1, chunk_index=0, filename="test.txt", text=texts[0])
        meta2 = ChunkMetadata(document_id=2, chunk_index=0, filename="test.txt", text=texts[1])
        store.add(embeddings, [meta1, meta2])
        self.assertEqual(store.total_vectors, 2)

        # Test vector retrieval
        query_vector = embed_query("complete assigned task")
        results = store.search(query_vector, top_k=1)
        self.assertEqual(len(results), 1)
        match_chunk, score = results[0]
        self.assertEqual(match_chunk.document_id, 1)
        self.assertEqual(match_chunk.text, texts[0])
        self.assertTrue(score > 0.3) # Cosine similarity score should be relatively high

        # Clean up
        if os.path.exists("./test_vector_store"):
            shutil.rmtree("./test_vector_store")


class TestDatabaseServices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
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

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        # We start a transaction block for each test so we can roll back and keep DB clean
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.session = SessionLocal(bind=self.connection)

        # Create fresh test users inside this transaction
        self.admin_user = User(
            username="test_admin_unique",
            email="test_admin@example.com",
            password_hash=hash_password("AdminPass123!"),
            role_id=self.admin_role.id,
            is_active=True
        )
        self.regular_user = User(
            username="test_user_unique",
            email="test_user@example.com",
            password_hash=hash_password("UserPass123!"),
            role_id=self.user_role.id,
            is_active=True
        )
        self.session.add(self.admin_user)
        self.session.add(self.regular_user)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.transaction.rollback()
        self.connection.close()

    def test_password_verification(self):
        self.assertTrue(verify_password("AdminPass123!", self.admin_user.password_hash))
        self.assertFalse(verify_password("WrongPass", self.admin_user.password_hash))

    def test_jwt_token_handling(self):
        token = create_access_token(self.regular_user.id)
        payload = decode_access_token(token)
        self.assertEqual(int(payload["sub"]), self.regular_user.id)

    def test_activity_logging_service(self):
        service = ActivityLogService(self.session)
        service.log(
            user_id=self.regular_user.id,
            action="LOGIN",
            details={"ip": "127.0.0.1"}
        )
        
        # Verify the record exists
        log = self.session.query(ActivityLog).filter_by(
            user_id=self.regular_user.id, action="LOGIN"
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.details["ip"], "127.0.0.1")

    def test_task_creation_and_ownership(self):
        task_service = TaskService(self.session)
        
        # Admin creates task
        from app.schemas.schemas import TaskCreate, TaskUpdate
        task_payload = TaskCreate(
            title="Complete technical assessment",
            description="Build modular monolithic project",
            assigned_to=self.regular_user.id
        )
        task = task_service.create_task(task_payload, self.admin_user.id)
        self.assertEqual(task.title, "Complete technical assessment")
        self.assertEqual(task.status, TaskStatus.PENDING)

        # Non-assigned user tries to view/update task (unauthorized check)
        other_user = User(
            username="other_user",
            email="other@example.com",
            password_hash="...",
            role_id=self.user_role.id,
            is_active=True
        )
        self.session.add(other_user)
        self.session.commit()

        with self.assertRaises(PermissionError):
            task_service.get_task(task.id, other_user)

        with self.assertRaises(PermissionError):
            task_service.update_task(task.id, TaskUpdate(status="COMPLETED"), other_user)

        # Assigned user completes task (should log TASK_UPDATE)
        updated_task = task_service.update_task(task.id, TaskUpdate(status="COMPLETED"), self.regular_user)
        self.assertEqual(updated_task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(updated_task.completed_at)

        # Check TASK_UPDATE log was created
        log = self.session.query(ActivityLog).filter_by(
            user_id=self.regular_user.id, action="TASK_UPDATE"
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.entity_id, task.id)

    def test_analytics_service(self):
        task_service = TaskService(self.session)
        from app.schemas.schemas import TaskCreate
        
        # Seed tasks
        task_service.create_task(TaskCreate(title="Task 1", assigned_to=self.regular_user.id), self.admin_user.id)
        task_service.create_task(TaskCreate(title="Task 2", assigned_to=self.regular_user.id), self.admin_user.id)
        
        # Test analytics values
        analytics_service = AnalyticsService(self.session)
        data = analytics_service.get_analytics(self.admin_user)
        self.assertEqual(data["total_tasks"], 2)
        self.assertEqual(data["pending_tasks"], 2)
        self.assertEqual(data["completed_tasks"], 0)


if __name__ == "__main__":
    unittest.main()
