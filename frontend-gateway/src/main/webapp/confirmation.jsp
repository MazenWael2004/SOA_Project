<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ page import="java.util.List, java.util.Map" %>

<html>
<head>
    <title>Order Confirmation</title>
    <style>
        table { border-collapse: collapse; width: 70%; margin-top: 20px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .error { color: red; }
    </style>
</head>
<body>

<h2>Order Confirmation</h2>

<%
    String error = (String) request.getAttribute("error");
    if(error != null){
%>
    <p class="error"><%= error %></p>
<%
    } else {
        Integer orderID = (Integer) request.getAttribute("orderID");
        List<Map<String,Object>> productsList = (List<Map<String,Object>>) request.getAttribute("productsList");
        Double totalAmount = (Double) request.getAttribute("totalAmount");

        if(orderID != null){
%>
<p><strong>Order ID:</strong> <%= orderID %></p>
<%
        }

        if(productsList != null && !productsList.isEmpty()){
%>
<table>
    <tr>
        <th>Product ID</th>
        <th>Product</th>
        <th>Quantity</th>
        <th>Price</th>
    </tr>
<%
        for(Map<String,Object> item : productsList){
%>
    <tr>
        <td><%= item.get("id") %></td>
        <td><%= item.get("name") %></td>
        <td><%= item.get("quantity") %></td>
        <td>$<%= item.get("price") %></td>
    </tr>
<%
        }
%>
</table>

<p><strong>Total Amount:</strong> $<%= totalAmount %></p>

<%
        } else {
%>
<p>No order details available.</p>
<%
        }
    }
%>

</body>
</html>
