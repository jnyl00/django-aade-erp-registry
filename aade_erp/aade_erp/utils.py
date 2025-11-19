from httpx import Auth


class BearerAuth(Auth):
    def __init__(self, token_username: str, token_password: str):
        self.token_username = token_username
        self.token_password = token_password

    def auth_flow(self, request):
        if self.token_username is not None:
            request.headers["tokenUsername"] = self.token_username
        if self.token_password is not None:
            request.headers["tokenPassword"] = self.token_password
        yield request
