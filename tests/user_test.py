import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core import db
from core.models.users import User
from core.libs import helpers

@pytest.fixture(scope='function')
def test_db():
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    db.Model.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    # Patch the global session to use our test session
    old_session = db.session
    db.session = session

    yield session

    # Restore the old session
    db.session = old_session
    session.close()

@pytest.fixture(scope='function')
def test_user(test_db):
    user = User(username='testuser', email='test@example.com')
    test_db.add(user)
    test_db.commit()
    return user

def test_create_user(test_db):
    user = User(username='newuser', email='new@example.com')
    test_db.add(user)
    test_db.commit()

    assert user.id is not None
    assert user.username == 'newuser'
    assert user.email == 'new@example.com'
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

def test_user_representation(test_user):
    assert str(test_user) == '<User \'testuser\'>'

def test_get_by_id(test_db, test_user):
    retrieved_user = User.get_by_id(test_user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id
    assert retrieved_user.username == 'testuser'

def test_get_by_email(test_db, test_user):
    retrieved_user = User.get_by_email('test@example.com')
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id
    assert retrieved_user.email == 'test@example.com'

def test_filter(test_db):
    user1 = User(username='user1', email='user1@example.com')
    user2 = User(username='user2', email='user2@example.com')
    test_db.add_all([user1, user2])
    test_db.commit()

    users = User.filter(User.username.like('user%')).all()
    assert len(users) == 2
    assert set([user.username for user in users]) == set(['user1', 'user2'])

def test_unique_constraint(test_db, test_user):
    user2 = User(username='testuser', email='test2@example.com')
    test_db.add(user2)
    with pytest.raises(Exception):  # This will depend on your specific database
        test_db.commit()

def test_update_user(test_db, test_user):
    original_updated_at = test_user.updated_at

    # Mock the get_utc_now function
    old_get_utc_now = helpers.get_utc_now
    helpers.get_utc_now = lambda: datetime.utcnow() + timedelta(seconds=1)

    test_user.username = 'updateduser'
    test_db.commit()

    assert test_user.username == 'updateduser'
    assert test_user.updated_at > original_updated_at

    # Restore the original get_utc_now function
    helpers.get_utc_now = old_get_utc_now

def test_non_existent_user(test_db):
    non_existent_user = User.get_by_id(999)  # Assuming 999 is not a valid id
    assert non_existent_user is None

    non_existent_user = User.get_by_email('nonexistent@example.com')
    assert non_existent_user is None