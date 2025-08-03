import pandas as pd


def load_and_clean_data():
    """
    Imports the csv files, cleans the data,
    and formats the datatypes

    :returns: all the cleaned tables
    """

    # loading data

    categories = pd.read_csv('tables/categories.csv', index_col='category_id')
    customers = pd.read_csv('tables/customers.csv', index_col='customer_id')
    employees = pd.read_csv('tables/employees.csv', index_col='employee_id')
    inventory_movements = pd.read_csv('tables/inventory_movements.csv', index_col='movement_id')
    order_items = pd.read_csv('tables/order_items.csv', index_col='order_item_id')
    orders = pd.read_csv('tables/orders.csv', index_col='order_id')
    product_suppliers = pd.read_csv('tables/product_suppliers.csv')
    products = pd.read_csv('tables/products.csv', index_col='product_id')
    promotions = pd.read_csv('tables/promotions.csv', index_col='promotion_id')
    reviews = pd.read_csv('tables/reviews.csv', index_col='review_id')
    suppliers = pd.read_csv('tables/suppliers.csv', index_col='supplier_id')

    # cleaning the data before rendering visualizations

    # ---------- capping outliers ----------
    # order_items table
    Q01 = order_items['unit_price'].quantile(0.25)
    Q03 = order_items['unit_price'].quantile(0.75)
    IQR1 = Q03 - Q01

    lb1 = Q01 - 1.5 * IQR1
    ub1 = Q03 + 1.5 * IQR1

    order_items.loc[order_items['unit_price'] < lb1, 'unit_price'] = lb1
    order_items.loc[order_items['unit_price'] > ub1, 'unit_price'] = ub1

    order_items['total_price'] = order_items['quantity'] * order_items['unit_price']

    # orders table
    Q1 = orders['total_amount'].quantile(0.25)
    Q3 = orders['total_amount'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    orders.loc[orders['total_amount'] < lower_bound, 'total_amount'] = lower_bound
    orders.loc[orders['total_amount'] > upper_bound, 'total_amount'] = upper_bound

    # capping outliers in supply_price in product_suppliers
    q1 = product_suppliers['supply_price'].quantile(0.25)
    q3 = product_suppliers['supply_price'].quantile(0.75)
    iqr = q3 - q1
    _lb = q1 - 1.5 * iqr
    _ub = q3 + 1.5 * iqr

    product_suppliers.loc[product_suppliers['supply_price'] < _lb, 'supply_price'] = _lb
    product_suppliers.loc[product_suppliers['supply_price'] > _ub, 'supply_price'] = _ub

    # ---------- dropping values ----------
    # dropping 'total_amount == 0' in orders
    orders.drop(orders[orders['total_amount'] == 0].index, inplace=True)

    # setting correct data types

    # for orders
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    orders['shipping_date'] = pd.to_datetime(orders['shipping_date'])
    orders['delivery_date'] = pd.to_datetime(orders['delivery_date'])
    orders['customer_id'] = orders['customer_id'].astype('category')
    orders['status'] = orders['status'].astype('category')
    orders['payment_method'] = orders['payment_method'].astype('category')
    orders['shipping_state'] = orders['shipping_state'].astype('category')
    orders['total_amount'] = orders['total_amount'].astype('float32')

    # for order_items
    order_items['product_id'] = order_items['product_id'].astype('category')
    order_items['order_id'] = order_items['order_id'].astype('category')
    order_items['quantity'] = order_items['quantity'].astype('int32')
    order_items['unit_price'] = order_items['unit_price'].astype('float32')
    order_items['total_price'] = order_items['total_price'].astype('float32')

    # for products
    products['category_id'] = products['category_id'].astype('category')
    products['brand'] = products['brand'].astype('category')
    products['created_date'] = pd.to_datetime(products['created_date'])
    products['stock_quantity'] = products['stock_quantity'].astype('int32')
    products['price'] = products['price'].astype('float32')
    products['cost'] = products['cost'].astype('float32')
    products['weight_kg'] = products['weight_kg'].astype('float32')

    # for customers
    customers['registration_date'] = pd.to_datetime(customers['registration_date'])
    customers['birth_date'] = pd.to_datetime(customers['birth_date'])
    customers['state'] = customers['state'].astype('category')

    # for categories
    categories['category_name'] = categories['category_name'].astype('category')

    # for promotions
    promotions['start_date'] = pd.to_datetime(promotions['start_date'])
    promotions['end_date'] = pd.to_datetime(promotions['end_date'])
    promotions['is_active'] = promotions['is_active'].astype('bool')
    promotions['discount_percentage'] = promotions['discount_percentage'].astype('float32')

    # for reviews
    reviews['review_date'] = pd.to_datetime(reviews['review_date'])
    reviews['customer_id'] = reviews['customer_id'].astype('category')
    reviews['product_id'] = reviews['product_id'].astype('category')
    reviews['order_id'] = reviews['order_id'].astype('category')
    reviews['rating'] = reviews['rating'].astype('int32')
    reviews['helpful_votes'] = reviews['helpful_votes'].astype('int32')

    # for inventory_movements
    inventory_movements['movement_date'] = pd.to_datetime(inventory_movements['movement_date'])
    inventory_movements['product_id'] = inventory_movements['product_id'].astype('category')
    inventory_movements['movement_type'] = inventory_movements['movement_type'].astype('category')
    inventory_movements['quantity'] = inventory_movements['quantity'].astype('int32')

    # for suppliers
    suppliers['country'] = suppliers['country'].astype('category')
    suppliers['state'] = suppliers['state'].astype('category')
    suppliers['rating'] = suppliers['rating'].astype('float32')

    # for product_suppliers
    product_suppliers['product_id'] = product_suppliers['product_id'].astype('category')
    product_suppliers['supplier_id'] = product_suppliers['supplier_id'].astype('category')
    product_suppliers['supply_price'] = product_suppliers['supply_price'].astype('float32')
    product_suppliers['lead_time_days'] = product_suppliers['lead_time_days'].astype('int32')
    product_suppliers['min_order_quantity'] = product_suppliers['min_order_quantity'].astype('int32')

    # returning a dict of csv names
    return {
        'categories': categories,
        'customers': customers,
        'employees': employees,
        'inventory_movements': inventory_movements,
        'order_items': order_items,
        'orders': orders,
        'product_suppliers': product_suppliers,
        'products': products,
        'promotions': promotions,
        'reviews': reviews,
        'suppliers': suppliers
    }