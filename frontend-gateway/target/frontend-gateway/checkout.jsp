<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Checkout Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f7fa;
            padding: 30px;
        }

        .container {
            max-width: 500px;
            background: #ffffff;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        h2 {
            text-align: center;
            margin-bottom: 20px;
        }

        label {
            font-weight: bold;
        }

        input[type="number"] {
            width: 100%;
            padding: 8px;
            margin: 5px 0 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        .product-row {
            border-top: 1px solid #ddd;
            padding-top: 15px;
            margin-top: 15px;
        }

        button {
            background-color: #3498db;
            color: white;
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        button:hover {
            background-color: #2980b9;
        }

        input[type="submit"] {
            width: 100%;
            background-color: #2ecc71;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 4px;
            margin-top: 15px;
            cursor: pointer;
            font-size: 16px;
        }

        input[type="submit"]:hover {
            background-color: #27ae60;
        }
    </style>
</head>

<body>
<div class="container">
    <h2>Checkout</h2>

    <form action="submitOrder" method="post">
        <label for="customerID">Customer ID</label>
        <input type="number" id="customerID" name="customerID" required>

        <div id="productRows">
            <div class="product-row">
                <label>Product ID</label>
                <input type="number" name="productID[]" required>

                <label>Quantity</label>
                <input type="number" name="quantity[]" required>
            </div>
        </div>

        <button type="button" onclick="addRow()">➕ Add another product</button>

        <input type="submit" value="Submit Order">
    </form>
</div>

<script>
    const newRowHTML = `
        <div class="product-row">
            <label>Product ID</label>
            <input type="number" name="productID[]" required>

            <label>Quantity</label>
            <input type="number" name="quantity[]" required>
        </div>
    `;

    function addRow(){
        document.getElementById("productRows")
            .insertAdjacentHTML("beforeend", newRowHTML);
    }
</script>

</body>
</html>
