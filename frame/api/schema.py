from typing import Optional

import strawberry
import httpx
import asyncio


@strawberry.federation.type(keys=["id"], shareable=True)
class Frame:
    id: strawberry.ID


@strawberry.federation.type(keys=["id"])
class FrameWithExtensions:
    id: strawberry.ID
    name: str


@strawberry.interface
class FrameInterface:
    id: strawberry.ID
    name: str


@strawberry.federation.type(keys=["id"])
class FrameA(FrameInterface):
    id: strawberry.ID
    name: str = strawberry.federation.field(external=True)


@strawberry.federation.type(keys=["id"])
class FrameB(FrameInterface):
    id: strawberry.ID
    name: str = strawberry.federation.field(external=True)


@strawberry.federation.type(keys=["id"])
class FrameWithRequires:
    id: strawberry.ID
    available_a: bool = strawberry.federation.field(external=True, default=False)
    available_b: bool = strawberry.federation.field(external=True, default=False)

    @strawberry.federation.field(requires=["availableA", "availableB"])
    def frame(self) -> FrameInterface | None:
        if self.available_a:
            return FrameA(id=self.id, name=None)  # type: ignore

        if self.available_b:
            return FrameB(id=self.id, name=None)  # type: ignore

        return None


@strawberry.type
class Query:
    @strawberry.federation.field(shareable=True)
    def frame(self, id: strawberry.ID) -> Frame | None:
        return Frame(id=id)

    @strawberry.federation.field(shareable=True)
    def frame_with_additional_data(
        self, id: strawberry.ID
    ) -> FrameWithExtensions | None:
        return FrameWithExtensions(
            id=id,
            name="Frame",
        )

    @strawberry.field
    def frame_with_union(self, id: strawberry.ID) -> FrameA | FrameB:
        if id == "1":
            return FrameA(id=id, name=None)  # type: ignore

        return FrameB(id=id, name=None)  # type: ignore

    @strawberry.field
    def frame_with_requires(self, id: strawberry.ID) -> Optional[FrameWithRequires]:
        return FrameWithRequires(id=id)

    @strawberry.field
    async def frame_via_http(
        self, id: strawberry.ID
    ) -> Optional[strawberry.scalars.JSON]:
        services = ["http://localhost:4001", "http://localhost:4002"]

        query = """
        query ($id: ID!) {
            frame(id: $id) {
                id
            }
        }
        """

        async with httpx.AsyncClient() as client:
            async with asyncio.taskgroups.TaskGroup() as g:
                tasks = [
                    g.create_task(
                        client.post(
                            service, json={"query": query, "variables": {"id": id}}
                        )
                    )
                    for service in services
                ]

        responses = [task.result() for task in tasks]

        for service, response in zip(services, responses):
            data = response.json()["data"]["frame"]

            if data:
                return {"from": service, "data": data}  # type: ignore

        return None


schema = strawberry.federation.Schema(
    Query,
    enable_federation_2=True,
)
