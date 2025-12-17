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

@WebServlet("/inventory")
public class InventoryServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String baseUrl = "http://localhost:";
        String inventoryServicePort = "5002";
        String inventoryApiUrl = baseUrl + inventoryServicePort + "/api/inventory";

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest inventoryRequest = HttpRequest.newBuilder()
                .uri(URI.create(inventoryApiUrl))
                .header("Content-Type", "application/json")
                .GET()
                .build();

        try {
            HttpResponse<String> inventoryResponse = client.send(inventoryRequest, HttpResponse.BodyHandlers.ofString());
            String responseBody = inventoryResponse.body();

            JSONArray inventoryArray = new JSONArray(responseBody);
            List<Map<String, Object>> inventoryList = new ArrayList<>();

            // Map JSON keys to generic keys for JSP
            for (int i = 0; i < inventoryArray.length(); i++) {
                JSONObject item = inventoryArray.getJSONObject(i);
                Map<String, Object> map = new HashMap<>();
                map.put("id", item.getInt("product_id"));
                map.put("name", item.getString("product_name"));
                map.put("quantity", item.getInt("quantity_availabe")); // matches Flask API key
                map.put("price", item.getDouble("unit_price"));
                inventoryList.add(map);
            }

            request.setAttribute("inventoryList", inventoryList);
            request.getRequestDispatcher("inventory.jsp").forward(request, response);

        } catch (Exception e) {
            throw new ServletException("Error fetching inventory from Flask service", e);
        }
    }
}
