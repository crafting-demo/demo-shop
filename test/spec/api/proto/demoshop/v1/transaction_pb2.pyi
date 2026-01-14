import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Product(_message.Message):
    __slots__ = ("id", "name", "description", "image_data", "price_per_unit", "count_in_stock", "state", "created_at", "updated_at")
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[Product.State]
        AVAILABLE: _ClassVar[Product.State]
        OFF_SHELF: _ClassVar[Product.State]
    UNSPECIFIED: Product.State
    AVAILABLE: Product.State
    OFF_SHELF: Product.State
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
    COUNT_IN_STOCK_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    image_data: bytes
    price_per_unit: int
    count_in_stock: int
    state: Product.State
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., image_data: _Optional[bytes] = ..., price_per_unit: _Optional[int] = ..., count_in_stock: _Optional[int] = ..., state: _Optional[_Union[Product.State, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CartItem(_message.Message):
    __slots__ = ("product", "quantity")
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    product: Product
    quantity: int
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ..., quantity: _Optional[int] = ...) -> None: ...

class Cart(_message.Message):
    __slots__ = ("id", "items", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    items: _containers.RepeatedCompositeFieldContainer[CartItem]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., items: _Optional[_Iterable[_Union[CartItem, _Mapping]]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OrderItem(_message.Message):
    __slots__ = ("product", "quantity", "price_at_purchase")
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_AT_PURCHASE_FIELD_NUMBER: _ClassVar[int]
    product: Product
    quantity: int
    price_at_purchase: int
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ..., quantity: _Optional[int] = ..., price_at_purchase: _Optional[int] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("id", "items", "total_amount", "state", "created_at", "updated_at")
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[Order.State]
        PROCESSING: _ClassVar[Order.State]
        SHIPPED: _ClassVar[Order.State]
        COMPLETED: _ClassVar[Order.State]
        CANCELED: _ClassVar[Order.State]
    UNSPECIFIED: Order.State
    PROCESSING: Order.State
    SHIPPED: Order.State
    COMPLETED: Order.State
    CANCELED: Order.State
    ID_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    items: _containers.RepeatedCompositeFieldContainer[OrderItem]
    total_amount: int
    state: Order.State
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., items: _Optional[_Iterable[_Union[OrderItem, _Mapping]]] = ..., total_amount: _Optional[int] = ..., state: _Optional[_Union[Order.State, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PageInfo(_message.Message):
    __slots__ = ("has_next_page", "has_previous_page", "start_cursor", "end_cursor")
    HAS_NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    HAS_PREVIOUS_PAGE_FIELD_NUMBER: _ClassVar[int]
    START_CURSOR_FIELD_NUMBER: _ClassVar[int]
    END_CURSOR_FIELD_NUMBER: _ClassVar[int]
    has_next_page: bool
    has_previous_page: bool
    start_cursor: str
    end_cursor: str
    def __init__(self, has_next_page: bool = ..., has_previous_page: bool = ..., start_cursor: _Optional[str] = ..., end_cursor: _Optional[str] = ...) -> None: ...

class PaginationRequest(_message.Message):
    __slots__ = ("first", "after")
    FIRST_FIELD_NUMBER: _ClassVar[int]
    AFTER_FIELD_NUMBER: _ClassVar[int]
    first: int
    after: str
    def __init__(self, first: _Optional[int] = ..., after: _Optional[str] = ...) -> None: ...

class QueryProductsRequest(_message.Message):
    __slots__ = ("pagination", "state_filter")
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    STATE_FILTER_FIELD_NUMBER: _ClassVar[int]
    pagination: PaginationRequest
    state_filter: Product.State
    def __init__(self, pagination: _Optional[_Union[PaginationRequest, _Mapping]] = ..., state_filter: _Optional[_Union[Product.State, str]] = ...) -> None: ...

class QueryProductsResponse(_message.Message):
    __slots__ = ("products", "page_info", "total_count")
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[Product]
    page_info: PageInfo
    total_count: int
    def __init__(self, products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ..., page_info: _Optional[_Union[PageInfo, _Mapping]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetProductRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetProductResponse(_message.Message):
    __slots__ = ("product",)
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: Product
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class CreateProductRequest(_message.Message):
    __slots__ = ("name", "description", "image_data", "price_per_unit", "count_in_stock", "state")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
    COUNT_IN_STOCK_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    image_data: bytes
    price_per_unit: int
    count_in_stock: int
    state: Product.State
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., image_data: _Optional[bytes] = ..., price_per_unit: _Optional[int] = ..., count_in_stock: _Optional[int] = ..., state: _Optional[_Union[Product.State, str]] = ...) -> None: ...

class CreateProductResponse(_message.Message):
    __slots__ = ("product",)
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: Product
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class UpdateProductRequest(_message.Message):
    __slots__ = ("id", "name", "description", "image_data", "price_per_unit", "count_in_stock", "state")
    class NameUpdate(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: str
        def __init__(self, value: _Optional[str] = ...) -> None: ...
    class DescriptionUpdate(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: str
        def __init__(self, value: _Optional[str] = ...) -> None: ...
    class ImageDataUpdate(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: bytes
        def __init__(self, value: _Optional[bytes] = ...) -> None: ...
    class PricePerUnitUpdate(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: int
        def __init__(self, value: _Optional[int] = ...) -> None: ...
    class CountInStockUpdate(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: int
        def __init__(self, value: _Optional[int] = ...) -> None: ...
    class StateUpdate(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: Product.State
        def __init__(self, value: _Optional[_Union[Product.State, str]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
    COUNT_IN_STOCK_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: UpdateProductRequest.NameUpdate
    description: UpdateProductRequest.DescriptionUpdate
    image_data: UpdateProductRequest.ImageDataUpdate
    price_per_unit: UpdateProductRequest.PricePerUnitUpdate
    count_in_stock: UpdateProductRequest.CountInStockUpdate
    state: UpdateProductRequest.StateUpdate
    def __init__(self, id: _Optional[str] = ..., name: _Optional[_Union[UpdateProductRequest.NameUpdate, _Mapping]] = ..., description: _Optional[_Union[UpdateProductRequest.DescriptionUpdate, _Mapping]] = ..., image_data: _Optional[_Union[UpdateProductRequest.ImageDataUpdate, _Mapping]] = ..., price_per_unit: _Optional[_Union[UpdateProductRequest.PricePerUnitUpdate, _Mapping]] = ..., count_in_stock: _Optional[_Union[UpdateProductRequest.CountInStockUpdate, _Mapping]] = ..., state: _Optional[_Union[UpdateProductRequest.StateUpdate, _Mapping]] = ...) -> None: ...

class UpdateProductResponse(_message.Message):
    __slots__ = ("product",)
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: Product
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class DeleteProductRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteProductResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCartRequest(_message.Message):
    __slots__ = ("cart_id",)
    CART_ID_FIELD_NUMBER: _ClassVar[int]
    cart_id: str
    def __init__(self, cart_id: _Optional[str] = ...) -> None: ...

class GetCartResponse(_message.Message):
    __slots__ = ("cart",)
    CART_FIELD_NUMBER: _ClassVar[int]
    cart: Cart
    def __init__(self, cart: _Optional[_Union[Cart, _Mapping]] = ...) -> None: ...

class AddProductToCartRequest(_message.Message):
    __slots__ = ("cart_id", "product_id", "quantity")
    CART_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    cart_id: str
    product_id: str
    quantity: int
    def __init__(self, cart_id: _Optional[str] = ..., product_id: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...

class AddProductToCartResponse(_message.Message):
    __slots__ = ("cart",)
    CART_FIELD_NUMBER: _ClassVar[int]
    cart: Cart
    def __init__(self, cart: _Optional[_Union[Cart, _Mapping]] = ...) -> None: ...

class UpdateProductInCartRequest(_message.Message):
    __slots__ = ("cart_id", "product_id", "quantity")
    CART_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    cart_id: str
    product_id: str
    quantity: int
    def __init__(self, cart_id: _Optional[str] = ..., product_id: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...

class UpdateProductInCartResponse(_message.Message):
    __slots__ = ("cart",)
    CART_FIELD_NUMBER: _ClassVar[int]
    cart: Cart
    def __init__(self, cart: _Optional[_Union[Cart, _Mapping]] = ...) -> None: ...

class ClearCartRequest(_message.Message):
    __slots__ = ("cart_id",)
    CART_ID_FIELD_NUMBER: _ClassVar[int]
    cart_id: str
    def __init__(self, cart_id: _Optional[str] = ...) -> None: ...

class ClearCartResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateOrderRequest(_message.Message):
    __slots__ = ("cart_id",)
    CART_ID_FIELD_NUMBER: _ClassVar[int]
    cart_id: str
    def __init__(self, cart_id: _Optional[str] = ...) -> None: ...

class CreateOrderResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: Order
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class QueryOrdersRequest(_message.Message):
    __slots__ = ("pagination", "state_filter")
    class StateFilter(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: Order.State
        def __init__(self, value: _Optional[_Union[Order.State, str]] = ...) -> None: ...
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    STATE_FILTER_FIELD_NUMBER: _ClassVar[int]
    pagination: PaginationRequest
    state_filter: QueryOrdersRequest.StateFilter
    def __init__(self, pagination: _Optional[_Union[PaginationRequest, _Mapping]] = ..., state_filter: _Optional[_Union[QueryOrdersRequest.StateFilter, _Mapping]] = ...) -> None: ...

class QueryOrdersResponse(_message.Message):
    __slots__ = ("orders", "page_info", "total_count")
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[Order]
    page_info: PageInfo
    total_count: int
    def __init__(self, orders: _Optional[_Iterable[_Union[Order, _Mapping]]] = ..., page_info: _Optional[_Union[PageInfo, _Mapping]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetOrderRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetOrderResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: Order
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class UpdateOrderRequest(_message.Message):
    __slots__ = ("id", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: Order.State
    def __init__(self, id: _Optional[str] = ..., state: _Optional[_Union[Order.State, str]] = ...) -> None: ...

class UpdateOrderResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: Order
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...
