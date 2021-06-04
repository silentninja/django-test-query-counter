from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.http import HttpResponse, HttpRequest


@dataclass
class IArbitraryData:
    shapeHashV1Base64: str
    asJsonString: str
    asText: str


@dataclass
class IBody:
    contentType: str
    value: IArbitraryData


@dataclass
class IResponse:
    statusCode: int
    headers: IArbitraryData
    body: IBody

    @classmethod
    def convert(cls, response: HttpResponse) -> IResponse:
        pass


@dataclass
class IHttpInteractionTag:
    name: str
    value: str


@dataclass
class IRequest:
    host: str
    method: str
    path: str
    query: IArbitraryData
    headers: IArbitraryData
    body: IBody

    @classmethod
    def convert(cls, request: HttpRequest) -> IRequest:
        pass


@dataclass
class IHttpInteraction:
    uuid: str
    request: Optional[IRequest]
    response: Optional[IResponse]
    tags: Optional[list[IHttpInteractionTag]]

    @classmethod
    def generate_from(cls, request: HttpRequest, response: HttpResponse) -> IHttpInteraction:
        # Todo extract data from request/response
        return IHttpInteraction("", None, None, None)
