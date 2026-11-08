class ScvError(Exception):
    """A user-facing, actionable Sidecaravan error."""


class AuthorizationError(ScvError):
    """The caller did not present the configured team credential."""
