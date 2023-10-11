from pydantic import BaseModel, HttpUrl


class place_holder_model(BaseModel):
    pass

#WISSLIST

class WishListItemModelBody(BaseModel):
    wishlist_item_id: str
    name: str
    type: str
    program_id: str
    price: float


class GetWishListResponseModel(BaseModel):
    wishlist: list[WishListItemModelBody]