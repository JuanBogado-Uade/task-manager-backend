import pytest
from auth import hash_password, verify_password

def test_hash_password_returns_different_hash():
    """Prueba que al hashear la misma contraseña dos veces devuelve hashes diferentes"""
    password = "test123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2
    assert isinstance(hash1, str)
    assert len(hash1) > 0

def test_hash_password_with_empty_string():
    """Prueba hashear una cadena vacía"""
    password = ""
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0

def test_verify_password_correct():
    """Prueba verificación de contraseña con contraseña correcta"""
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True

def test_verify_password_incorrect():
    """Prueba verificación de contraseña con contraseña incorrecta"""
    password = "test123"
    wrong_password = "wrongpass"
    hashed = hash_password(password)
    assert verify_password(wrong_password, hashed) is False

def test_verify_password_empty():
    """Prueba verificación de contraseña con cadena vacía"""
    password = "test123"
    hashed = hash_password(password)
    assert verify_password("", hashed) is False

def test_verify_password_none():
    """Prueba verificación de contraseña con valores None"""
    with pytest.raises(TypeError):
        verify_password(None, None)

def test_hash_password_none():
    """Prueba hashear una contraseña None"""
    with pytest.raises(TypeError):
        hash_password(None)

def test_verify_password_invalid_hash():
    """Prueba verificación de contraseña con hash inválido"""
    password = "test123"
    invalid_hash = "invalid_hash"
    assert verify_password(password, invalid_hash) is False

def test_long_password():
    """Prueba hashear y verificar una contraseña muy larga"""
    password = "x" * 1000  # Contraseña muy larga
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True

def test_special_characters():
    """Prueba hashear y verificar contraseña con caracteres especiales"""
    password = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True