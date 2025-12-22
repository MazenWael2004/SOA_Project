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

@WebServlet("/ordersHistory")
public class OrderHistoryServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String BASEURL = "http://localhost:";
        String ORDER_SERVICE_PORT = "5001";
        String ORDER_API_URL = BASEURL + ORDER_SERVICE_PORT + "/api/orders/by_customer/2";

        String INVENTORY_SERVICE_PORT = "5002";
        String INVENTORY_API_URL = BASEURL + INVENTORY_SERVICE_PORT + "/api/inventory";

        HttpClient client = HttpClient.newHttpClient();

        try {
            HttpRequest inventoryRequest = HttpRequest.newBuilder()
                    .uri(URI.create(INVENTORY_API_URL))
                    .header("Content-Type", "application/json")
                    .GET()
                    .build();

            HttpResponse<String> inventoryResponse = client.send(inventoryRequest, HttpResponse.BodyHandlers.ofString());
            JSONArray inventoryArray = new JSONArray(inventoryResponse.body());
            Map<Integer, String> productIdToName = new HashMap<>();
            for (int i = 0; i < inventoryArray.length(); i++) {
                JSONObject product = inventoryArray.getJSONObject(i);
                productIdToName.put(product.getInt("product_id"), product.getString("product_name"));
            }

            HttpRequest orderRequest = HttpRequest.newBuilder()
                    .uri(URI.create(ORDER_API_URL))
                    .header("Content-Type", "application/json")
                    .GET()
                    .build();

            HttpResponse<String> orderResponse = client.send(orderRequest, HttpResponse.BodyHandlers.ofString());
            JSONArray ordersArray = new JSONArray(orderResponse.body());

            List<Map<String, Object>> orderList = new ArrayList<>();

            // --- 3. Map orders and product details ---
            for (int i = 0; i < ordersArray.length(); i++) {
                JSONObject order = ordersArray.getJSONObject(i);
                Map<String, Object> orderMap = new HashMap<>();
                orderMap.put("id", order.getInt("order_id"));
                orderMap.put("total", order.getDouble("total_amount"));
                orderMap.put("customerID", order.getInt("customer_id"));

                JSONArray productsArray = order.getJSONArray("products");
                List<Map<String, Object>> productsList = new ArrayList<>();

                for (int j = 0; j < productsArray.length(); j++) {
                    JSONObject product = productsArray.getJSONObject(j);
                    Map<String, Object> productMap = new HashMap<>();
                    int productId = product.getInt("product_id");
                    productMap.put("name", productIdToName.getOrDefault(productId, "Unknown Product"));
                    productMap.put("quantity", product.getInt("quantity"));
                    productMap.put("unit_price", product.getDouble("unit_price"));
                    productsList.add(productMap);
                }

                orderMap.put("products", productsList);
                orderList.add(orderMap);
            }

            request.setAttribute("orderList", orderList);
            request.getRequestDispatcher("ordersHistory.jsp").forward(request, response);

        } catch (Exception e) {
            e.printStackTrace();
            response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
                    "Error fetching order or product data: " + e.getMessage());
        }
    }
}
