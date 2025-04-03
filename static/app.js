// Function to ping the server and check connection status
const pingServer = async () => {
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
const fetchModelDetails = async () => {
  try {
    const response = await fetch("/api/connection/stats");
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return await response.json();
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

  if (models?.available?.length) {
    let formattedOutput = "<h3>MODELS:</h3>";
    let formattedForModelPicker = "";

    models.available.forEach(({ name, model }) => {
      formattedOutput += `<p>Name/Model: ${name}/${model}</p>`;
      formattedForModelPicker += `<option value="${model}">${name}</option>`;
    });

    element.innerHTML = formattedOutput;
    document.getElementById("model-picker").innerHTML = formattedForModelPicker;
  } else {
    element.innerHTML = "<h3>No models found on the server.</h3>";
    document.getElementById("model-picker").innerHTML =
      "<option value=''>Unable to connect to server</option>";
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
                         <p>Host: ${connection.host || "Unknown"}</p>
                         <p>Port: ${connection.port || "Unknown"}</p>
                         <p>Status: ${
                           connection.status || "Unknown"
                         } - CONNECTED</p>`;
  } else {
    element.innerHTML = "<h3>UNABLE TO CONNECT TO SERVER</h3>";
  }
};

// Function to handle loading state
const handleLoadingState = async (func, delay, loadingPage = false) => {
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
  if (inputBoxButton) inputBoxButton.style.display = "none";

  try {
    await func();
  } catch (error) {
    console.error("Error during loading function:", error);
    mainContainer.innerHTML = `<h1>ERROR: ${error.message}</h1>`;
  } finally {
    setTimeout(() => {
      if (inputBox) inputBox.disabled = false;
      if (inputBoxButton) inputBoxButton.style.display = "block";
    }, delay);
  }
};

// Main function to initialize the page
const initializeDataPage = async () => {
  const connectionsInfo = document.getElementById("connectionsInfo");
  const printModel = document.getElementById("print_models");
  const printActiveModel = document.getElementById("print_active_models");

  if (!connectionsInfo || !printModel || !printActiveModel) {
    console.error("One or more required elements not found.");
    return;
  }

  try {
    const connection = await pingServer();
    const models = await fetchModelDetails();

    displayConnectionDetails(connection, connectionsInfo);
    displayModelDetails(models, printModel);

    if (models?.active?.length) {
      let formattedOutput = "<h3>ACTIVE MODELS:</h3>";

      models.active.forEach(({ name, model }) => {
        formattedOutput += `<p>Name/Model: ${name}/${model}</p>`;
      });

      printActiveModel.innerHTML = formattedOutput;
    } else {
      printActiveModel.innerHTML =
        "<h3>Currently No Active Models Present.</h3>";
    }
  } catch (error) {
    console.error("Error initializing page:", error);
    connectionsInfo.innerHTML = "<h3>ERROR LOADING DATA</h3>";
    printModel.innerHTML = "<h3>ERROR LOADING MODELS</h3>";
    printActiveModel.innerHTML = "<h3>ERROR LOADING ACTIVE MODELS</h3>";
  }
};

// Function to send a message to the AI and get a response
const sendMessageToAI = async (prompt, model) => {
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, model }),
    });

    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
};

// Function to print the response from AI
const printResponse = (res, element) => {
  if (!element) {
    console.error("Element for displaying response from AI not found.");
    return;
  }
  element.innerHTML = res?.response?.length
    ? `<div class="response-card"><b>AI :</b> ${res.response}</div>`
    : "<h3>No response received.</h3>";
};

// Function to handle sending a message
const sendMessage = async () => {
  const modelPicker = document.getElementById("model-picker");
  const prompt = document.getElementById("prompt");
  const inputBoxButton = document.getElementById("prompt-btn");

  const cardContainer = document.getElementById("response-container");

  if (!modelPicker || !prompt || !cardContainer) {
    console.error("Missing required elements.");
    return;
  }

  inputBoxButton.style.display = "none";
  cardContainer.style.display = "block";
  cardContainer.innerHTML = "<h3>LOADING...</h3>";

  try {
    const res = await sendMessageToAI(prompt.value, modelPicker.value);
    printResponse(res, cardContainer);
  } catch (error) {
    console.error("Error sending message:", error);
    cardContainer.innerHTML = "<h3>ERROR SENDING MESSAGE</h3>";
  }
  inputBoxButton.style.display = "block";
};

// Initialize the page when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  handleLoadingState(initializeDataPage, 1000);
});
