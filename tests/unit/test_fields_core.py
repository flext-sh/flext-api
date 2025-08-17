"""Tests for fields module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api import (
    FlextAPIFieldCore,
    FlextAPIFields,
    api_key_field,
    bearer_token_field,
    endpoint_path_field,
    http_method_field,
    pipeline_config_field,
    plugin_config_field,
    response_format_field,
    user_role_field,
)


class TestFlextAPIFieldCore:
    """Test cases for FlextAPIFieldCore class."""

    def test_api_key_field_creation(self) -> None:
      """Test creating API key field."""
      field = FlextAPIFieldCore.api_key_field()
      assert field is not None
      # Basic field structure validation
      if "field_type" not in field or hasattr(field, "field_type"):
          msg: str = (
              f"Expected {'field_type'} in {field or hasattr(field, 'field_type')}"
          )
          raise AssertionError(msg)

    def test_api_key_field_with_description(self) -> None:
      """Test creating API key field with custom description."""
      description = "Custom API key description"
      field = FlextAPIFieldCore.api_key_field(description=description)
      assert field is not None

    def test_bearer_token_field_creation(self) -> None:
      """Test creating bearer token field."""
      field = FlextAPIFieldCore.bearer_token_field()
      assert field is not None

    def test_bearer_token_field_with_description(self) -> None:
      """Test creating bearer token field with custom description."""
      description = "Custom bearer token description"
      field = FlextAPIFieldCore.bearer_token_field(description=description)
      assert field is not None

    def test_pipeline_config_field_creation(self) -> None:
      """Test creating pipeline config field."""
      field = FlextAPIFieldCore.pipeline_config_field()
      assert field is not None

    def test_pipeline_config_field_with_description(self) -> None:
      """Test creating pipeline config field with custom description."""
      description = "Custom pipeline config description"
      field = FlextAPIFieldCore.pipeline_config_field(description=description)
      assert field is not None

    def test_plugin_config_field_creation(self) -> None:
      """Test creating plugin config field."""
      field = FlextAPIFieldCore.plugin_config_field()
      assert field is not None

    def test_plugin_config_field_with_description(self) -> None:
      """Test creating plugin config field with custom description."""
      description = "Custom plugin config description"
      field = FlextAPIFieldCore.plugin_config_field(description=description)
      assert field is not None

    def test_user_role_field_creation(self) -> None:
      """Test creating user role field."""
      field = FlextAPIFieldCore.user_role_field()
      assert field is not None

    def test_user_role_field_with_description(self) -> None:
      """Test creating user role field with custom description."""
      description = "Custom user role description"
      field = FlextAPIFieldCore.user_role_field(description=description)
      assert field is not None

    def test_endpoint_path_field_creation(self) -> None:
      """Test creating endpoint path field."""
      field = FlextAPIFieldCore.endpoint_path_field()
      assert field is not None

    def test_endpoint_path_field_with_description(self) -> None:
      """Test creating endpoint path field with custom description."""
      description = "Custom endpoint path description"
      field = FlextAPIFieldCore.endpoint_path_field(description=description)
      assert field is not None

    def test_http_method_field_creation(self) -> None:
      """Test creating HTTP method field."""
      field = FlextAPIFieldCore.http_method_field()
      assert field is not None

    def test_http_method_field_with_description(self) -> None:
      """Test creating HTTP method field with custom description."""
      description = "Custom HTTP method description"
      field = FlextAPIFieldCore.http_method_field(description=description)
      assert field is not None

    def test_response_format_field_creation(self) -> None:
      """Test creating response format field."""
      field = FlextAPIFieldCore.response_format_field()
      assert field is not None

    def test_response_format_field_with_description(self) -> None:
      """Test creating response format field with custom description."""
      description = "Custom response format description"
      field = FlextAPIFieldCore.response_format_field(description=description)
      assert field is not None

    def test_field_creation_with_kwargs(self) -> None:
      """Test field creation with additional kwargs."""
      field = FlextAPIFieldCore.api_key_field(
          description="Test description",
          custom_param="custom_value",
      )
      assert field is not None


class TestFlextAPIFields:
    """Test cases for FlextAPIFields class."""

    def test_authentication_fields_exist(self) -> None:
      """Test authentication fields are available."""
      assert hasattr(FlextAPIFields, "API_KEY")
      assert hasattr(FlextAPIFields, "BEARER_TOKEN")
      assert FlextAPIFields.API_KEY is not None
      assert FlextAPIFields.BEARER_TOKEN is not None

    def test_configuration_fields_exist(self) -> None:
      """Test configuration fields are available."""
      assert hasattr(FlextAPIFields, "PIPELINE_CONFIG")
      assert hasattr(FlextAPIFields, "PLUGIN_CONFIG")
      assert FlextAPIFields.PIPELINE_CONFIG is not None
      assert FlextAPIFields.PLUGIN_CONFIG is not None

    def test_authorization_fields_exist(self) -> None:
      """Test authorization fields are available."""
      assert hasattr(FlextAPIFields, "USER_ROLE")
      assert FlextAPIFields.USER_ROLE is not None

    def test_api_fields_exist(self) -> None:
      """Test API fields are available."""
      assert hasattr(FlextAPIFields, "ENDPOINT_PATH")
      assert hasattr(FlextAPIFields, "HTTP_METHOD")
      assert hasattr(FlextAPIFields, "RESPONSE_FORMAT")
      assert FlextAPIFields.ENDPOINT_PATH is not None
      assert FlextAPIFields.HTTP_METHOD is not None
      assert FlextAPIFields.RESPONSE_FORMAT is not None

    def test_user_management_fields_exist(self) -> None:
      """Test user management fields are available."""
      assert hasattr(FlextAPIFields, "USERNAME")
      assert hasattr(FlextAPIFields, "EMAIL")
      assert hasattr(FlextAPIFields, "PASSWORD")
      assert FlextAPIFields.USERNAME is not None
      assert FlextAPIFields.EMAIL is not None
      assert FlextAPIFields.PASSWORD is not None

    def test_pipeline_fields_exist(self) -> None:
      """Test pipeline fields are available."""
      assert hasattr(FlextAPIFields, "PIPELINE_NAME")
      assert hasattr(FlextAPIFields, "PIPELINE_DESCRIPTION")
      assert hasattr(FlextAPIFields, "PIPELINE_TIMEOUT")
      assert FlextAPIFields.PIPELINE_NAME is not None
      assert FlextAPIFields.PIPELINE_DESCRIPTION is not None
      assert FlextAPIFields.PIPELINE_TIMEOUT is not None

    def test_plugin_fields_exist(self) -> None:
      """Test plugin fields are available."""
      assert hasattr(FlextAPIFields, "PLUGIN_ID")
      assert hasattr(FlextAPIFields, "PLUGIN_VERSION")
      assert hasattr(FlextAPIFields, "PLUGIN_ENABLED")
      assert FlextAPIFields.PLUGIN_ID is not None
      assert FlextAPIFields.PLUGIN_VERSION is not None
      assert FlextAPIFields.PLUGIN_ENABLED is not None

    def test_system_fields_exist(self) -> None:
      """Test system fields are available."""
      assert hasattr(FlextAPIFields, "SYSTEM_STATUS")
      assert hasattr(FlextAPIFields, "LOG_LEVEL")
      assert FlextAPIFields.SYSTEM_STATUS is not None
      assert FlextAPIFields.LOG_LEVEL is not None

    def test_request_response_fields_exist(self) -> None:
      """Test request/response fields are available."""
      assert hasattr(FlextAPIFields, "REQUEST_ID")
      assert hasattr(FlextAPIFields, "CORRELATION_ID")
      assert hasattr(FlextAPIFields, "TIMESTAMP")
      assert FlextAPIFields.REQUEST_ID is not None
      assert FlextAPIFields.CORRELATION_ID is not None
      assert FlextAPIFields.TIMESTAMP is not None


class TestConvenienceFieldBuilders:
    """Test cases for convenience field builder functions."""

    def test_api_key_field_function(self) -> None:
      """Test api_key_field convenience function."""
      field = api_key_field()
      assert field is not None

    def test_api_key_field_function_with_description(self) -> None:
      """Test api_key_field function with custom description."""
      description = "Custom API key"
      field = api_key_field(description=description)
      assert field is not None

    def test_bearer_token_field_function(self) -> None:
      """Test bearer_token_field convenience function."""
      field = bearer_token_field()
      assert field is not None

    def test_bearer_token_field_function_with_description(self) -> None:
      """Test bearer_token_field function with custom description."""
      description = "Custom bearer token"
      field = bearer_token_field(description=description)
      assert field is not None

    def test_pipeline_config_field_function(self) -> None:
      """Test pipeline_config_field convenience function."""
      field = pipeline_config_field()
      assert field is not None

    def test_pipeline_config_field_function_with_description(self) -> None:
      """Test pipeline_config_field function with custom description."""
      description = "Custom pipeline config"
      field = pipeline_config_field(description=description)
      assert field is not None

    def test_plugin_config_field_function(self) -> None:
      """Test plugin_config_field convenience function."""
      field = plugin_config_field()
      assert field is not None

    def test_plugin_config_field_function_with_description(self) -> None:
      """Test plugin_config_field function with custom description."""
      description = "Custom plugin config"
      field = plugin_config_field(description=description)
      assert field is not None

    def test_user_role_field_function(self) -> None:
      """Test user_role_field convenience function."""
      field = user_role_field()
      assert field is not None

    def test_user_role_field_function_with_description(self) -> None:
      """Test user_role_field function with custom description."""
      description = "Custom user role"
      field = user_role_field(description=description)
      assert field is not None

    def test_endpoint_path_field_function(self) -> None:
      """Test endpoint_path_field convenience function."""
      field = endpoint_path_field()
      assert field is not None

    def test_endpoint_path_field_function_with_description(self) -> None:
      """Test endpoint_path_field function with custom description."""
      description = "Custom endpoint path"
      field = endpoint_path_field(description=description)
      assert field is not None

    def test_http_method_field_function(self) -> None:
      """Test http_method_field convenience function."""
      field = http_method_field()
      assert field is not None

    def test_http_method_field_function_with_description(self) -> None:
      """Test http_method_field function with custom description."""
      description = "Custom HTTP method"
      field = http_method_field(description=description)
      assert field is not None

    def test_response_format_field_function(self) -> None:
      """Test response_format_field convenience function."""
      field = response_format_field()
      assert field is not None

    def test_response_format_field_function_with_description(self) -> None:
      """Test response_format_field function with custom description."""
      description = "Custom response format"
      field = response_format_field(description=description)
      assert field is not None

    def test_field_function_with_kwargs(self) -> None:
      """Test field functions with additional kwargs."""
      field = api_key_field(
          description="Test description",
          custom_param="custom_value",
      )
      assert field is not None


class TestFieldsModuleIntegration:
    """Test integration between field classes and functions."""

    def test_field_core_and_function_consistency(self) -> None:
      """Test that field core methods and convenience functions work consistently."""
      # Create fields using both methods
      core_field = FlextAPIFieldCore.api_key_field(description="Core field")
      function_field = api_key_field(description="Function field")

      # Both should create valid field dictionaries
      assert core_field is not None
      assert function_field is not None
      assert isinstance(core_field, dict)
      assert isinstance(function_field, dict)
      if core_field["field_type"] != "api_key":
          msg: str = f"Expected {'api_key'}, got {core_field['field_type']}"
          raise AssertionError(msg)
      assert function_field["field_type"] == "api_key"

    def test_all_convenience_functions_work(self) -> None:
      """Test that all convenience functions can be called successfully."""
      functions = [
          api_key_field,
          bearer_token_field,
          pipeline_config_field,
          plugin_config_field,
          user_role_field,
          endpoint_path_field,
          http_method_field,
          response_format_field,
      ]

      for func in functions:
          field = func()
          assert field is not None

    def test_fields_class_attributes_are_valid(self) -> None:
      """Test that FlextAPIFields class attributes are properly initialized."""
      # Authentication fields
      assert FlextAPIFields.API_KEY is not None
      assert FlextAPIFields.BEARER_TOKEN is not None

      # Configuration fields
      assert FlextAPIFields.PIPELINE_CONFIG is not None
      assert FlextAPIFields.PLUGIN_CONFIG is not None

      # Other core fields
      assert FlextAPIFields.USER_ROLE is not None
      assert FlextAPIFields.ENDPOINT_PATH is not None
      assert FlextAPIFields.HTTP_METHOD is not None
      assert FlextAPIFields.RESPONSE_FORMAT is not None

    def test_type_annotations_coverage(self) -> None:
      """Test type annotations to cover TYPE_CHECKING imports."""
      # Runtime-safe coverage without inline imports
      assert hasattr(FlextAPIFields, "API_KEY")
