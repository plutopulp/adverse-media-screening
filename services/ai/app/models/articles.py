from pydantic import BaseModel


class Article(BaseModel):
    """
    Represents a news article.

    Attributes:
        url: Source URL of the article
        title: Article title
        content: Full text content of the article
    """

    url: str
    title: str
    content: str
