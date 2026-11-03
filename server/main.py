from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from mock_data import inventory_items, orders, demand_forecasts, backlog_items, spending_summary, monthly_spending, category_spending, recent_transactions, purchase_orders

app = FastAPI(title="Factory Inventory Management System")

# Quarter mapping for date filtering
QUARTER_MAP = {
    'Q1-2025': ['2025-01', '2025-02', '2025-03'],
    'Q2-2025': ['2025-04', '2025-05', '2025-06'],
    'Q3-2025': ['2025-07', '2025-08', '2025-09'],
    'Q4-2025': ['2025-10', '2025-11', '2025-12']
}

def filter_by_month(items: list, month: Optional[str]) -> list:
    """Filter items by month/quarter based on order_date field"""
    if not month or month == 'all':
        return items

    if month.startswith('Q'):
        # Handle quarters
        if month in QUARTER_MAP:
            months = QUARTER_MAP[month]
            return [item for item in items if any(m in item.get('order_date', '') for m in months)]
    else:
        # Direct month match
        return [item for item in items if month in item.get('order_date', '')]

    return items

def apply_filters(items: list, warehouse: Optional[str] = None, category: Optional[str] = None,
                 status: Optional[str] = None) -> list:
    """Apply common filters to a list of items"""
    filtered = items

    if warehouse and warehouse != 'all':
        filtered = [item for item in filtered if item.get('warehouse') == warehouse]

    if category and category != 'all':
        filtered = [item for item in filtered if item.get('category', '').lower() == category.lower()]

    if status and status != 'all':
        filtered = [item for item in filtered if item.get('status', '').lower() == status.lower()]

    return filtered

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class InventoryItem(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_point: int
    unit_cost: float
    location: str
    last_updated: str

class Order(BaseModel):
    id: str
    order_number: str
    customer: str
    items: List[dict]
    status: str
    order_date: str
    expected_delivery: str
    total_value: float
    actual_delivery: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None

class DemandForecast(BaseModel):
    id: str
    item_sku: str
    item_name: str
    current_demand: int
    forecasted_demand: int
    trend: str
    period: str

class BacklogItem(BaseModel):
    id: str
    order_id: str
    item_sku: str
    item_name: str
    quantity_needed: int
    quantity_available: int
    days_delayed: int
    priority: str
    has_purchase_order: Optional[bool] = False

class PurchaseOrder(BaseModel):
    id: str
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: str
    created_date: str
    notes: Optional[str] = None

class CreatePurchaseOrderRequest(BaseModel):
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    notes: Optional[str] = None

class RestockRecommendation(BaseModel):
    item_sku: str
    item_name: str
    category: str
    current_stock: int
    forecasted_demand: int
    recommended_quantity: int
    unit_cost: float
    total_cost: float
    priority: str
    trend: str

class RestockOrderRequest(BaseModel):
    items: List[dict]  # List of items with sku and quantity
    total_budget: float
    notes: Optional[str] = None

class RestockOrderResponse(BaseModel):
    order_id: str
    order_number: str
    status: str
    total_value: float
    items: List[dict]
    expected_delivery: str
    delivery_lead_time_days: int
    order_date: str

# API endpoints
@app.get("/")
def root():
    return {"message": "Factory Inventory Management System API", "version": "1.0.0"}

@app.get("/api/inventory", response_model=List[InventoryItem])
def get_inventory(
    warehouse: Optional[str] = None,
    category: Optional[str] = None
):
    """Get all inventory items with optional filtering"""
    return apply_filters(inventory_items, warehouse, category)

@app.get("/api/inventory/{item_id}", response_model=InventoryItem)
def get_inventory_item(item_id: str):
    """Get a specific inventory item"""
    item = next((item for item in inventory_items if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/api/orders", response_model=List[Order])
def get_orders(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get all orders with optional filtering"""
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)
    return filtered_orders

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    """Get a specific order"""
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/demand", response_model=List[DemandForecast])
def get_demand_forecasts():
    """Get demand forecasts"""
    return demand_forecasts

@app.get("/api/backlog", response_model=List[BacklogItem])
def get_backlog():
    """Get backlog items with purchase order status"""
    # Add has_purchase_order flag to each backlog item
    result = []
    for item in backlog_items:
        item_dict = dict(item)
        # Check if this backlog item has a purchase order
        has_po = any(po["backlog_item_id"] == item["id"] for po in purchase_orders)
        item_dict["has_purchase_order"] = has_po
        result.append(item_dict)
    return result

@app.get("/api/dashboard/summary")
def get_dashboard_summary(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get summary statistics for dashboard with optional filtering"""
    # Filter inventory
    filtered_inventory = apply_filters(inventory_items, warehouse, category)

    # Filter orders
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    total_inventory_value = sum(item["quantity_on_hand"] * item["unit_cost"] for item in filtered_inventory)
    low_stock_items = len([item for item in filtered_inventory if item["quantity_on_hand"] <= item["reorder_point"]])
    pending_orders = len([order for order in filtered_orders if order["status"] in ["Processing", "Backordered"]])
    total_backlog_items = len(backlog_items)

    return {
        "total_inventory_value": round(total_inventory_value, 2),
        "low_stock_items": low_stock_items,
        "pending_orders": pending_orders,
        "total_backlog_items": total_backlog_items,
        "total_orders_value": sum(order["total_value"] for order in filtered_orders)
    }

@app.get("/api/spending/summary")
def get_spending_summary():
    """Get spending summary statistics"""
    return spending_summary

@app.get("/api/spending/monthly")
def get_monthly_spending():
    """Get monthly spending breakdown"""
    return monthly_spending

@app.get("/api/spending/categories")
def get_category_spending():
    """Get spending by category"""
    return category_spending

@app.get("/api/spending/transactions")
def get_recent_transactions():
    """Get recent transactions"""
    return recent_transactions

@app.get("/api/reports/quarterly")
def get_quarterly_reports():
    """Get quarterly performance reports"""
    # Calculate quarterly statistics from orders
    quarters = {}

    for order in orders:
        order_date = order.get('order_date', '')
        # Determine quarter
        if '2025-01' in order_date or '2025-02' in order_date or '2025-03' in order_date:
            quarter = 'Q1-2025'
        elif '2025-04' in order_date or '2025-05' in order_date or '2025-06' in order_date:
            quarter = 'Q2-2025'
        elif '2025-07' in order_date or '2025-08' in order_date or '2025-09' in order_date:
            quarter = 'Q3-2025'
        elif '2025-10' in order_date or '2025-11' in order_date or '2025-12' in order_date:
            quarter = 'Q4-2025'
        else:
            continue

        if quarter not in quarters:
            quarters[quarter] = {
                'quarter': quarter,
                'total_orders': 0,
                'total_revenue': 0,
                'delivered_orders': 0,
                'avg_order_value': 0
            }

        quarters[quarter]['total_orders'] += 1
        quarters[quarter]['total_revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            quarters[quarter]['delivered_orders'] += 1

    # Calculate averages and fulfillment rate
    result = []
    for q, data in quarters.items():
        if data['total_orders'] > 0:
            data['avg_order_value'] = round(data['total_revenue'] / data['total_orders'], 2)
            data['fulfillment_rate'] = round((data['delivered_orders'] / data['total_orders']) * 100, 1)
        result.append(data)

    # Sort by quarter
    result.sort(key=lambda x: x['quarter'])
    return result

@app.get("/api/reports/monthly-trends")
def get_monthly_trends():
    """Get month-over-month trends"""
    months = {}

    for order in orders:
        order_date = order.get('order_date', '')
        if not order_date:
            continue

        # Extract month (format: YYYY-MM-DD)
        month = order_date[:7]  # Gets YYYY-MM

        if month not in months:
            months[month] = {
                'month': month,
                'order_count': 0,
                'revenue': 0,
                'delivered_count': 0
            }

        months[month]['order_count'] += 1
        months[month]['revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            months[month]['delivered_count'] += 1

    # Convert to list and sort
    result = list(months.values())
    result.sort(key=lambda x: x['month'])
    return result

@app.post("/api/restock/recommendations", response_model=List[RestockRecommendation])
def get_restock_recommendations(budget: float):
    """
    Generate restocking recommendations based on available budget.

    Algorithm:
    1. Combine inventory data with demand forecasts
    2. Prioritize items with:
       - Increasing demand trend
       - Low stock relative to reorder point
       - High forecasted demand
    3. Calculate recommended quantity within budget constraints
    4. Return sorted list by priority (High > Medium > Low)
    """
    if budget <= 0:
        raise HTTPException(status_code=400, detail="Budget must be greater than 0")

    recommendations = []
    remaining_budget = budget

    # Create a map of demand forecasts by SKU for quick lookup
    demand_map = {forecast['item_sku']: forecast for forecast in demand_forecasts}

    # Analyze each inventory item
    for item in inventory_items:
        sku = item['sku']

        # Check if we have demand forecast for this item
        if sku not in demand_map:
            continue

        forecast = demand_map[sku]
        current_stock = item['quantity_on_hand']
        reorder_point = item['reorder_point']
        forecasted_demand = forecast['forecasted_demand']
        trend = forecast['trend']
        unit_cost = item['unit_cost']

        # Calculate priority based on stock level and trend
        # High priority: Low stock + Increasing trend
        # Medium priority: Low stock OR Increasing trend
        # Low priority: Adequate stock + Stable/Decreasing trend
        is_low_stock = current_stock <= reorder_point
        is_increasing = trend.lower() == 'increasing'

        if is_low_stock and is_increasing:
            priority = 'High'
            priority_score = 3
        elif is_low_stock or is_increasing:
            priority = 'Medium'
            priority_score = 2
        else:
            priority = 'Low'
            priority_score = 1

        # Calculate recommended quantity
        # Order enough to meet forecasted demand minus current stock
        # But ensure we don't go below reorder point buffer
        recommended_qty = max(forecasted_demand - current_stock, reorder_point)

        # Ensure minimum order of 10 units if we're ordering at all
        if recommended_qty > 0:
            recommended_qty = max(recommended_qty, 10)

        total_cost = recommended_qty * unit_cost

        # Only recommend if it fits in remaining budget
        if total_cost <= remaining_budget:
            recommendations.append({
                'item_sku': sku,
                'item_name': item['name'],
                'category': item['category'],
                'current_stock': current_stock,
                'forecasted_demand': forecasted_demand,
                'recommended_quantity': recommended_qty,
                'unit_cost': unit_cost,
                'total_cost': round(total_cost, 2),
                'priority': priority,
                'trend': trend,
                '_priority_score': priority_score  # For sorting
            })
            remaining_budget -= total_cost

    # Sort by priority (High > Medium > Low), then by total cost descending
    recommendations.sort(key=lambda x: (x['_priority_score'], x['total_cost']), reverse=True)

    # Remove internal sorting field before returning
    for rec in recommendations:
        del rec['_priority_score']

    return recommendations

@app.post("/api/orders/restock", response_model=RestockOrderResponse)
def create_restock_order(request: RestockOrderRequest):
    """
    Create a new restocking order and add it to the orders list.

    Calculates delivery lead time based on item categories:
    - Circuit Boards: 14 days
    - Sensors: 10 days
    - Actuators: 12 days
    - Controllers: 10 days
    - Default: 10 days
    """
    # Generate unique order ID and number
    order_id = f"order_{len(orders) + 1000}"
    order_number = f"ORD-REST-{len(orders) + 1:05d}"

    # Calculate total value from items
    total_value = 0
    order_items = []
    max_lead_time = 10  # Default lead time

    # Category-based lead times (in days)
    lead_time_map = {
        'circuit boards': 14,
        'sensors': 10,
        'actuators': 12,
        'controllers': 10
    }

    for item_data in request.items:
        sku = item_data['sku']
        quantity = item_data['quantity']

        # Find inventory item to get details
        inventory_item = next((inv for inv in inventory_items if inv['sku'] == sku), None)
        if not inventory_item:
            continue

        item_cost = inventory_item['unit_cost'] * quantity
        total_value += item_cost

        # Determine lead time based on category
        category = inventory_item['category'].lower()
        item_lead_time = lead_time_map.get(category, 10)
        max_lead_time = max(max_lead_time, item_lead_time)

        order_items.append({
            'sku': sku,
            'name': inventory_item['name'],
            'quantity': quantity,
            'unit_price': inventory_item['unit_cost'],
            'total': round(item_cost, 2)
        })

    # Calculate dates
    order_date = datetime.now().strftime('%Y-%m-%d')
    expected_delivery = (datetime.now() + timedelta(days=max_lead_time)).strftime('%Y-%m-%d')

    # Create new order object
    new_order = {
        'id': order_id,
        'order_number': order_number,
        'customer': 'Internal Restocking',
        'items': order_items,
        'status': 'Processing',
        'order_date': order_date,
        'expected_delivery': expected_delivery,
        'total_value': round(total_value, 2),
        'actual_delivery': None,
        'warehouse': 'Multiple',  # Restocking orders can affect multiple warehouses
        'category': 'Restocking',
        'notes': request.notes or 'Automated restocking order',
        'is_restock_order': True,  # Flag to identify restock orders
        'delivery_lead_time_days': max_lead_time
    }

    # Add to orders list (in-memory)
    orders.append(new_order)

    return {
        'order_id': order_id,
        'order_number': order_number,
        'status': 'Processing',
        'total_value': round(total_value, 2),
        'items': order_items,
        'expected_delivery': expected_delivery,
        'delivery_lead_time_days': max_lead_time,
        'order_date': order_date
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
