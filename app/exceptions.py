class ProductNotFoundError(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product {product_id} not found")


class InsufficientStockError(Exception):
    def __init__(self, product_id: int, requested_qty: int):
        self.product_id = product_id
        self.requested_qty = requested_qty
        super().__init__(f"Not enough stock for product {product_id} (requested {requested_qty})")
