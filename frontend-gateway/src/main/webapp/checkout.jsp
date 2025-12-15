<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
    <head>
        <title>Checkout Page</title>
    </head>
    <body>
        <h2>Checkout</h2>
        <form action="submitOrder" method="post">
            <label for="customerID">Customer ID:</label><br>
            <input type="number" id="customerID" name="customerID" required><br><br>
            <div id = "productRows">
                <label for="productID">Product ID:</label><br>
                <input type ="number"  name="productID[]" required><br>
                <label for="quantity">Quantity:</label><br>
                <input type ="number"  name="quantity[]" required><br>
            </div>
            <button type = "button" onclick="addRow()">Add another product?</button>
            <input type="submit" value="Submit">
            <script>
                const newRowHTML = `<label for="productID">Product ID:</label><br>
                                    <input type ="number"  name="productID[]" required><br>
                                    <label for="quantity">Quantity:</label><br>
                                    <input type ="number"  name="quantity[]" required><br>`;
                function addRow(){
                    const container = document.getElementById("productRows");
                    const newRow = document.createElement('div');
                    newRow.innerHTML = newRowHTML;
                    container.appendChild(newRow)
                }
            </script>
        </form>
    </body>
</html>