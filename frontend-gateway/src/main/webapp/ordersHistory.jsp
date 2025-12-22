<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ page import="java.util.List, java.util.Map" %>
<html>
<head>
    <title>Order History</title>
</head>
<body>
<%
List<Map<String,Object>> orderList = (List<Map<String,Object>>) request.getAttribute("orderList");
if(orderList != null && !orderList.isEmpty()) {
%>
<h2>Order History for Customer ID: <%= orderList.get(0).get("customerID") %> </h2>



<%
for(Map<String,Object> order : orderList){
    List<Map<String,Object>> products = (List<Map<String,Object>>) order.get("products");
%>
<h3>Order ID: <%= order.get("id") %> | Total: $<%= order.get("total") %></h3>
<table border="1">
<tr>
    <th>Product Name</th>
    <th>Quantity</th>
    <th>Unit Price</th>
</tr>
<%
    for(Map<String,Object> p : products){
%>
<tr>
    <td><%= p.get("name") %></td>
    <td><%= p.get("quantity") %></td>
    <td>$<%= p.get("unit_price") %></td>
</tr>
<%
    }
%>
</table>
<hr/>
<%
}
%>

<%
} else {
%>
<p>No orders found.</p>
<%
}
%>
</body>
</html>
