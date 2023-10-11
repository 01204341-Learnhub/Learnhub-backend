from pydantic import BaseModel, HttpUrl


# WISSLIST


class WishListItemModelBody(BaseModel):
    wishlist_item_id: str
    name: str
    type: str
    program_id: str
    price: float


class GetWishListResponseModel(BaseModel):
    wishlist: list[WishListItemModelBody]


class PostWishListItemRequestModel(BaseModel):
    type: str
    program_id: str
