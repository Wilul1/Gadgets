import re

def route_intent(user_input):
    """
    Evaluates user input and routes to the appropriate data source.
    Returns a tuple (intent, extracted_data).
    Intents: 'inventory', 'order_tracking', 'faq'
    """
    user_input_lower = user_input.lower()
    
    # Check for order tracking
    order_match = re.search(r'(?:order\s*#?|#)\s*([a-z0-9]+)', user_input_lower)
    if order_match and ("track" in user_input_lower or "status" in user_input_lower or "where" in user_input_lower):
        # We store the extracted order number in a global or pass it via context if needed,
        # but for now, chatbot_engine just passes user_input directly to get_order_status.
        return 'order_status'
        
    # Check for inventory
    inventory_keywords = ["iphone", "stock", "available", "do you have", "price", "how much", "sell", "bestsellers", "products", "bestseller", "ano tinda", "ano benta"]
    
    # If the user asks about iphones, bestsellers, products, or what we sell, route to inventory
    if any(keyword in user_input_lower for keyword in inventory_keywords):
        return 'inventory'
        
    # Default to FAQ
    return 'faq'
