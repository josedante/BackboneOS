#!/usr/bin/env python3
"""
Script de prueba para verificar los endpoints de la API de interactions.
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api/interactions"
ADMIN_URL = "http://localhost:8000/admin"

def test_endpoint(endpoint, description):
    """Prueba un endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Probando: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                print(f"Resultados: {len(data['results'])} items")
                if data['results']:
                    print(f"Primer item: {json.dumps(data['results'][0], indent=2)[:200]}...")
            elif isinstance(data, list):
                print(f"Resultados: {len(data)} items")
                if data:
                    print(f"Primer item: {json.dumps(data[0], indent=2)[:200]}...")
            else:
                print(f"Respuesta: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - Verifica que el backend esté corriendo")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 Probando API de Interactions")
    print("=" * 50)
    
    # Endpoints principales
    endpoints = [
        ("/mediums/", "Mediums - Listado"),
        ("/mediums/choices/", "Mediums - Choices"),
        ("/channels/", "Channels - Listado"),
        ("/channels/choices/", "Channels - Choices"),
        ("/action-types/", "Action Types - Listado"),
        ("/action-types/choices/", "Action Types - Choices"),
        ("/actions/", "Actions - Listado"),
        ("/actions/choices/", "Actions - Choices"),
        ("/agents/", "Agents - Listado"),
        ("/agents/choices/", "Agents - Choices"),
        ("/agents/by_type/?type=browser", "Agents - Por tipo"),
        ("/touchpoint-classes/", "Touchpoint Classes - Listado"),
        ("/touchpoints/", "Touchpoints - Listado"),
        ("/interactions/", "Interactions - Listado"),
        ("/interactions/analytics/", "Interactions - Analytics"),
        ("/interactions/geographic/", "Interactions - Geográficas"),
    ]
    
    for endpoint, description in endpoints:
        test_endpoint(endpoint, description)
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas completadas!")
    print(f"💡 Admin URL: {ADMIN_URL}")

if __name__ == "__main__":
    main()
