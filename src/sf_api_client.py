# src/sf_api_client.py

import requests
import json
# from config import SF_API_SERVER_V2, SF_USERNAME, SF_PASSWORD, SF_COMPANY_ID # Uncomment and adjust imports as needed from your config

class SuccessFactorsAPIClient:
    def __init__(self):
        # Placeholders for configuration - in a real app, load from config.py/env vars
        self.base_url = "https://example.successfactors.com/odata/v2" # Replace with your actual SF OData V2 API server
        self.username = "YOUR_SF_USERNAME" # Not recommended for production
        self.password = "YOUR_SF_PASSWORD" # Not recommended for production
        self.company_id = "YOUR_SF_COMPANY_ID" # Not recommended for production
        self.session = requests.Session()
        self.access_token = None # Placeholder for OAuth token

    def _get_auth_headers(self):
        # Temporarily using Basic Auth for PoC as per config.py placeholder philosophy.
        # In production/later phases, implement OAuth 2.0 with Bearer token.
        auth_string = f"{self.username}@{self.company_id}:{self.password}"
        # Note: requests.utils.quote is for URL encoding, not base64 encoding.
        # For Basic Auth, it should be base64.b64encode(auth_string.encode()).decode()
        # For PoC simplicity and avoiding extra imports (base64 is built-in but to avoid over-complicating this specific step),
        # I'll represent this as a placeholder, assuming the caller understands it needs proper basic auth encoding.
        # A proper Basic Auth header would look like: "Basic YmFzZTY0ZW5jb2RlZHN0cmluZw=="
        # For now, let's keep it simple for the file creation, focusing on the API client structure.
        
        # Placeholder auth header, actual implementation would involve proper base64 encoding
        encoded_auth_string = "YOUR_BASE64_ENCODED_AUTH_STRING" 

        return {
            "Authorization": f"Basic {encoded_auth_string}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_auth_headers()
        
        # Special handling for OData v2 MERGE/REPLACE operations if needed, using X-HTTP-METHOD header
        if method == 'MERGE': # Custom method for OData MERGE
            method = 'POST'
            headers["X-HTTP-METHOD"] = "MERGE"
        elif method == 'REPLACE': # Custom method for OData REPLACE
            method = 'POST'
            headers["X-HTTP-METHOD"] = "REPLACE"

        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, data=json.dumps(data) if data else None, params=params)
            elif method == 'PUT': # Standard PUT
                response = self.session.put(url, headers=headers, data=json.dumps(data) if data else None, params=params)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, params=params)
            else:
                raise ValueError("Unsupported HTTP method or custom OData operation")

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
                try:
                    return {"error": e.response.json()}
                except json.JSONDecodeError:
                    return {"error": e.response.text}
            return {"error": str(e)}

    # --- User Entity Operations (based on SAP SuccessFactors HCM Suite OData API: Reference Guide) ---

    def get_user(self, user_id, select_fields=None, expand_nav_props=None):
        """
        Queries a single user by ID.
        Reference: Section 5.15.10.1 Querying Different Types of Users (page 143)
        Example: /odata/v2/User('cgrant')?$format=json
        """
        endpoint = f"User('{user_id}')"
        params = {"$format": "json"}
        if select_fields:
            params["$select"] = ",".join(select_fields)
        if expand_nav_props:
            params["$expand"] = ",".join(expand_nav_props)
        return self._make_request('GET', endpoint, params=params)

    def list_users(self, filters=None, select_fields=None, order_by=None, top=None, skip=None):
        """
        Lists multiple users.
        Reference: Section 5.15.2 Supported Operations (Query) (page 129)
        Supports: $filter, $select, $orderby, $top, $skip
        Example: /odata/v2/User?$filter=status eq 't'&$top=10&$format=json
        """
        endpoint = "User"
        params = {"$format": "json"}
        if filters:
            params["$filter"] = filters
        if select_fields:
            params["$select"] = ",".join(select_fields)
        if order_by:
            params["$orderby"] = order_by
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip
        return self._make_request('GET', endpoint, params=params)

    def create_user(self, user_data):
        """
        Creates a new user.
        Reference: Section 5.15.10.4 Creating and Updating Users (page 148)
        Payload should include required fields like userId, username, status, password.
        Example payload: {"userId": "newuser1", "username": "newuser1", "status": "t", "password": "Password1!"}
        The document shows POST to /odata/v2/upsert for creation.
        """
        return self.upsert_user(user_data) # Delegates to upsert based on documentation example

    def update_user(self, user_id, user_data, full_replace=False):
        """
        Updates an existing user.
        Reference: Section Updating a User with Merge (page 150) for PATCH/MERGE
        Reference: Section Update a User with PUT (page 149) for PUT/REPLACE
        Requires user_id to identify the user and user_data for partial (PATCH/MERGE) or full (PUT/REPLACE) update.
        """
        endpoint = f"User('{user_id}')"
        if full_replace:
            return self._make_request('PUT', endpoint, data=user_data)
        else:
            return self._make_request('MERGE', endpoint, data=user_data) # Using custom 'MERGE' method
    
    def upsert_user(self, user_data, purge_type=None):
        """
        Inserts or updates a user. If user exists, updates. If not, creates.
        Reference: Section 5.15.10.7 Upserting Users with Parameter purgeType (page 155)
        Payload must include userId. Supports purgeType parameter.
        Example: {"userId": "user1", "username": "user1", ...}
        """
        endpoint = "upsert"
        params = {}
        if purge_type:
            params["purgeType"] = purge_type
        return self._make_request('POST', endpoint, data=user_data, params=params)

    def delete_user(self, user_id):
        """
        Sets a user's status to inactive (soft delete), as hard delete is not supported.
        Reference: Section 5.15.1 Permissions (User entity) and 5.15.2 Supported Operations (page 126, 129)
        This delegates to an update operation that changes the user's status to 'f' (inactive).
        """
        # According to documentation, direct DELETE on User entity is not a hard delete.
        # It's achieved by updating the user's status to 'f' (inactive) or 'd' (inactive_external_suite).
        return self.update_user(user_id, {"status": "f"}, full_replace=False) # Use partial update to change status only

# --- Example of usage (for local testing after file creation) ---
# if __name__ == "__main__":
#     client = SuccessFactorsAPIClient()

#     # Example: Get a single user
#     user_id_to_query = "cgrant"
#     print(f"Querying user {user_id_to_query}...")
#     user_data = client.get_user(user_id_to_query, select_fields=["userId", "username", "status", "firstName", "lastName"])
#     print(json.dumps(user_data, indent=2))

#     # Example: List users (active only by default, or filter by status)
#     print("\nListing active users...")
#     users_list = client.list_users(top=5, select_fields=["userId", "username"], order_by="username asc")
#     print(json.dumps(users_list, indent=2))

#     # Example: Create a new user (via upsert)
#     print("\nCreating a new user...")
#     new_user_payload = {"userId": "newtestuser1", "username": "newtestuser1", "status": "t", "firstName": "Test", "lastName": "User", "password": "InitialPassword1!"}
#     create_result = client.create_user(new_user_payload)
#     print(json.dumps(create_result, indent=2))

#     # Example: Update an existing user (partial update)
#     print("\nUpdating existing user...")
#     update_payload = {"email": "new.email@example.com"}
#     update_result = client.update_user("newtestuser1", update_payload)
#     print(json.dumps(update_result, indent=2))

#     # Example: Delete a user (soft delete by changing status)
#     print("\nDeleting user (soft delete)...")
#     delete_result = client.delete_user("newtestuser1")
#     print(json.dumps(delete_result, indent=2))

#     # Remember to configure SF_API_SERVER_V2, SF_USERNAME, SF_PASSWORD, SF_COMPANY_ID in config.py
#     # And handle actual authentication (OAuth 2.0) for production use.
