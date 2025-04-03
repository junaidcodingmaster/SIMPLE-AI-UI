// Utility function for fetching data from a URL
async function fetchData(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return response.json();
  } catch (error) {
    console.error(`Error fetching ${url}:`, error);
    return null;
  }
}

// Server functions
const pingServer = () => fetchData("/api/connection");
const fetchModelDetails = () => fetchData("/api/connection/stats");

// Display functions
function displayConnectionDetails(connection, element) {
  if (!element) return console.error("Missing element for connection details.");
  element.innerHTML = connection
    ? `<h3>CONNECTION INFO:</h3>
       <p>Host: ${connection.host || "Unknown"}</p>
       <p>Port: ${connection.port || "Unknown"}</p>
       <p>Status: ${connection.status || "Unknown"} - CONNECTED</p>`
    : "<h3>UNABLE TO CONNECT TO SERVER</h3>";
}

function displayModelDetails(models, element) {
  if (!element) return console.error("Missing element for model details.");
  const modelPicker = document.getElementById("model-picker");
  if (models?.available?.length) {
    let modelHTML = "<h3>MODELS:</h3>";
    let optionsHTML = "";
    models.available.forEach(({ name, model }) => {
      modelHTML += `<p>Name/Model: ${name}/${model}</p>`;
      optionsHTML += `<option value="${model}">${name}</option>`;
    });
    element.innerHTML = modelHTML;
    if (modelPicker) modelPicker.innerHTML = optionsHTML;
  } else {
    element.innerHTML = "<h3>No models found on the server.</h3>";
    if (modelPicker)
      modelPicker.innerHTML =
        "<option value=''>Unable to connect to server</option>";
  }
}

function displayActiveModels(models, element) {
  if (!element) return console.error("Missing element for active models.");
  if (models?.active?.length) {
    let html = "<h3>ACTIVE MODELS:</h3>";
    models.active.forEach(({ name, model }) => {
      html += `<p>Name/Model: ${name}/${model}</p>`;
    });
    element.innerHTML = html;
  } else {
    element.innerHTML = "<h3>Currently No Active Models Present.</h3>";
  }
}

// Handle UI loading state during async operations
async function handleLoadingState(func, delay, showLoadingPage = false) {
  const inputBox = document.getElementById("prompt");
  const inputButton = document.getElementById("prompt-btn");
  const mainContainer = document.getElementById("main");

  if (!mainContainer) return console.error("Missing main container.");

  if (showLoadingPage) mainContainer.innerHTML = "<h1>LOADING...</h1>";
  if (inputBox) inputBox.disabled = true;
  if (inputButton) inputButton.style.display = "none";

  try {
    await func();
  } catch (error) {
    console.error("Error during loading:", error);
    mainContainer.innerHTML = `<h1>ERROR: ${error.message}</h1>`;
  } finally {
    setTimeout(() => {
      if (inputBox) inputBox.disabled = false;
      if (inputButton) inputButton.style.display = "block";
    }, delay);
  }
}

// Initialize the page by fetching and displaying connection and model details
async function initializeDataPage() {
  const connectionsInfo = document.getElementById("connectionsInfo");
  const printModel = document.getElementById("print_models");
  const printActiveModel = document.getElementById("print_active_models");

  if (!connectionsInfo || !printModel || !printActiveModel)
    return console.error("One or more required elements not found.");

  const connection = await pingServer();
  const models = await fetchModelDetails();

  displayConnectionDetails(connection, connectionsInfo);
  displayModelDetails(models, printModel);
  displayActiveModels(models, printActiveModel);
}

// AI communication functions
async function sendMessageToAI(prompt, model) {
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, model }),
    });
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return response.json();
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
}

function printResponse(res, element) {
  if (!element) return console.error("Missing element for AI response.");
  element.innerHTML = res?.response?.length
    ? `<div class="response-card"><b>AI :</b> ${res.response}</div>`
    : "<h3>No response received.</h3>";
}

async function sendMessage() {
  const modelPicker = document.getElementById("model-picker");
  const prompt = document.getElementById("prompt");
  const inputButton = document.getElementById("prompt-btn");
  const responseContainer = document.getElementById("response-container");

  if (!modelPicker || !prompt || !responseContainer)
    return console.error("Missing required elements for sending message.");

  inputButton.style.display = "none";
  responseContainer.style.display = "block";
  responseContainer.innerHTML = "<h3>LOADING...</h3>";

  try {
    const res = await sendMessageToAI(prompt.value, modelPicker.value);
    printResponse(res, responseContainer);
  } catch (error) {
    console.error("Error sending message:", error);
    responseContainer.innerHTML = "<h3>ERROR SENDING MESSAGE</h3>";
  }
  inputButton.style.display = "block";
}

// Initialize the page when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  handleLoadingState(initializeDataPage, 1000);
});
