package soa.project;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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
    private static final String ORDER_SERVICE_PORT = "5001";
    private static final String PRICING_SERVICE_PORT = "5003";
    private static final String INVENTORY_SERVICE_PORT = "5002";

    private final HttpClient client = HttpClient.newHttpClient();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        String orderID = req.getParameter("order_id");
        if (orderID == null || orderID.isEmpty()) {
            req.setAttribute("error", "Missing order_id parameter.");
            req.getRequestDispatcher("confirmation.jsp").forward(req, resp);
            return;
        }

        try {
            JSONObject orderJson = fetchOrder(orderID);
            List<Map<String, Object>> productsList = buildProductDetails(orderJson);

            req.setAttribute("orderID", orderJson.getInt("order_id"));
            req.setAttribute("productsList", productsList);
            req.setAttribute("totalAmount", orderJson.getDouble("total_amount"));

            req.getRequestDispatcher("confirmation.jsp").forward(req, resp);

        } catch (Exception e) {
            e.printStackTrace();
            req.setAttribute("error", "Failed to load order details.");
            req.getRequestDispatcher("confirmation.jsp").forward(req, resp);
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        String customerID = req.getParameter("customerID");
        String[] productIDs = req.getParameterValues("productID[]");
        String[] quantities = req.getParameterValues("quantity[]");

        if (customerID == null || productIDs == null || quantities == null ||
                productIDs.length != quantities.length) {

            req.setAttribute("error", "Invalid order parameters.");
            req.getRequestDispatcher("confirmation.jsp").forward(req, resp);
            return;
        }

        try {
            JSONArray products = buildProductsArray(productIDs, quantities);

            double totalAmount = calculatePrice(products);
            int orderID = createOrder(customerID, products, totalAmount);

            JSONObject orderJson = fetchOrder(String.valueOf(orderID));
            List<Map<String, Object>> productsList = buildProductDetails(orderJson);

            req.setAttribute("orderID", orderID);
            req.setAttribute("productsList", productsList);
            req.setAttribute("totalAmount", totalAmount);

            req.getRequestDispatcher("confirmation.jsp").forward(req, resp);

        } catch (Exception e) {
            e.printStackTrace();
            req.setAttribute("error", "Error processing order.");
            req.getRequestDispatcher("confirmation.jsp").forward(req, resp);
        }
    }

    

    private JSONObject fetchOrder(String orderID) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + ORDER_SERVICE_PORT + "/api/orders/" + orderID))
                .GET()
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return new JSONObject(response.body());
    }

    private JSONArray buildProductsArray(String[] ids, String[] quantities) {
        JSONArray products = new JSONArray();
        for (int i = 0; i < ids.length; i++) {
            JSONObject p = new JSONObject();
            p.put("product_id", Integer.parseInt(ids[i]));
            p.put("quantity", Integer.parseInt(quantities[i]));
            products.put(p);
        }
        return products;
    }

    private double calculatePrice(JSONArray products) throws Exception {
        JSONObject payload = new JSONObject();
        payload.put("products", products);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + PRICING_SERVICE_PORT + "/api/pricing/calculate"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(payload.toString()))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return new JSONObject(response.body()).getDouble("total_amount");
    }

    private int createOrder(String customerID, JSONArray products, double totalAmount) throws Exception {
        JSONObject payload = new JSONObject();
        payload.put("customer_id", Integer.parseInt(customerID));
        payload.put("products", products);
        payload.put("total_amount", totalAmount);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + ORDER_SERVICE_PORT + "/api/orders/create"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(payload.toString()))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return new JSONObject(response.body()).getInt("order_id");
    }

    private List<Map<String, Object>> buildProductDetails(JSONObject orderJson) throws Exception {
        JSONArray productsArray = orderJson.getJSONArray("products");
        List<Map<String, Object>> productsList = new ArrayList<>();

        for (int i = 0; i < productsArray.length(); i++) {
            JSONObject p = productsArray.getJSONObject(i);
            int productId = p.getInt("product_id");
            int quantity = p.getInt("quantity");

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(BASE_URL + INVENTORY_SERVICE_PORT + "/api/inventory/check/" + productId))
                    .GET()
                    .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            JSONObject prodJson = new JSONObject(response.body());

            Map<String, Object> map = new HashMap<>();
            map.put("id", productId);
            map.put("name", prodJson.getString("product_name"));
            map.put("quantity", quantity);
            map.put("price", prodJson.getDouble("unit_price"));

            productsList.add(map);
        }
        return productsList;
    }
}
