import json
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from repositories.url_repository import UrlRepository
from router import route
from services.redirect_service import RedirectService


EXAMPLE_ORIGINAL_URL = "https://youtu.be/xFrGuyw1V8s?si=Biwdg-LYqohj05Px"


def build_event(code: str | None = "Ab3xY9", method: str = "GET") -> dict:
    event = {"httpMethod": method}
    if code is not None:
        event["pathParameters"] = {"codigo": code}
    return event


def parse_body(response: dict) -> dict:
    return json.loads(response["body"])


class RedirectServiceTest(unittest.TestCase):
    def test_valid_code_returns_redirect_and_increments_clicks(self):
        repository = MagicMock()
        repository.find_by_code.return_value = {
            "codigo": "Ab3xY9",
            "url_original": EXAMPLE_ORIGINAL_URL,
            "created_at": "2026-05-16T00:00:00+00:00",
            "clicks": 0,
        }

        response = RedirectService(repository=repository).redirect("Ab3xY9")

        self.assertEqual(response["statusCode"], 302)
        self.assertEqual(response["headers"]["Location"], EXAMPLE_ORIGINAL_URL)
        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response["headers"]["Access-Control-Expose-Headers"], "Location")
        self.assertNotIn("body", response)
        repository.find_by_code.assert_called_once_with("Ab3xY9")
        repository.increment_clicks.assert_called_once_with("Ab3xY9")
        repository.increment_daily_clicks.assert_called_once_with("Ab3xY9", datetime.now(UTC).date().isoformat())

    def test_missing_code_returns_structured_not_found(self):
        repository = MagicMock()
        repository.find_by_code.return_value = None

        response = RedirectService(repository=repository).redirect("Ab3xY9")

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEqual(parse_body(response), {"error": "URL not found", "code": "Ab3xY9"})
        repository.find_by_code.assert_called_once_with("Ab3xY9")
        repository.increment_clicks.assert_not_called()

    def test_router_extracts_code_from_path_parameters(self):
        repository = MagicMock()
        repository.find_by_code.return_value = {
            "codigo": "Ab3xY9",
            "url_original": EXAMPLE_ORIGINAL_URL,
            "created_at": "2026-05-16T00:00:00+00:00",
            "clicks": 0,
        }

        original_init = RedirectService.__init__

        def init_with_repository(self):
            original_init(self, repository=repository)

        RedirectService.__init__ = init_with_repository
        try:
            response = route(build_event())
        finally:
            RedirectService.__init__ = original_init

        self.assertEqual(response["statusCode"], 302)
        repository.find_by_code.assert_called_once_with("Ab3xY9")

    def test_repository_uses_atomic_update_item_to_increment_clicks(self):
        table = MagicMock()
        table.get_item.return_value = {"Item": {"codigo": "Ab3xY9", "url_original": EXAMPLE_ORIGINAL_URL}}
        dynamodb = MagicMock()
        dynamodb.Table.return_value = table

        repository = UrlRepository(table_name="urls", stats_table_name="url_stats", dynamodb_resource=dynamodb)
        item = repository.find_by_code("Ab3xY9")
        repository.increment_clicks("Ab3xY9")
        repository.increment_daily_clicks("Ab3xY9", "2026-05-16")

        self.assertEqual(dynamodb.Table.call_args_list[0].args, ("urls",))
        self.assertEqual(dynamodb.Table.call_args_list[1].args, ("url_stats",))
        table.get_item.assert_called_once_with(Key={"codigo": "Ab3xY9"})
        self.assertEqual(table.update_item.call_args_list[0].kwargs, {
            "Key": {"codigo": "Ab3xY9"},
            "UpdateExpression": "ADD clicks :inc",
            "ExpressionAttributeValues": {":inc": 1},
        })
        self.assertEqual(table.update_item.call_args_list[1].kwargs, {
            "Key": {"codigo": "Ab3xY9", "fecha": "2026-05-16"},
            "UpdateExpression": "ADD clicks :inc",
            "ExpressionAttributeValues": {":inc": 1},
        })
        self.assertEqual(item, {"codigo": "Ab3xY9", "url_original": EXAMPLE_ORIGINAL_URL})

    def test_non_get_method_returns_method_not_allowed(self):
        response = route(build_event(method="POST"))

        self.assertEqual(response["statusCode"], 405)
        self.assertEqual(parse_body(response), {"message": "Method not allowed"})


if __name__ == "__main__":
    unittest.main()
