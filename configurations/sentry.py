import sentry_sdk

from configurations.environments import Values

sentry_sdk.init(
    dsn=Values.SENTRY,
    traces_sample_rate=1.0,
    enable_tracing=True,
    send_default_pii=True,
)