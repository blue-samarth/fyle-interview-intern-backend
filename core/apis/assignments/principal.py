from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, Teacher
from core.apis.teachers.schema import TeacherSchema
from .schema import AssignmentSchema, AssignmentGradeSchema
from core.libs import assertions
from ...libs.exceptions import FyleError
from core.models.assignments import AssignmentStateEnum

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_submitted_graded_assignments(p):
    """Returns list of submitted and graded assignments"""
    assignments = Assignment.list_all_graded_submitted_assignments()
    assignments_data = AssignmentSchema().dump(assignments, many=True)
    return APIResponse.respond(data=assignments_data)

    
@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    if not incoming_payload:
        assertions.assert_valid(None, 'No payload found')
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    assignment = Assignment.get_by_id(grade_assignment_payload.id)
    if not assignment: raise FyleError(400, 'Assignment not found') # bug fix : bad request was changed to not found
    if assignment.state == AssignmentStateEnum.DRAFT:
        raise FyleError(400, 'Assignment is in draft state')
    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)