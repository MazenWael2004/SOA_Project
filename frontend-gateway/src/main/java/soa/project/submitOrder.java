package soa.project;

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
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String orderID = req.getParameter("order_id");
        if(orderID == null || orderID.isEmpty()){
            resp.getWriter().println("Missing order_id parameter");
            return;
        }

        String endGetOrderURL = BASE_URL + ORDER_SERVICE_PORT + "/orders/" + orderID;

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest orderRequest = HttpRequest.newBuilder()
                .uri(URI.create(endGetOrderURL))
                .header("Content-Type", "application/json")
                .GET()
                .build();

        try {
            HttpResponse<String> orderResponse = client.send(orderRequest, HttpResponse.BodyHandlers.ofString());
            resp.setContentType("application/json");
            resp.getWriter().write(orderResponse.body());
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            resp.getWriter().println("Failed to fetch order details: " + e.getMessage());
        }
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse resp) throws ServletException, IOException {
        String customerID = request.getParameter("customerID");
        String[] productIDs = request.getParameterValues("productID[]");
        String[] quantities = request.getParameterValues("quantity[]");

        if(customerID == null || productIDs == null || quantities == null){
            resp.getWriter().println("Missing required parameters.");
            return;
        }

        if(productIDs.length != quantities.length){
            resp.getWriter().println("Mismatched number of Product IDs and quantities.");
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
            resp.getWriter().println("Invalid number format in product IDs or quantities.");
            return;
        }

        // Call Pricing Service
        JSONObject pricingPayload = new JSONObject();
        pricingPayload.put("products", products);

        HttpClient client = HttpClient.newHttpClient();
        String endPricingServiceURL = BASE_URL + PRICING_SERVICE_PORT + "/api/pricing/calculate";
        HttpRequest pricingRequest = HttpRequest.newBuilder()
                .uri(URI.create(endPricingServiceURL))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(pricingPayload.toString()))
                .build();

        double totalAmount;
        try {
            HttpResponse<String> pricingResponse = client.send(pricingRequest, HttpResponse.BodyHandlers.ofString());
            JSONObject pricingJson = new JSONObject(pricingResponse.body());

            if(!pricingJson.has("total_amount")){
                resp.getWriter().println("Pricing service failed or returned invalid data: " + pricingResponse.body());
                return;
            }
            totalAmount = pricingJson.getDouble("total_amount");

        } catch(Exception e){
            e.printStackTrace();
            resp.getWriter().println("Error calling pricing service: " + e.getMessage());
            return;
        }

        // Call Order Service to create order
        JSONObject orderPayload = new JSONObject();
        try {
            orderPayload.put("customer_id", Integer.parseInt(customerID));
            orderPayload.put("products", products);
            orderPayload.put("total_amount", totalAmount);
        } catch(NumberFormatException e){
            resp.getWriter().println("Invalid customer ID format.");
            return;
        }

        String endCreateOrderUrl = BASE_URL + ORDER_SERVICE_PORT + "/api/orders/create";
        HttpRequest orderRequest = HttpRequest.newBuilder()
                .uri(URI.create(endCreateOrderUrl))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(orderPayload.toString()))
                .build();

        try {
            HttpResponse<String> orderCreationResponse = client.send(orderRequest, HttpResponse.BodyHandlers.ofString());
            JSONObject orderCreationJson = new JSONObject(orderCreationResponse.body());

            int status = orderCreationJson.optInt("status", 0);
            if(status != 201 || !orderCreationJson.has("order_id")){
                resp.getWriter().println("Failed to create order: " + orderCreationResponse.body());
                return;
            }

            int orderID = orderCreationJson.getInt("order_id");
            resp.sendRedirect("confirmation.jsp?order_id=" + orderID);

        } catch(Exception e){
            e.printStackTrace();
            resp.getWriter().println("Error creating order: " + e.getMessage());
        }
    }
}
