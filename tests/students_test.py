def test_get_assignments_student_1(client, h_student_1):
    response = client.get(
        '/student/assignments',
        headers=h_student_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 1


def test_get_assignments_student_2(client, h_student_2):
    response = client.get(
        '/student/assignments',
        headers=h_student_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 2


def test_post_assignment_null_content(client, h_student_1):
    """
    failure case: content cannot be null
    """

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': None
        })

    assert response.status_code == 400


def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })
    print(response.json)
    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None


def test_submit_and_resubmit_assignment(client, h_student_1):
    # Step 1: Create a new assignment
    content = 'New assignment for submission test'
    create_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })
    assert create_response.status_code == 200
    new_assignment_id = create_response.json['data']['id']

    # Step 2: Submit the assignment
    submit_response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': new_assignment_id,
            'teacher_id': 2
        })

    assert submit_response.status_code == 200

    data = submit_response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2

    # Step 3: Attempt to resubmit the same assignment
    resubmit_response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': new_assignment_id,
            'teacher_id': 2
        })

    assert resubmit_response.status_code == 400
    assert resubmit_response.json['error'] == 'FyleError'
    assert resubmit_response.json['message'] == 'only a draft assignment can be submitted'
