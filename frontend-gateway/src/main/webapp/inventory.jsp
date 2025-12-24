<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ page import="java.util.List, java.util.Map" %>
<html>
<head>
    <title>Inventory</title>
    <style>
        table { border-collapse: collapse; width: 70%; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .nav { margin-bottom: 15px; }
    </style>
</head>
<body>

<h2 style="color: blue;">Inventory List</h2>


<form method="get" action="customerProfile">
    <label>Customer ID:</label>
    <input type="number" name="customerId" required>
    <button type="submit">View Profile</button>
</form>

<br>

<form method="get" action="ordersHistory">
    <label>Customer ID:</label>
    <input type="number" name="customerId" required>
    <button type="submit">Orders History</button>
</form>

<br>

<%
    List<Map<String,Object>> inventoryList =
        (List<Map<String,Object>>) request.getAttribute("inventoryList");

    if (inventoryList != null && !inventoryList.isEmpty()) {
%>

<table>
<tr>
    <th>ID</th>
    <th>Name</th>
    <th>Quantity</th>
    <th>Price</th>
</tr>

<%
    for (Map<String,Object> item : inventoryList) {
%>
<tr>
    <td><%= item.get("id") %></td>
    <td><%= item.get("name") %></td>
    <td><%= item.get("quantity") %></td>
    <td><%= item.get("price") %></td>
</tr>
<%
    }
%>
</table>

<%
    } else {
%>
<p>No inventory data available.</p>
<%
    }
%>

</body>
</html>
