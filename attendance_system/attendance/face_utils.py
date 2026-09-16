import numpy as np
from insightface.app import FaceAnalysis
from employees.models import Employee

face_app = FaceAnalysis(providers=["CPUExecutionProvider"])

face_app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

def recognize_faces(frame):
    faces = face_app.get(frame)
    employees = Employee.objects.exclude(face_encoding__isnull=True)
    matches = []

    for face in faces:
        current_embedding = face.embedding
        best_employee = None
        best_similarity = 0.0

        for employee in employees:
            db_embedding = np.array(
                employee.face_encoding,
                dtype=np.float32
            )

            similarity = (
                np.dot(current_embedding,db_embedding)
                /
                (np.linalg.norm(current_embedding)* np.linalg.norm(db_embedding))
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_employee = employee

        # Face recognized

        if (best_employee is not None and best_similarity > 0.65):
            matches.append({
                "employee": best_employee,
                "recognized": True,
                "bbox": (
                    face.bbox
                    .astype(int)
                    .tolist()
                ),
                "similarity": round(float(best_similarity), 3)
            })
            print(f"Matched: " f"{best_employee.employee_id} " f"({best_similarity:.3f})")

        # Face unknown

        else:
            matches.append({
                "employee": None,
                "recognized": False,
                "bbox": (
                    face.bbox
                    .astype(int)
                    .tolist()
                ),
                "similarity": round(float(best_similarity), 3)
            })

            print(f"Unknown Face " f"({best_similarity:.3f})")
    return matches