from task_service import CameraClient
from utils.image import image_to_base64

def set_face_service(req):
    # 1. Convert image
    image_b64 = image_to_base64(req.image)

    # 2. Chuẩn hóa info cho đầu ghi
    info = {
        "group_id": req.group_id,
        "name": req.name,
        "image": image_b64,
        "count": req.count,
        "sex": req.sex,
        "age": req.age,
        "nation": req.nation,
        "email": req.email,
        "phone": req.phone
    }

    # 3. Login đầu ghi
    cam = CameraClient(
        ip="192.168.100.119",
        user="admin",
        pwd="Batek@abcd"
    )

    if not cam.login():
        raise Exception("Login camera failed")

    # 4. Add face
    resp = cam.add_face(info)

    if resp.status_code != 200:
        raise Exception(resp.text)

    return resp.json()
