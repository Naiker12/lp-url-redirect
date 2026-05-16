import json
from datetime import UTC, datetime
from http import HTTPStatus

from repositories.url_repository import UrlRepository


class RedirectService:
    def __init__(self, repository: UrlRepository | None = None):
        self.repository = repository or UrlRepository()

    def redirect(self, code: str | None) -> dict:
        if not code:
            return self._not_found(code)

        record = self.repository.find_by_code(code)
        if record is None:
            return self._not_found(code)

        self.repository.increment_clicks(code)
        self.repository.increment_daily_clicks(code, datetime.now(UTC).date().isoformat())

        return {
            "statusCode": int(HTTPStatus.FOUND),
            "headers": {
                "Location": record["url_original"],
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "Location",
            },
        }

    @staticmethod
    def _not_found(code: str | None) -> dict:
        return {
            "statusCode": int(HTTPStatus.NOT_FOUND),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": "URL not found", "code": code}),
        }
