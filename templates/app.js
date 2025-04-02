// Function to ping the server and check connection status
const ping = async () => {
  try {
    const response = await fetch("/api/connection");
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching /api/connection:", error);
    return null;
  }
};

// Function to fetch model details from the server
const getModelsDetails = async () => {
  try {
    const response = await fetch("/api/connection/stats");
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching /api/connection/stats:", error);
    return null;
  }
};

// Function to format and display model details
const displayModelDetails = (models, element) => {
  if (!element) {
    console.error("Element for displaying model details not found.");
    return;
  }

  if (models && models.available && models.available.length > 0) {
    let formattedOutput = "<h3>MODELS:</h3>";
    let formatted_for_model_picker = `<option value="auto">Auto</option>`;

    models.available.forEach((item) => {
      formattedOutput += `<p>Name/Model: ${item.name}/${item.model}</p>`;
      formatted_for_model_picker += `<option value="${item.model}">${item.name}</option>`;
    });

    element.innerHTML = formattedOutput;
    modelPicker.innerHTML = formatted_for_model_picker;
  } else {
    element.innerText = "<h3>No models found in server.</h3>";
    modelPicker.innerHTML = "Unable to connect to server";
  }
};

const modelPicker = (models) => {
  const element = document.getElementById("model-picker");
  
  if (models && models.available && models.available.length > 0) {
    let formatted_for_model_picker = `<option value="auto">Auto</option>`;

    models.available.forEach((item) => {
      formatted_for_model_picker += `<option value="${item.model}">${item.name}</option>`;
    });

    element.innerHTML = formatted_for_model_picker;
  } else {
    element.innerHTML = "Unable to connect to server";
  }
};

// Function to display connection details
const displayConnectionDetails = (connection, element) => {
  if (!element) {
    console.error("Element for displaying connection details not found.");
    return;
  }

  if (connection) {
    element.innerHTML = `<h3>CONNECTION INFO:</h3>
                         <p>Host: ${connection.host}</p>
                         <p>Port: ${connection.port}</p>
                         <p>Status: ${connection.status} - CONNECTED</p>`;
  } else {
    element.innerText = "<h3>UNABLE TO CONNECT TO SERVER</h3>";
  }
};

// Function to handle loading state
const loading = async (func, sec, loadingPage = false) => {
  const inputBox = document.getElementById("prompt");
  const inputBoxButton = document.getElementById("prompt-btn");
  const mainContainer = document.getElementById("main");

  if (!mainContainer) {
    console.error("Main container element not found.");
    return;
  }

  // Show loading state if enabled
  if (loadingPage) {
    mainContainer.innerHTML = `<h1>LOADING...</h1>`;
  }

  // Disable input elements if they exist
  if (inputBox) inputBox.disabled = true;
  if (inputBoxButton) inputBoxButton.disabled = true;

  try {
    // Execute the provided function
    await func();
  } catch (error) {
    console.error("Error during loading function:", error);
    mainContainer.innerHTML = `<h1>ERROR: ${error.message}</h1>`;
  } finally {
    // Re-enable input elements after the specified delay
    setTimeout(() => {
      if (inputBox) inputBox.disabled = false;
      if (inputBoxButton) inputBoxButton.disabled = false;
    }, sec);
  }
};

// Main function to initialize the page
const initDataPage = async () => {
  const connectionsInfo = document.getElementById("connectionsInfo");
  const printModel = document.getElementById("print_models");
  const printActiveModel = document.getElementById("print_active_models");

  if (!connectionsInfo || !printModel || !printActiveModel) {
    console.error("One or more required elements not found.");
    return;
  }

  try {
    // Fetch connection and model details
    const connection = await ping();
    const models = await getModelsDetails();

    // Display connection and model details
    displayConnectionDetails(connection, connectionsInfo);
    displayModelDetails(models, printModel);

    // Display active models (if needed)
    if (models && models.active && models.active.length > 0) {
      let formattedOutput = "<h3>ACTIVE MODELS:</h3>";

      models.active.forEach((item) => {
        formattedOutput += `<p>Name/Model: ${item.name}/${item.model}</p>`;
      });

      printActiveModel.innerHTML = formattedOutput;
    } else {
      printActiveModel.innerText = "Currently No Active Models Present.";
    }
  } catch (error) {
    console.error("Error initializing page:", error);
    if (connectionsInfo) connectionsInfo.innerText = "ERROR LOADING DATA";
    if (printModel) printModel.innerText = "ERROR LOADING MODELS";
    if (printActiveModel)
      printActiveModel.innerText = "ERROR LOADING ACTIVE MODELS";
  }
};

const getAIresToggle = () => {};

// Initialize the page when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  loading(initDataPage, 1000);
});
