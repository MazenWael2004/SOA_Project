<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ page import="java.util.List, java.util.Map" %>
<html>
<head>
    <title>Customer Profile</title>
    <style>
        table { border-collapse: collapse; width: 70%; margin: 20px auto; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        h2 { text-align: center; }
    </style>
</head>
<body>
<h2>Customer Profile</h2>

<%
    List<Map<String,Object>> customerList = (List<Map<String,Object>>) request.getAttribute("customerList");
    if (customerList != null && !customerList.isEmpty()) {
%>

<table>
<tr>
    <th>ID</th>
    <th>Name</th>
    <th>Email</th>
    <th>Phone</th>
    <th>Loyalty Points</th>
</tr>
<%
    for (Map<String,Object> customer : customerList) {
%>
<tr>
    <td><%= customer.get("id") %></td>
    <td><%= customer.get("name") %></td>
    <td><%= customer.get("email") %></td>
    <td><%= customer.get("phone") %></td>
    <td><%= customer.get("points") %></td>
</tr>
<%
    }
%>
</table>

<%
    } else {
%>
<p style="text-align: center;">No customer data available.</p>
<%
    }
%>

</body>
</html>
