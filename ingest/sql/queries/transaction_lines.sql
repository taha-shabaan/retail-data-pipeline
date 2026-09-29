SELECT
    line_id,
    transaction_id,
    store_id,
    product_id,
    sale_date,
    quantity,
    unit_price
FROM operational.transaction_lines
ORDER BY sale_date, line_id;
