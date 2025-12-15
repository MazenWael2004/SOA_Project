package soa.project;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import java.io.IOException;

public class DemoServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/html");
        response.getWriter().println("<h1>Hello from DemoServlet!</h1>");
    }
}
