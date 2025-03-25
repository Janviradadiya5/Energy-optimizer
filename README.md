# Energy-optimizer
# Energy Optimizer

**Energy Optimizer** is a full-stack application that helps users analyze and optimize their energy consumption. Users register using a unique User ID, submit their monthly electricity bill details and appliance data, and receive personalized predictions and insights. All user data is stored uniquely based on the User ID so that each user's records remain separate.

---

## Features

- **User Registration & Persistent Login**  
  - On the index page, if no user is registered (i.e. no User ID stored in localStorage), a registration modal appears.
  - The user enters a unique User ID and clicks “Done.” This ID is verified via a backend API endpoint (`/api/register`) to ensure uniqueness.
  - Once registered, the User ID is stored in localStorage. On subsequent visits, the site loads directly with the stored User ID (without requiring re-registration).

- **Energy Data Submission**  
  - Users can enter details such as:
    - **Month** (e.g., Jan 2023)
    - **Total Units (kWh)**
    - **Bill Amount (₹)**
    - **Appliance Usage** (Name, Power Rating, Daily Usage Hours)
  - This data is sent along with the User ID to the backend API endpoint (`/api/submit_data`).

- **Personalized Predictions & Insights**  
  The backend processes the data and provides several predictions, including:
  1. **Next Month's Bill Prediction:** Forecasted amount for the upcoming bill.
  2. **Overall Energy Consumption Prediction:** Estimated kWh for the next month.
  3. **Appliance-Level Predictions & Efficiency Alerts:** Predictions for each appliance’s energy usage and alerts for efficiency drops.
  4. **Energy Savings Simulation:** Calculates potential savings if appliance usage is reduced.
  5. **Carbon Footprint Calculation:** Estimates CO₂ emissions (using 0.82 kg CO₂ per kWh).
  6. **Seasonal Consumption Forecast:** Adjusts predictions based on seasonal factors (e.g., 10% increase in summer, 10% decrease in winter).
  7. **Dynamic Tariff Suggestion:** Recommends off-peak hours (e.g., 12 AM - 6 AM) for operating appliances.
  8. **Solar Energy Savings:** Estimates potential savings if solar power is used.
  9. **Long-Term Financial Projection:** Projects annual electricity expenditure.
  10. **Usage Benchmark:** Compares user consumption against a set benchmark (e.g., 200 kWh).
  11. **Anomaly Detection:** Identifies if the current bill deviates significantly (e.g., more than 2× standard deviation) from historical data.
  12. **Peak Demand Prediction:** Indicates if the current consumption reaches or exceeds
