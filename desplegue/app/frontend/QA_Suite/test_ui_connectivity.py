import pytest
import socket
import requests

def test_portal_port_active():
    """Verifica si el puerto del Portal (8103) está escuchando."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8103))
    assert result == 0, "El Portal en el puerto 8103 no está respondiendo."

def test_dashboard_port_active():
    """Verifica si el puerto del Dashboard (8105) está escuchando."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8105))
    assert result == 0, "El Dashboard en el puerto 8105 no está respondiendo."

def test_portal_http_status():
    """Verifica que el Portal retorne un código HTTP 200."""
    try:
        response = requests.get('http://localhost:8103')
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.fail("No se pudo conectar al Portal HTTP.")

def test_dashboard_http_status():
    """Verifica que el Dashboard retorne un código HTTP 200."""
    try:
        response = requests.get('http://localhost:8105')
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.fail("No se pudo conectar al Dashboard HTTP.")
