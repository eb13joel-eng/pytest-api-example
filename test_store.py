from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, equal_to
import uuid
import json

'''
TODO: Finish this test by...
1) Creating a function to test the PATCH request /store/order/{order_id}
2) *Optional* Consider using @pytest.fixture to create unique test data for each run
2) *Optional* Consider creating an 'Order' model in schemas.py and validating it in the test
3) Validate the response codes and values
4) Validate the response message "Order and pet status updated successfully"
'''

@pytest.fixture
def create_order():
    """Fixture to create a unique order for testing"""
    # First, make sure pet with ID 0 is available
    reset_pet_endpoint = "/pets/"
    reset_data = {
        "id": 0,
        "name": "snowball",
        "type": "cat", 
        "status": "available"
    }
    api_helpers.post_api_data(reset_pet_endpoint, reset_data)
    
    # Create an order
    order_data = {
        "pet_id": 0  # Using pet ID 0 (snowball)
    }
    response = api_helpers.post_api_data("/store/order", order_data)
    
    if response.status_code == 201:
        order = response.json()
        return order['id']
    return None

def test_patch_order_by_id(create_order):
    """Test PATCH /store/order/{order_id} endpoint"""
    
    # Get the order ID from fixture
    order_id = create_order
    
    if order_id is None:
        pytest.skip("Could not create order for testing")
    
    # Test updating order status to 'sold'
    patch_data = {
        "status": "sold"
    }
    
    test_endpoint = f"/store/order/{order_id}"
    response = api_helpers.patch_api_data(test_endpoint, patch_data)
    
    # Validate response code
    assert response.status_code == 200
    
    # Validate response message
    response_json = response.json()
    assert_that(response_json['message'], equal_to("Order and pet status updated successfully"))
    
    # Verify pet status was also updated
    pet_response = api_helpers.get_api_data("/pets/0")
    assert pet_response.status_code == 200
    pet_data = pet_response.json()
    assert_that(pet_data['status'], equal_to("sold"))

def test_patch_order_invalid_status():
    """Test PATCH with invalid status"""
    # Create an order first
    order_data = {
        "pet_id": 1  # Using pet ID 1
    }
    
    # Make pet available first
    reset_data = {
        "id": 1,
        "name": "ranger",
        "type": "dog",
        "status": "available"
    }
    api_helpers.post_api_data("/pets/", reset_data)
    
    response = api_helpers.post_api_data("/store/order", order_data)
    
    if response.status_code == 201:
        order_id = response.json()['id']
        
        # Try invalid status
        patch_data = {
            "status": "invalid_status"
        }
        
        test_endpoint = f"/store/order/{order_id}"
        response = api_helpers.patch_api_data(test_endpoint, patch_data)
        
        # Should return 400 for invalid status
        assert response.status_code == 400

def test_patch_order_not_found():
    """Test PATCH for non-existent order"""
    fake_order_id = "non-existent-order-id"
    patch_data = {
        "status": "sold"
    }
    
    test_endpoint = f"/store/order/{fake_order_id}"
    response = api_helpers.patch_api_data(test_endpoint, patch_data)
    
    # Should return 404
    assert response.status_code == 404