# Shop architecture

`shop.api` is the public command adapter. It creates the repository and
`PageTokenCodec`, then calls the application function `shop.orders.list_orders`.
`PageTokenCodec` is the sole owner of opaque continuation-token encoding and decoding.
Application functions may call that owner but must not implement token serialization
themselves.
