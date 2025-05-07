# pylint: disable=no-member
import pytest
import allure
from pages.commure_template_page import CommureTemplatePage
from testcases.base_test import BaseTest
from utils.helper import validate_response_schema
from utils.request_handler import RequestHandler


class TestCommureTemplate(BaseTest):
    def setup_class(self):
        """
        Set up initial data for Commure Template tests.
        """
        self.commure_template_page = CommureTemplatePage()
        self.user_name = pytest.configs.get_config("appointment_api_provider")  # ("commure_template_email")
        self.password = pytest.configs.get_config("all_provider_password")

        # Generate auth_token dynamically
        self.token = RequestHandler.get_auth_token(user_name=self.user_name, password=self.password)
        print(f"Auth Token: {self.token}")

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_commure_template(self):
        """
        Test GET /textexpander/v1/athelas/templates to retrieve Commure templates.
        """
        email = "sakibul_dev_rt_provider_01@augmedix.com"
        response = self.commure_template_page.commure_template_request(
            method="GET",
            email=email,
            auth_token=self.token
        )
        response_json = response.json()
        print(f"Response: {response_json}")

        # Validate the response
        assert response.status_code == 200, "GET /textexpander/v1/athelas/templates failed"
        validate_response_schema(response_json, "resources/json_schema/get_commure_template.json")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_commure_template_with_invalid_email(self):
        """
        Test GET /textexpander/v1/athelas/templates with an invalid email.
        """
        invalid_email = "invalid_email@augmedix.com"
        response = self.commure_template_page.commure_template_request(
            method="GET",
            email=invalid_email,
            auth_token=self.token
        )
        print(f"Response: {response.text}")

        # Validate the response
        assert response.status_code == 500, "Expected 500 Internal Server Error for invalid email"
        response_json = response.json()
        assert response_json["status"] == 500, "Expected status 500 in the response"
        assert response_json["error"] == "Internal Server Error", "Expected 'Internal Server Error' in the response"
        assert "Account with email INVALID_EMAIL@AUGMEDIX.COM does not exist" in response_json["message"], "Expected error message about invalid email"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_commure_template_with_missing_token(self):
        """
        Test GET /textexpander/v1/athelas/templates without an authorization token.
        """
        response = self.commure_template_page.commure_template_request(
            method="GET",
            email=self.user_name,
            auth_token=None  # No token provided
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Validate the response status code
        assert response.status_code == 401, "Expected 401 Unauthorized for missing token"

        # Attempt to parse the response as JSON
        try:
            response_json = response.json()
            assert "error" in response_json, "Error message not found in response JSON"
            assert response_json["error"] == "Unauthorized", "Expected 'Unauthorized' error in response JSON"
        except ValueError:
            # Handle non-JSON responses
            pytest.fail("Response is not in JSON format")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_commure_template_with_expired_token(self):
        """
        Test GET /textexpander/v1/athelas/templates with an expired token.
        """
        expired_token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjb20uYXVnbWVkaXgiLCJleHAiOjE2MDAwMDAwMDAsInVpZCI6OTg5OTgzNzM0LCJybHMiOlsiU0NSSUJFIl0sImd1aWQiOiJzY3JpYmUtMmNkMmIyNDctNWE3MC00MDk1LTgyZDctYjkwYWMzNmI3ZTg2In0.invalid_signature"
        response = self.commure_template_page.commure_template_request(
            method="GET",
            email=self.user_name,
            auth_token=expired_token
        )
        print(f"Response: {response.text}")

        # Validate the response
        assert response.status_code == 401, "Expected 401 for expired token"
        # Attempt to parse the response as JSON
        try:
            response_json = response.json()
            assert "error" in response_json, "Error message not found in response JSON"
            assert response_json["error"] == "Unauthorized", "Expected 'Unauthorized' error in response JSON"
        except ValueError:
            # Handle non-JSON responses
            pytest.fail("Response is not in JSON format")
            
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_commure_template_with_empty_email(self):
        """
        Test GET /textexpander/v1/athelas/templates with an empty email.
        """
        empty_email = ""
        response = self.commure_template_page.commure_template_request(
            method="GET",
            email=empty_email,
            auth_token=self.token
        )
        print(f"Response: {response.text}")

        # Validate the response
        assert response.status_code == 500, "Expected 500 Internal Server Error for empty email"
        response_json = response.json()
        assert response_json["status"] == 500, "Expected status 500 in the response"
        assert response_json["error"] == "Internal Server Error", "Expected 'Internal Server Error' in the response"
        assert "Account with email  does not exist" in response_json["message"], "Expected error message about missing email"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_get_commure_template_with_sql_injection(self):
        """
        Test GET /textexpander/v1/athelas/templates with SQL injection in the email parameter.
        """
        sql_injection_email = "' OR 1=1; --"
        response = self.commure_template_page.commure_template_request(
            method="GET",
            email=sql_injection_email,
            auth_token=self.token
        )
        print(f"Response: {response.text}")

        # Validate the response
        assert response.status_code in [400, 403], "Expected 400 or 403 for SQL injection attempt"
        assert "error" in response.json(), "Error message not found in response"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_get_commure_template_with_xss_attack(self):
        """
        Test GET /textexpander/v1/athelas/templates with XSS attack in the email parameter.
        """
        xss_attack_email = "<script>alert('XSS')</script>"
        response = self.commure_template_page.commure_template_request(
            method="GET",
            email=xss_attack_email,
            auth_token=self.token
        )
        print(f"Response: {response.text}")

        # Validate the response
        assert response.status_code in [400, 403], "Expected 400 or 403 for XSS attack attempt"
        assert "error" in response.json(), "Error message not found in response"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_not_allowed(self):
        """
        Test POST method on GET-only endpoint to ensure method is not allowed.
        """
        response = self.commure_template_page.commure_template_request(
            method="POST",
            email=self.user_name,
            auth_token=self.token
        )
        print(f"Response: {response.text}")

        # Validate the response
        assert response.status_code == 405, "Expected 405 Method Not Allowed for POST request"
        assert "error" in response.json(), "Error message not found in response"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_not_allowed(self):
        """
        Test PUT method on GET-only endpoint to ensure method is not allowed.
        """
        response = self.commure_template_page.commure_template_request(
            method="PUT",
            email=self.user_name,
            auth_token=self.token
        )
        print(f"Response: {response.text}")

        # Validate the response
        assert response.status_code == 405, "Expected 405 Method Not Allowed for PUT request"
        assert "error" in response.json(), "Error message not found in response"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_not_allowed(self):
        """
        Test DELETE method on GET-only endpoint to ensure method is not allowed.
        """
        response = self.commure_template_page.commure_template_request(
            method="DELETE",
            email=self.user_name,
            auth_token=self.token
        )
        print(f"Response: {response.text}")

        # Validate the response
        assert response.status_code == 405, "Expected 405 Method Not Allowed for DELETE request"
        assert "error" in response.json(), "Error message not found in response"