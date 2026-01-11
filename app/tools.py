from typing import Dict
from app.retrieval import search_faqs


# ---- Mock Order Database ----
ORDERS_DB: Dict[str, Dict[str, str]] = {
    "ORD-1001": {
        "status": "Shipped",
        "estimated_delivery": "2025-10-01"
    },
    "ORD-1002": {
        "status": "Processing",
        "estimated_delivery": "2025-10-03"
    },
    "ORD-1003": {
        "status": "Delivered",
        "estimated_delivery": "2025-09-28"
    }
}


def get_order_status(order_id: str) -> str:
    """
    Tool: Fetch order status from backend system.
    """

    order = ORDERS_DB.get(order_id)

    if not order:
        return f"No order found with ID {order_id}."

    return (
        f"Order {order_id} is currently {order['status']} "
        f"and is expected by {order['estimated_delivery']}."
    )


# def search_faqs(query: str) -> str:
#     """
#     Tool: Search FAQs (stub).
#     Will be connected to vector retrieval in Phase 3.
#     """

#     return (
#         "This is a placeholder FAQ response. "
#         "FAQ retrieval will be implemented using vector search."
#     )

def search_faqs_tool(query: str) -> str:
    """
    Tool: Retrieve relevant FAQ content using vector search.
    """
    return search_faqs(query)