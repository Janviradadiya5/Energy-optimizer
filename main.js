document.addEventListener('DOMContentLoaded', () => {
    // If user isn't registered, show the registration modal.
    if (!localStorage.getItem("loggedInUser")) {
      document.getElementById("registrationModal").classList.remove("hidden");
    }
  
    // Registration Modal "Done" button handler.
    const regDoneButton = document.getElementById("regDoneButton");
    if (regDoneButton) {
      regDoneButton.addEventListener("click", async () => {
        const regUserId = document.getElementById("regUserId").value.trim();
        if (!regUserId) {
          alert("Please enter a valid User ID.");
          return;
        }
        try {
          const response = await fetch('http://127.0.0.1:5000/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: regUserId })
          });
          if (response.ok) {
            const data = await response.json();
            // Save the registered user data in localStorage.
            localStorage.setItem("loggedInUser", JSON.stringify(data));
            document.getElementById("registrationModal").classList.add("hidden");
            document.getElementById("userIdDisplay").innerText = "Welcome, " + data.user_id;
            document.getElementById("mainContent").classList.remove("hidden");
          } else {
            const err = await response.json();
            alert("Registration Error: " + err.error);
          }
        } catch (error) {
          console.error("Registration error:", error);
          alert("Registration network error!");
        }
      });
    }
  
    // If user is not registered, do not continue with the rest of the script.
    if (!localStorage.getItem("loggedInUser")) return;
  
    const form = document.getElementById('energyForm');
    const addApplianceButton = document.getElementById('addAppliance');
    const appliancesSection = document.getElementById('appliancesSection');
  
    // Function to add a new appliance input group.
    function addApplianceInput() {
      const applianceDiv = document.createElement('div');
      applianceDiv.classList.add('appliance', 'mb-6', 'p-6', 'border', 'rounded-md', 'shadow-md');
      applianceDiv.innerHTML = `
        <div class="mb-4">
          <label class="block text-lg font-body text-gray-700 mb-1">Appliance Name</label>
          <input type="text" class="applianceName w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary" placeholder="Enter appliance name" required />
        </div>
        <div class="mb-4">
          <label class="block text-lg font-body text-gray-700 mb-1">Power Rating (W)</label>
          <input type="number" class="powerRating w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary" placeholder="Enter power rating" required />
        </div>
        <div class="mb-4">
          <label class="block text-lg font-body text-gray-700 mb-1">Daily Usage Hours</label>
          <input type="number" class="usageHours w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary" placeholder="Enter usage hours" required />
        </div>
      `;
      appliancesSection.appendChild(applianceDiv);
    }
    
    addApplianceButton.addEventListener('click', addApplianceInput);
  
    // Handle form submission: submit data and redirect to result.html.
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const loggedInUser = JSON.parse(localStorage.getItem("loggedInUser"));
      const userId = loggedInUser.user_id;
      const month = document.getElementById('month').value;
      const totalUnits = parseFloat(document.getElementById('totalUnits').value);
      const billAmount = parseFloat(document.getElementById('billAmount').value);
      
      // Gather appliance details.
      const applianceDivs = document.querySelectorAll('.appliance');
      const appliances = Array.from(applianceDivs).map(div => {
        const name = div.querySelector('.applianceName').value;
        const powerRating = parseFloat(div.querySelector('.powerRating').value);
        const usageHours = parseFloat(div.querySelector('.usageHours').value);
        return { name, power_rating: powerRating, usage_hours: usageHours };
      });
      
      const payload = {
        user_id: userId,
        month,
        total_units: totalUnits,
        bill_amount: billAmount,
        appliances: appliances.map(appl => ({
          name: appl.name,
          power_rating: appl.power_rating,
          usage_hours: appl.usage_hours
        }))
      };
      
      try {
        const response = await fetch('http://127.0.0.1:5000/api/submit_data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (response.ok) {
          const data = await response.json();
          // Save the result and redirect to result.html.
          localStorage.setItem("resultData", JSON.stringify(data));
          window.location.href = "result.html";
        } else {
          alert('Error submitting data!');
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Network error!');
      }
    });
  });
  
