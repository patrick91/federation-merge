# How to run this example

## Install dependencies

in each frame folder run

```bash
pdm install
```

And also run

```bash
curl -sSL https://rover.apollo.dev/nix/latest | sh
```

To install rover

## Run the services

in each frame folder run

```bash
pdm dev
```

## Run Apollo Router in dev mode

in the root folder run

```bash
rover dev --supergraph-config supergraph.yaml
```

Then you should be able to access the Apollo Studio Explorer at
http://localhost:4000

## Queries:

> standard federation query, field with the same name will only be fetched once
> usually from the first service

```graphql
query Basic($id: ID!) {
  frame(id: $id) {
    id

    # unique fields will come from the correct service
    # (because they only live in that specific service)
    # for example:
    frameFord {
      id
      dataOnlyInFrameB
    }

    frameGpl {
      id
      dataOnlyInFrameA
    }
  }
}
```

> similar to the one we had previously, but also with a common field, the common
> field will be resolved by only one subgraph

```graphql
query CommonField($id: ID!) {
  frameWithAdditionalData(id: $id) {
    id
    commonField
    # try commenting one of these two fields
    # and see the value of common field update
    # Apollo Router tries to do the most efficient
    # query plan, in order to reduce the number of
    # data fetches
    dataOnlyInFrameA
    dataOnlyInFrameB
  }
}
```

> in this approach we abuse some feature of federation in order to fetch the
> data from the correct subgraph in the frame field for the `FrameWithRequires`
> type we require the `available_X` field (using the @require directive) for
> every subgraph, so that we have a way of knowing if this frame is available in
> any of the frames subgraphs the annoying part of this is that we need to
> implement this field in all the subgraphs, and we also need some logic in our
> main Frame service to return the right type we also use an interface to make
> common fields easier to fetch

```graphql
query FrameWithRequires($id: ID!) {
  frameWithRequires(id: $id) {
    id
    frame {
      id
      name

      ... on FrameA {
        dataOnlyInFrameA
      }

      ... on FrameB {
        dataOnlyInFrameB
      }
    }
  }
}
```

> similar to the one before, but we assume the main Frame service has a way to
> know where the data comes from, in this case we only do a simple check on the
> id if the id is one then we return data from Frame A otherwise Frame B we can
> also add interfaces like above to make it easier to fetch

```graphql
query FrameWithUnion($id: ID!) {
  frameWithUnion(id: $id) {
    ... on FrameA {
      dataOnlyInFrameA
      id
      name
    }
    ... on FrameB {
      dataOnlyInFrameB
      id
      name
    }
  }
}
```

> this uses service to service communication to fetch the data from other
> subgraphs I've done a JSON field for time sake, but you can return any object
> too

```graphql
query Http($id: ID!) {
  frameViaHttp(id: $id)
}
```
