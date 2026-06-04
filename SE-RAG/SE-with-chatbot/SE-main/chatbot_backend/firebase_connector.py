import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Flag to use mock data if serviceAccountKey.json is not found
USE_MOCK = True

# Try to initialize Firebase if the key exists
key_path = os.path.join(os.path.dirname(__file__), "SE-RAG", "SE-with-chatbot", "SE-main", "tech-hub-master-firebase-adminsdk-fbsvc-0ac3399f9e.json")
if os.path.exists(key_path):
    try:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        USE_MOCK = False
        print("Firebase initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}. Falling back to mock data.")

def get_iphone_inventory():
    """
    Fetches iPhone inventory from Firestore and returns it as a structured JSON string.
    """
    if USE_MOCK:
        # Return mock data for testing
        mock_data = [
            {"model": "iPhone 15 Pro", "color": "Titanium", "storage": "256GB", "price": 65000, "stock": 5},
            {"model": "iPhone 15", "color": "Black", "storage": "128GB", "price": 50000, "stock": 12},
            {"model": "iPhone 14 Pro", "color": "Deep Purple", "storage": "256GB", "price": 55000, "stock": 2},
            {"model": "iPhone 13", "color": "Blue", "storage": "128GB", "price": 40000, "stock": 0}
        ]
        return json.dumps(mock_data)
    else:
        # Active service layer
        try:
            iphones_ref = db.collection('inventory').where(filter=FieldFilter('category', '==', 'iphone')).stream()
            inventory_list = []
            for doc in iphones_ref:
                item = doc.to_dict()
                inventory_list.append(item)
            return json.dumps(inventory_list)
        except Exception as e:
            return json.dumps({"error": f"Failed to fetch from Firebase: {e}"})

def get_order_status(order_id):
    """
    Fetches order status from Firestore.
    """
    if USE_MOCK:
        if order_id == "12345":
            return json.dumps({"order_id": "12345", "status": "Shipped", "eta": "2 days"})
        return json.dumps({"error": "Order not found."})
    else:
        try:
            order_ref = db.collection('orders').document(order_id).get()
            if order_ref.exists:
                return json.dumps(order_ref.to_dict())
            else:
                return json.dumps({"error": "Order not found."})
        except Exception as e:
            return json.dumps({"error": f"Failed to fetch order: {e}"})
