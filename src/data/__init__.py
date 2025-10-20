"""Data access layer - Repository Pattern implementations"""

from .repositories import (
    Repository,
    UserRepository,
    PortfolioRepository,
    SessionRepository,
    UsageStatsRepository,
    RepositoryFactory,
)
from .in_memory import (
    InMemoryUserRepository,
    InMemoryPortfolioRepository,
    InMemorySessionRepository,
    InMemoryUsageStatsRepository,
    InMemoryRepositoryFactory,
)
from .sqlite import (
    SqliteUserRepository,
    SqlitePortfolioRepository,
    SqliteSessionRepository,
    SqliteUsageStatsRepository,
    SqliteRepositoryFactory,
)

__all__ = [
    # Interfaces
    'Repository',
    'UserRepository',
    'PortfolioRepository',
    'SessionRepository',
    'UsageStatsRepository',
    'RepositoryFactory',
    # In-Memory Implementations
    'InMemoryUserRepository',
    'InMemoryPortfolioRepository',
    'InMemorySessionRepository',
    'InMemoryUsageStatsRepository',
    'InMemoryRepositoryFactory',
    # SQLite Implementations
    'SqliteUserRepository',
    'SqlitePortfolioRepository',
    'SqliteSessionRepository',
    'SqliteUsageStatsRepository',
    'SqliteRepositoryFactory',
]
