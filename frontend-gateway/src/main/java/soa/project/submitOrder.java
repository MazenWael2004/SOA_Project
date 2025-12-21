package soa.project;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import org.json.JSONArray;
import org.json.JSONObject;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/submitOrder")
public class submitOrder extends HttpServlet {

    private static final String BASE_URL = "http://localhost:";
    private static final String PRICING_SERVICE_PORT = "5003";
    private static final String ORDER_SERVICE_PORT = "5001";

    @Override
protected void doGet(HttpServletRequest req, HttpServletResponse resp)
        throws ServletException, IOException {

    String orderID = req.getParameter("order_id");
    if (orderID == null || orderID.isEmpty()) {
        req.setAttribute("error", "Missing order_id parameter");
        req.getRequestDispatcher("confirmation.jsp").forward(req, resp);
        return;
    }

    HttpClient client = HttpClient.newHttpClient();

    try {
        // 1️⃣ Fetch order details
        String orderUrl = BASE_URL + ORDER_SERVICE_PORT + "/api/orders/" + orderID;
        HttpRequest orderReq = HttpRequest.newBuilder()
                .uri(URI.create(orderUrl))
                .header("Content-Type", "application/json")
                .GET()
                .build();

        HttpResponse<String> orderResp = client.send(orderReq, HttpResponse.BodyHandlers.ofString());
        JSONObject orderJson = new JSONObject(orderResp.body());

        JSONArray productsArray = orderJson.getJSONArray("products");
        List<Map<String, Object>> productsList = new ArrayList<>();

        // 2️⃣ Fetch product details for each product
        for (int i = 0; i < productsArray.length(); i++) {
    JSONObject p = productsArray.getJSONObject(i);
    int productId = p.getInt("product_id");
    int quantity = p.optInt("quantity", 0);

    // Call product/inventory service
    String productUrl = BASE_URL + "5002/api/products/" + productId;
    HttpRequest prodReq = HttpRequest.newBuilder()
            .uri(URI.create(productUrl))
            .GET()
            .build();

    HttpResponse<String> prodResp = client.send(prodReq, HttpResponse.BodyHandlers.ofString());
    JSONObject prodJson = new JSONObject(prodResp.body());

    Map<String,Object> map = new HashMap<>();
    map.put("id", productId);
    map.put("name", prodJson.getString("product_name"));    // correct field
    map.put("quantity", quantity);
    map.put("price", prodJson.getDouble("unit_price"));     // correct field
    productsList.add(map);
}


        // 3️⃣ Set attributes for JSP
        req.setAttribute("orderID", orderJson.getInt("order_id"));
        req.setAttribute("productsList", productsList);
        req.setAttribute("totalAmount", orderJson.optDouble("total_amount", 0.0));

        req.getRequestDispatcher("confirmation.jsp").forward(req, resp);

    } catch (Exception e) {
        e.printStackTrace();
        req.setAttribute("error", "Failed to fetch order details: " + e.getMessage());
        req.getRequestDispatcher("confirmation.jsp").forward(req, resp);
    }
}

    @Override
protected void doPost(HttpServletRequest request, HttpServletResponse resp) throws ServletException, IOException {
    String customerID = request.getParameter("customerID");
    String[] productIDs = request.getParameterValues("productID[]");
    String[] quantities = request.getParameterValues("quantity[]");

    if(customerID == null || productIDs == null || quantities == null){
        request.setAttribute("error", "Missing required parameters.");
        request.getRequestDispatcher("confirmation.jsp").forward(request, resp);
        return;
    }

    if(productIDs.length != quantities.length){
        request.setAttribute("error", "Mismatched number of Product IDs and quantities.");
        request.getRequestDispatcher("confirmation.jsp").forward(request, resp);
        return;
    }

    // Build products JSON array
    JSONArray products = new JSONArray();
    try {
        for(int i = 0; i < productIDs.length; i++){
            JSONObject product = new JSONObject();
            product.put("product_id", Integer.parseInt(productIDs[i]));
            product.put("quantity", Integer.parseInt(quantities[i]));
            products.put(product);
        }
    } catch(NumberFormatException e){
        request.setAttribute("error", "Invalid number format in product IDs or quantities.");
        request.getRequestDispatcher("confirmation.jsp").forward(request, resp);
        return;
    }

    HttpClient client = HttpClient.newHttpClient();

    // Call Pricing Service
    JSONObject pricingPayload = new JSONObject();
    pricingPayload.put("products", products);

    try {
        HttpRequest pricingRequest = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + PRICING_SERVICE_PORT + "/api/pricing/calculate"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(pricingPayload.toString()))
                .build();

        HttpResponse<String> pricingResponse = client.send(pricingRequest, HttpResponse.BodyHandlers.ofString());
        JSONObject pricingJson = new JSONObject(pricingResponse.body());

        if(!pricingJson.has("total_amount")){
            request.setAttribute("error", "Pricing service returned invalid data.");
            request.getRequestDispatcher("confirmation.jsp").forward(request, resp);
            return;
        }

        double totalAmount = pricingJson.getDouble("total_amount");

        // Create Order
        JSONObject orderPayload = new JSONObject();
        orderPayload.put("customer_id", Integer.parseInt(customerID));
        orderPayload.put("products", products);
        orderPayload.put("total_amount", totalAmount);

        HttpRequest orderRequest = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + ORDER_SERVICE_PORT + "/api/orders/create"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(orderPayload.toString()))
                .build();

        HttpResponse<String> orderCreationResponse = client.send(orderRequest, HttpResponse.BodyHandlers.ofString());
        JSONObject orderCreationJson = new JSONObject(orderCreationResponse.body());

        int status = orderCreationJson.optInt("status", 0);
        if(status != 201 || !orderCreationJson.has("order_id")){
            request.setAttribute("error", "Failed to create order: " + orderCreationResponse.body());
            request.getRequestDispatcher("confirmation.jsp").forward(request, resp);
            return;
        }

        int orderID = orderCreationJson.getInt("order_id");

        // Fetch created order details
        HttpRequest getOrderRequest = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + ORDER_SERVICE_PORT + "/api/orders/" + orderID))
                .header("Content-Type", "application/json")
                .GET()
                .build();

        HttpResponse<String> orderResponse = client.send(getOrderRequest, HttpResponse.BodyHandlers.ofString());
        JSONObject orderJson = new JSONObject(orderResponse.body());

        JSONArray productsArray = orderJson.getJSONArray("products");
        List<Map<String,Object>> productsList = new ArrayList<>();
        for(int i=0; i<productsArray.length(); i++){
            JSONObject p = productsArray.getJSONObject(i);
            Map<String,Object> map = new HashMap<>();
            map.put("id", p.optInt("product_id", i+1));
            map.put("name", p.optString("name", "N/A"));
            map.put("quantity", p.optInt("quantity", 0));
            map.put("price", p.optDouble("price", 0.0));
            productsList.add(map);
        }

        request.setAttribute("productsList", productsList);
        request.setAttribute("totalAmount", orderJson.optDouble("total_amount", totalAmount));
        request.setAttribute("orderID", orderID);

        // Forward to JSP for server-side table rendering
        request.getRequestDispatcher("confirmation.jsp").forward(request, resp);

    } catch(Exception e){
        e.printStackTrace();
        request.setAttribute("error", "Error processing order: " + e.getMessage());
        request.getRequestDispatcher("confirmation.jsp").forward(request, resp);
    }
}
}
