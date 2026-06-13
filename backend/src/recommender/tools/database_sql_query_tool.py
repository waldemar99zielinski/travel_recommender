from __future__ import annotations

from collections.abc import Sequence

from langchain_community.tools.sql_database.tool import InfoSQLDatabaseTool
from langchain_community.tools.sql_database.tool import ListSQLDatabaseTool
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import BaseTool
from sqlalchemy.engine import Engine

from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_database_sql_tools(engine: Engine) -> Sequence[BaseTool]:
    """Create raw SQL database tools ready to inject into a BaseReActAgent.

    Returns three tools that let a ReAct agent discover tables, inspect
    schemas, and run SELECT queries against the PostgreSQL database::

        from recommender.tools import create_database_sql_tools

        agent = MyAgent.builder() \\
            .with_tools(*create_database_sql_tools(engine)) \\
            .build()
    """
    db = SQLDatabase(engine)

    tools: list[BaseTool] = [
        ListSQLDatabaseTool(db=db),
        InfoSQLDatabaseTool(db=db),
        QuerySQLDatabaseTool(db=db),
    ]

    logger.verbose("Database SQL tools created: list_tables, schema, query")
    return tools
