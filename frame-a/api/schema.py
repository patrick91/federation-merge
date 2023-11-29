import strawberry


@strawberry.federation.type(keys=["id"])
class FrameWithExtensions:
    id: strawberry.ID = strawberry.federation.field(shareable=True)
    common_field: str = strawberry.federation.field(shareable=True)

    data_only_in_frame_a: str


@strawberry.federation.type(keys=["id"])
class FrameA:
    id: strawberry.ID
    name: str

    data_only_in_frame_a: str

    @staticmethod
    def resolve_reference(id: strawberry.ID) -> "FrameA":
        return FrameA(id=id, name="A", data_only_in_frame_a="some data from frame a")


@strawberry.federation.type(keys=["id"])
class Frame:
    id: strawberry.ID

    @strawberry.field
    def frame_gpl(self) -> FrameA:
        return FrameA(
            id=self.id, name="A", data_only_in_frame_a="some data from frame a"
        )


@strawberry.federation.type(keys=["id"])
class FrameWithRequires:
    id: strawberry.ID
    available_a: bool = strawberry.federation.field(inaccessible=True)

    @staticmethod
    def resolve_reference(id: strawberry.ID) -> "FrameWithRequires":
        return FrameWithRequires(id=id, available_a=False)


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
            id=id, common_field="Frame A", data_only_in_frame_a="some data from frame a"
        )


schema = strawberry.federation.Schema(
    Query,
    enable_federation_2=True,
    types=[FrameA, FrameWithRequires, Frame],
)
