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
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String baseUrl ="http://localhost:";
        String orderServicePort = "5001";
        String orderID = req.getParameter("order_id");
        String endGetOrderURL= baseUrl+orderServicePort + "/orders/" + orderID;

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
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    
        
    }
    //submit the order to the orders service
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse resp) throws ServletException, IOException {
        //paths
        String baseUrl ="http://localhost:";
        String pricingServicePort = "5003";
        String orderServicePort = "5001";
        // get values from form
        String customerID = request.getParameter("customerID");
        String productIDs[] = request.getParameterValues("productID[]");
        String quantities[] = request.getParameterValues("quantity[]");
        // check quantities length matches productids 
        if(productIDs.length != quantities.length){
            throw new ServletException("Mismatched number of Product IDs and number of quantities");
        }
        //for each product add to json object products
        JSONArray products = new JSONArray();
        for( int i = 0; i < productIDs.length; i ++){
            JSONObject product = new JSONObject();
            product.put("product_id", Integer.parseInt(productIDs[i]));
            product.put("quantity",Integer.parseInt(quantities[i]));
            products.put(product);
        }
        JSONObject productsQuantityPayload = new JSONObject();
        productsQuantityPayload.put("products",products);
        //send request to pricing service to get total amount

        String endPricingServiceURL = baseUrl + pricingServicePort + "/api/pricing/calculate";
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest pricingRequest = HttpRequest.newBuilder()
        .uri(URI.create(endPricingServiceURL))
        .header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString(productsQuantityPayload.toString()))
        .build();
        
        try {
            HttpResponse<String> pricingResponse = client.send(pricingRequest, HttpResponse.BodyHandlers.ofString());
            // get the response body
            String responseBody = pricingResponse.body();
            JSONObject pricingJson = new JSONObject(responseBody);
            double totalAmount = pricingJson.getDouble("total_amount"); 
            
            // //temporary defualt value while Pricing Service is being made
            // double totalAmount = 100;

            // create request to Orders Service

            String endCreateOrderUrl = baseUrl + orderServicePort + "/api/orders/create" ;
            JSONObject orderPayload = new JSONObject();
            orderPayload.put("customer_id",Integer.parseInt(customerID));
            orderPayload.put("products", products);
            orderPayload.put("total_amount", totalAmount);
            HttpRequest orderRequest = HttpRequest.newBuilder()
            .uri(URI.create(endCreateOrderUrl))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(orderPayload.toString()))
            .build();
        HttpResponse<String> orderCreationResponse = client.send(orderRequest, HttpResponse.BodyHandlers.ofString());
        String orderCreationResponseBody = orderCreationResponse.body();
        JSONObject orderCreationResponseJson = new JSONObject(orderCreationResponseBody);
        int status = orderCreationResponseJson.getInt("status");
        int orderID = orderCreationResponseJson.getInt("order_id");
        if(status == 201){
            resp.sendRedirect("confirmation.jsp?order_id=" + orderID);
        }
        else{
            resp.getWriter().println("Failed to Create Order");
        }
        } catch (Exception e) {
             throw new ServletException("Request interrupted", e);
        }


    }
    
}
