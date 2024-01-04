from tapvalidator.models.tap_service import TAPService, TAPEndpoints


class TestTAPService:
    #  TAPService can be created with a valid URL
    def test_create_tap_service_with_valid_url(self):
        url = "http://example.com"
        tap_service = TAPService(url)

        assert tap_service.url == url
        assert tap_service.name != ""
        assert isinstance(tap_service.endpoints, TAPEndpoints)

    #  TAPService can be created with a valid URL and name
    def test_create_tap_service_with_valid_url_and_name(self):
        url = "http://example.com"
        name = "Test Service"
        tap_service = TAPService(url, name)

        assert tap_service.url == url
        assert tap_service.name == name
        assert isinstance(tap_service.endpoints, TAPEndpoints)

    #  TAPService name is generated if not provided
    def test_tap_service_name_generation(self):
        url = "http://example.com"
        tap_service = TAPService(url)

        assert tap_service.url == url
        assert tap_service.name != ""
        assert isinstance(tap_service.endpoints, TAPEndpoints)

    #  TAPService can be created with an empty URL
    def test_create_tap_service_with_empty_url(self):
        url = ""
        tap_service = TAPService(url)
        assert tap_service.url == ""

    #  TAPService can be created with an invalid URL
    def test_create_tap_service_with_invalid_url(self):
        url = "invalid_url"
        tap_service = TAPService(url)

        assert tap_service.url == url
        assert tap_service.name != ""
        assert isinstance(tap_service.endpoints, TAPEndpoints)

    #  TAPService name can be an empty string
    def test_create_tap_service_with_empty_name(self):
        url = "http://example.com"
        name = ""
        tap_service = TAPService(url, name)

        assert tap_service.url == url
        assert isinstance(tap_service.endpoints, TAPEndpoints)

    def test_create_tap_endpoints(self):
        url = "http://example.com"
        tap_service = TAPService(url)

        assert tap_service.endpoints.tables == f"{url}/tables"
        assert tap_service.endpoints.asynchronous == f"{url}/async"
        assert tap_service.endpoints.synchronous == f"{url}/sync"
        assert tap_service.endpoints.capabilities == f"{url}/capabilities"
        assert tap_service.endpoints.availability == f"{url}/availability"
