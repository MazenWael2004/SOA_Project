<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>

<html>
<body>
<h2>Confirm order!</h2>
<% String order_id = request.getParameter("order_id"); %>
<pre id="output"></pre>
<script>
    fetch('submitOrder?order_id=<%= order_id %>')
    .then(response => response.json())
    .then(data =>document.getElementById("output").innerText = JSON.stringify(data,null,2) )
</script>

</body>
</html>
