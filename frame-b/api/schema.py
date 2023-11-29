import strawberry


@strawberry.federation.type(keys=["id"])
class Frame:
    id: strawberry.ID

    @strawberry.field
    def frame_ford(self) -> "FrameB":
        return FrameB(
            id=self.id, name="B", data_only_in_frame_b="some data from frame b"
        )


@strawberry.federation.type(keys=["id"])
class FrameWithExtensions:
    id: strawberry.ID
    common_field: str = strawberry.federation.field(shareable=True)

    data_only_in_frame_b: str


@strawberry.federation.type(keys=["id"])
class FrameB:
    id: strawberry.ID
    name: str

    data_only_in_frame_b: str

    @staticmethod
    def resolve_reference(id: strawberry.ID) -> "FrameB":
        return FrameB(id=id, name="B", data_only_in_frame_b="some data from frame b")


@strawberry.federation.type(keys=["id"])
class FrameWithRequires:
    id: strawberry.ID
    available_b: bool = strawberry.federation.field(inaccessible=True)

    @staticmethod
    def resolve_reference(id: strawberry.ID) -> "FrameWithRequires":
        return FrameWithRequires(id=id, available_b=True)


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
            id=id, common_field="Frame B", data_only_in_frame_b="some data from frame b"
        )


schema = strawberry.federation.Schema(
    Query,
    enable_federation_2=True,
    types=[FrameB, FrameWithRequires, Frame],
)
