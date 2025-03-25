document.addEventListener('DOMContentLoaded', () => {
    const resultContainer = document.getElementById('resultContainer');
    const resultData = JSON.parse(localStorage.getItem("resultData"));
    
    if (!resultData) {
      resultContainer.innerHTML = "<p class='text-center text-red-600'>No result data found. Please submit data first.</p>";
      return;
    }
    
    let html = `<div class="space-y-8">`;
    
    // Bill Details Section
    html += `
      <div class="p-6 border rounded bg-gray-50 shadow-md">
        <h2 class="text-3xl font-bold mb-4 text-primary">Bill Details</h2>
        <p class="text-lg"><strong>Month:</strong> ${resultData.bill.month}</p>
        <p class="text-lg"><strong>Total Units:</strong> ${resultData.bill.total_units} kWh</p>
        <p class="text-lg"><strong>Bill Amount:</strong> ₹${resultData.bill.bill_amount}</p>
        <p class="text-lg"><strong>Suggestion:</strong> ${resultData.bill.recommendation}</p>
      </div>
    `;
    
    // Basic Predictions Section
    html += `
      <div class="p-6 border rounded bg-gray-50 shadow-md">
        <h2 class="text-3xl font-bold mb-4 text-primary">Basic Predictions</h2>
        <p class="text-lg"><strong>Next Month Bill:</strong> ₹${resultData.predictions.predicted_next_bill.toFixed(2)}</p>
        <p class="text-lg"><strong>Next Month Consumption:</strong> ${resultData.predictions.predicted_next_total_units.toFixed(2)} kWh</p>
      </div>
    `;
    
    // Appliance-Level Predictions & Efficiency Alerts Section
    html += `
      <div class="p-6 border rounded bg-gray-50 shadow-md">
        <h2 class="text-3xl font-bold mb-4 text-primary">Appliance Predictions</h2>
        <ul class="list-disc list-inside text-lg">`;
    for (let appliance in resultData.predictions.appliance_level_predictions) {
      html += `
        <li>
          <strong>${appliance}:</strong> Predicted Usage: ${resultData.predictions.appliance_level_predictions[appliance].toFixed(2)} kWh.
          <br/><small>Efficiency: ${resultData.predictions.appliance_efficiency_alerts[appliance]}</small>
        </li>`;
    }
    html += `
        </ul>
      </div>
    `;
    
    // Energy Savings Simulation Section
    html += `
      <div class="p-6 border rounded bg-gray-50 shadow-md">
        <h2 class="text-3xl font-bold mb-4 text-primary">Energy Savings</h2>
        <ul class="list-disc list-inside text-lg">`;
    for (let appName in resultData.predictions.energy_savings_simulation) {
      html += `<li><strong>${appName}:</strong> Estimated Saving: ₹${resultData.predictions.energy_savings_simulation[appName].toFixed(2)}</li>`;
    }
    html += `
        </ul>
      </div>
    `;
    
    // Additional Insights Section
    html += `
      <div class="p-6 border rounded bg-gray-50 shadow-md">
        <h2 class="text-3xl font-bold mb-4 text-primary">Additional Insights</h2>
        <p class="text-lg"><strong>Carbon Footprint:</strong> ${resultData.predictions.carbon_footprint.toFixed(2)} kg CO₂</p>
        <p class="text-lg"><strong>Seasonal Forecast:</strong> ${resultData.predictions.predicted_seasonal_consumption.toFixed(2)} kWh</p>
        <p class="text-lg"><strong>Tariff Advice:</strong> ${resultData.predictions.dynamic_tariff_suggestion}</p>
        <p class="text-lg"><strong>Solar Savings:</strong> ₹${resultData.predictions.solar_energy_savings.toFixed(2)}</p>
        <p class="text-lg"><strong>Annual Projection:</strong> ₹${resultData.predictions.annual_financial_projection.toFixed(2)}</p>
        <p class="text-lg"><strong>Usage Benchmark:</strong> ${resultData.predictions.usage_benchmark}</p>
        <p class="text-lg"><strong>Anomaly Detection:</strong> ${resultData.predictions.anomaly_flag ? "Anomaly Detected" : "No Anomaly"}</p>
        <p class="text-lg"><strong>Peak Demand:</strong> ${resultData.predictions.peak_demand_prediction}</p>
      </div>
    `;
    
    html += `</div>`;
    resultContainer.innerHTML = html;
    
    document.getElementById('backButton').addEventListener('click', () => {
      window.location.href = "index.html";
    });
  });
  