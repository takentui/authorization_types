#!/usr/bin/env python3
"""
Keycloak initialization script.
Sets up realm, client, and default users for development.
"""

import requests
import time
import json
import sys
from typing import Dict, Any


class KeycloakInitializer:
    """Initialize Keycloak for development."""

    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.realm_name = "master"
        self.client_id = "fastapi-app"
        self.access_token = None

    def wait_for_keycloak(self, max_attempts: int = 30) -> bool:
        """Wait for Keycloak to be ready."""
        print("Waiting for Keycloak to start...")

        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.server_url}", timeout=5)
                if response.status_code == 200:
                    print("Keycloak is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass

            print(f"Attempt {attempt + 1}/{max_attempts} - Keycloak not ready yet...")
            time.sleep(5)

        print("Keycloak failed to start within timeout period")
        return False

    def get_admin_token(self) -> bool:
        """Get admin access token."""
        url = f"{self.server_url}/realms/master/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": self.admin_username,
            "password": self.admin_password,
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            print("Admin token obtained successfully")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Failed to get admin token: {e}")
            return False

    def create_client(self) -> bool:
        """Create FastAPI client in Keycloak."""
        url = f"{self.server_url}/admin/realms/{self.realm_name}/clients"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        client_data = {
            "clientId": self.client_id,
            "name": "FastAPI Application",
            "description": "FastAPI application client",
            "enabled": True,
            "publicClient": False,
            "standardFlowEnabled": True,
            "directAccessGrantsEnabled": True,
            "serviceAccountsEnabled": True,
            "clientAuthenticatorType": "client-secret",
            "secret": "your-client-secret",
            "redirectUris": ["http://localhost:8000/*"],
            "webOrigins": ["http://localhost:8000"],
        }

        try:
            # Check if client already exists
            get_response = requests.get(
                f"{url}?clientId={self.client_id}", headers=headers
            )

            if get_response.status_code == 200 and get_response.json():
                print(f"Client {self.client_id} already exists")
                return True

            # Create client
            response = requests.post(url, headers=headers, json=client_data)
            response.raise_for_status()

            print(f"Client {self.client_id} created successfully")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Failed to create client: {e}")
            return False

    def create_test_user(self, username: str, password: str, email: str) -> bool:
        """Create a test user."""
        url = f"{self.server_url}/admin/realms/{self.realm_name}/users"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        user_data = {
            "username": username,
            "email": email,
            "enabled": True,
            "credentials": [
                {"type": "password", "value": password, "temporary": False}
            ],
        }

        try:
            # Check if user already exists
            get_response = requests.get(f"{url}?username={username}", headers=headers)

            if get_response.status_code == 200 and get_response.json():
                print(f"User {username} already exists")
                return True

            # Create user
            response = requests.post(url, headers=headers, json=user_data)
            response.raise_for_status()

            print(f"User {username} created successfully")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Failed to create user {username}: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize Keycloak with required configuration."""
        print("Starting Keycloak initialization...")

        if not self.wait_for_keycloak():
            return False

        if not self.get_admin_token():
            return False

        if not self.create_client():
            return False

        # Create test users
        test_users = [
            ("admin", "password", "admin@example.com"),
            ("testuser", "password", "test@example.com"),
        ]

        for username, password, email in test_users:
            if not self.create_test_user(username, password, email):
                return False

        print("Keycloak initialization completed successfully!")
        return True


def main():
    """Main function."""
    initializer = KeycloakInitializer()

    if not initializer.initialize():
        print("Keycloak initialization failed!")
        sys.exit(1)

    print("Keycloak is ready for use!")


if __name__ == "__main__":
    main()
