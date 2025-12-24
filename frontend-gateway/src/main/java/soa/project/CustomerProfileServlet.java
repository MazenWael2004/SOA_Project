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

import org.json.JSONObject;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@WebServlet("/customerProfile")
public class CustomerProfileServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        String customerId = request.getParameter("customerId");
        if (customerId == null || customerId.isEmpty()) {
            response.sendError(HttpServletResponse.SC_BAD_REQUEST, "Missing customerId parameter.");
            return;
        }
        int customerIdInt;
        try {
            customerIdInt = Integer.parseInt(customerId);
        } catch (NumberFormatException e) {
            response.sendError(HttpServletResponse.SC_BAD_REQUEST, "Invalid customerId parameter.");
            return;
        }
        String baseUrl = "http://localhost:";
        String customerServicePort = "5004";
        String customerApiUrl = baseUrl + customerServicePort + "/api/customers/" + customerIdInt;

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest customerRequest = HttpRequest.newBuilder()
                .uri(URI.create(customerApiUrl))
                .header("Content-Type", "application/json")
                .GET()
                .build();

        try {
            HttpResponse<String> customerResponse = client.send(customerRequest, HttpResponse.BodyHandlers.ofString());

            if (customerResponse.statusCode() != 200) {
                response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
                        "Flask service returned status: " + customerResponse.statusCode());
                return;
            }

            String responseBody = customerResponse.body();

            // Parse single JSON object from Flask
            JSONObject customer = new JSONObject(responseBody);
            Map<String, Object> map = new HashMap<>();
            map.put("id", customer.getInt("customer_id"));
            map.put("name", customer.getString("name"));
            map.put("email", customer.getString("email"));
            map.put("phone", customer.getString("phone"));
            map.put("points", customer.getInt("loyalty_points"));

            // Wrap in a list to reuse existing JSP
            List<Map<String, Object>> customerList = new ArrayList<>();
            customerList.add(map);

            // Forward to JSP
            request.setAttribute("customerList", customerList);
            request.getRequestDispatcher("customerProfile.jsp").forward(request, response);

        } catch (Exception e) {
            e.printStackTrace();
            response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
                    "Error fetching or parsing customer data: " + e.getMessage());
        }
    }
}
