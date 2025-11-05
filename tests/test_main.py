from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timedelta

client = TestClient(app)

# Constantes para tests
TEST_CREDENTIALS = {
    "user": {
        "correo": "test@mail.com",
        "nombre": "Test User",
        "contraseña": "test123"
    },
    "other_user": {
        "correo": "other@mail.com",
        "nombre": "Other User",
        "contraseña": "test123"
    }
}

# Constante para headers
HEADERS = {"X-User-Mail": TEST_CREDENTIALS["user"]["correo"]}

def test_register_user():
    """Test registro de usuario"""
    response = client.post("/register", json=TEST_CREDENTIALS["user"])
    assert response.status_code in [201, 400]  # 201 si es nuevo, 400 si ya existe
    
    # Registrar segundo usuario para tests
    response = client.post("/register", json=TEST_CREDENTIALS["other_user"])
    assert response.status_code in [201, 400]

def test_login():
    """Test login exitoso"""
    response = client.post("/login", json={
        "correo": TEST_CREDENTIALS["user"]["correo"],
        "contraseña": TEST_CREDENTIALS["user"]["contraseña"],
        "captcha_token": "test_token"  # Agregar token de captcha
    })
    if response.status_code == 422:
        print("Login error:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert "usuario" in data
    assert data["nombre"] == TEST_CREDENTIALS["user"]["nombre"]

def test_create_project():
    """Test crear proyecto"""
    response = client.post(
        "/proyectos",
        headers=HEADERS,  # Usar header correcto
        json={"nombre": "Proyecto Test", "descripcion": "Descripción de prueba"}
    )
    if response.status_code == 422:
        print("Create project error:", response.json())
    assert response.status_code == 201
    data = response.json()
    assert "id_proyecto" in data
    return data["id_proyecto"]

def test_list_projects():
    """Test listar proyectos"""
    # proyecto_id = test_create_project()
    response = client.get(
        "/proyectos",
        headers={"x-user-mail": TEST_CREDENTIALS["user"]["correo"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(p["nombre_proyecto"] == "Proyecto Test" for p in data)

def test_add_project_member():
    """Test agregar miembro a proyecto"""
    proyecto_id = test_create_project()
    response = client.post(
        f"/proyectos/{proyecto_id}/integrantes",
        headers=HEADERS,
        json={  # Formato correcto según IntegrantesAddRequest
            TEST_CREDENTIALS["other_user"]["correo"]: "editor"
        }
    )
    if response.status_code == 422:
        print("Add member error:", response.json())
    assert response.status_code == 201
    data = response.json()
    assert "integrantes" in data
    assert len(data["integrantes"]) == 1

def test_create_task():
    """Test crear tarea"""
    proyecto_id = test_create_project()
    response = client.post(
        f"/proyectos/{proyecto_id}/tareas",
        headers={"x-user-email": TEST_CREDENTIALS["user"]["correo"]},
        json={
            "titulo": "Tarea Test",
            "descripcion": "Descripción tarea test"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id_tarea" in data
    return proyecto_id, data["id_tarea"]

def test_list_tasks():
    """Test listar tareas"""
    proyecto_id, _ = test_create_task()
    response = client.get(
        f"/proyectos/{proyecto_id}/tareas",
        headers={"x-user-mail": TEST_CREDENTIALS["user"]["correo"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["titulo"] == "Tarea Test"

def test_update_task_status():
    """Test actualizar estado de tarea"""
    proyecto_id, tarea_id = test_create_task()
    response = client.put(
        f"/proyectos/{proyecto_id}/tareas/{tarea_id}/estado",
        headers={"x-user-mail": TEST_CREDENTIALS["user"]["correo"]},
        json={"estado": "completado"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "completado"

def test_list_project_members():
    """Test listar miembros de proyecto"""
    proyecto_id = test_create_project()
    test_add_project_member()  # Agregar un miembro primero
    response = client.get(
        f"/proyectos/{proyecto_id}/integrantes",
        headers={"x-user-mail": TEST_CREDENTIALS["user"]["correo"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(m["correo"] == TEST_CREDENTIALS["user"]["correo"] for m in data)

def test_unauthorized_access():
    """Test accesos no autorizados"""
    response = client.get(
        "/proyectos",
        headers={"x-user-mail": "nonexistent@mail.com"}
    )
    assert response.status_code == 404

def test_delete_task():
    """Test eliminar tarea"""
    proyecto_id, tarea_id = test_create_task()
    response = client.delete(
        f"/proyectos/{proyecto_id}/tareas/{tarea_id}",
        headers={"x-user-mail": TEST_CREDENTIALS["user"]["correo"]}
    )
    assert response.status_code == 200

def test_delete_project():
    """Test eliminar proyecto"""
    proyecto_id = test_create_project()
    response = client.delete(
        f"/proyectos/{proyecto_id}",
        headers={"x-user-mail": TEST_CREDENTIALS["user"]["correo"]}
    )
    assert response.status_code == 200