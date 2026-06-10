# WARNING: This application is INTENTIONALLY VULNERABLE for educational purposes. DO NOT deploy to production.


class Config:
    """Application configuration with INTENTIONAL security issues."""

    # VULN: Hardcoded secret key - should use environment variable
    SECRET_KEY = 'super-secret-key-123'

    # VULN: Hardcoded database password
    DATABASE_PASSWORD = 'admin123'

    # VULN: Hardcoded AWS API key (fake but matches AWS key format for Gitleaks detection)
    API_KEY = 'AKIAIOSFODNN7EXAMPLE'

    # VULN: Debug mode enabled in production config
    DEBUG = True

    # VULN: Hardcoded JWT secret
    JWT_SECRET = 'jwt-secret-key'

    # Database URI
    DATABASE_URI = 'sqlite:///app.db'
